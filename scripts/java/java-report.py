#!/usr/bin/env python3
"""Lightwell Java demo: provenance check + HTML/markdown report.

Reads what scripts/java/scan.sh produced for one stage:
  - target/deps-<stage>.txt     (mvn dependency:list, absolute paths)
  - <maven local repo>/.../_remote.repositories (which repository served each jar)
  - artifacts/live/trivy-<stage>.json

Writes into artifacts/live/:
  - demo-report-<stage>.html / .md
  - sbom-<stage>-inventory.txt
  - scan-before-summary.md (before) or lightwell-proof.md (after)

Exit code 1 on the after stage when a package of the remediated set is not a
Lightwell rhlw build served by the Java Remediated feed.

Usage:
  python3 scripts/java/java-report.py before|after
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps" / "vulnerable-spring"
LIVE = ROOT / "artifacts" / "live"
NS = {"m": "http://maven.apache.org/POM/4.0.0"}
LENS_URL = "https://console.redhat.com/lightwell/lens"

SOURCE_LABEL = {
    "lightwell-remediated": "Lightwell Java Remediated",
    "lightwell-validated": "Lightwell Java Validated",
    "central": "Maven Central (public)",
}


def remediated_set() -> list[str]:
    """groupId:artifactId whose version the `lightwell` profile swaps for an rhlw build."""
    pom = ET.parse(APP / "pom.xml").getroot()
    swapped: set[str] = set()
    for profile in pom.findall("m:profiles/m:profile", NS):
        if profile.findtext("m:id", namespaces=NS) != "lightwell":
            continue
        props = profile.find("m:properties", NS)
        for prop in props if props is not None else []:
            if "rhlw" in (prop.text or ""):
                swapped.add(prop.tag.split("}", 1)[1])
    found: list[str] = []
    for dep in pom.iter("{%s}dependency" % NS["m"]):
        ver = dep.findtext("m:version", default="", namespaces=NS)
        m = re.fullmatch(r"\$\{([^}]+)\}", ver.strip())
        if m and m.group(1) in swapped:
            ga = f"{dep.findtext('m:groupId', namespaces=NS)}:{dep.findtext('m:artifactId', namespaces=NS)}"
            if ga not in found:
                found.append(ga)
    return found


def resolved_dependencies(stage: str) -> list[dict]:
    """Parse `mvn dependency:list -DoutputAbsoluteArtifactFilename=true` output."""
    path = APP / "target" / f"deps-{stage}.txt"
    deps: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        # group:artifact:type[:classifier]:version:scope:/abs/path.jar [-- module ...]
        m = re.match(r"^([^:\s]+):([^:\s]+):jar(?::[^:\s]+)?:([^:\s]+):(compile|runtime):(\S+\.jar)", line)
        if not m:
            continue
        group, artifact, version, _scope, jar = m.groups()
        deps.append(
            {
                "ga": f"{group}:{artifact}",
                "artifact": artifact,
                "version": version,
                "jar": jar,
                "source": jar_source(Path(jar)),
            }
        )
    return sorted(deps, key=lambda d: d["ga"])


def jar_source(jar: Path) -> str:
    """Repository id recorded by Maven in _remote.repositories next to the jar."""
    marker = jar.parent / "_remote.repositories"
    if not marker.exists():
        return "unknown"
    repos = [
        line.split(">", 1)[1].rstrip("=")
        for line in marker.read_text(encoding="utf-8").splitlines()
        if line.startswith(jar.name + ">")
    ]
    for preferred in ("lightwell-remediated", "lightwell-validated", "central"):
        if preferred in repos:
            return preferred
    return repos[0] if repos else "unknown"


def trivy_findings(stage: str) -> list[dict] | None:
    """Findings, or None when Trivy did not produce a usable report."""
    path = LIVE / f"trivy-{stage}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    rows = []
    for result in data.get("Results") or []:
        for v in result.get("Vulnerabilities") or []:
            rows.append(
                {
                    "ga": v.get("PkgName", "?"),
                    "installed": v.get("InstalledVersion", "?"),
                    "id": v.get("VulnerabilityID", "?"),
                    "severity": v.get("Severity", "?"),
                    "fixed": v.get("FixedVersion", ""),
                }
            )
    return rows


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def render(stage: str) -> int:
    deps = resolved_dependencies(stage)
    rem = remediated_set()
    by_ga = {d["ga"]: d for d in deps}
    findings = trivy_findings(stage)
    trivy_ok = findings is not None
    findings = findings or []
    if not trivy_ok:
        print(f"::warning::Trivy did not produce trivy-{stage}.json (install or vulnerability DB download failed)")
    sources = Counter(d["source"] for d in deps)

    problems = []
    if stage == "after":
        for ga in rem:
            d = by_ga.get(ga)
            if d is None:
                problems.append(f"{ga} not resolved")
            elif "rhlw" not in d["version"] or d["source"] != "lightwell-remediated":
                problems.append(f"{ga} {d['version']} from {d['source']}")
    ok = not problems

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run_url = ""
    if os.environ.get("GITHUB_REPOSITORY") and os.environ.get("GITHUB_RUN_ID"):
        run_url = (
            f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
            f"{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
        )

    if stage == "before":
        headline = "Vulnerable - public Maven Central"
        status, status_class = "FINDINGS", "bad"
        blurb = (
            f"The app pins {len(rem)} libraries Lightwell remediates at their public versions. "
            "Scanners light up on these builds. Upload the before SBOM to Lightwell Lens to see "
            "which CVEs have a Lightwell fix available."
        )
        next_step = "Next: run <strong>J2 · Java Remediate (Lightwell)</strong> with your service account."
    else:
        headline = "Remediated - Lightwell Network"
        status, status_class = ("PASS", "good") if ok else ("CHECK", "warn")
        blurb = (
            "Same code, same tests. Maven resolved the remediated set from Lightwell "
            "<strong>Java Remediated</strong> (<code>rhlw</code> builds) and the rest from "
            "<strong>Java Validated</strong> where available. Upload the after SBOM to Lens and "
            "compare it with the before SBOM."
        )
        next_step = "Compare the before and after SBOMs in Lightwell Lens."

    # --- remediated set table ---
    rem_rows = []
    for ga in rem:
        d = by_ga.get(ga, {"version": "not resolved", "source": "unknown"})
        is_lw = "rhlw" in d["version"]
        tag = ("tag-good", "Lightwell rhlw") if is_lw else (
            ("tag-bad", "public") if stage == "before" else ("tag-warn", "missing rhlw"))
        rem_rows.append(
            f"<tr><td>{esc(ga.split(':')[1])}</td><td><code>{esc(d['version'])}</code></td>"
            f"<td>{esc(SOURCE_LABEL.get(d['source'], d['source']))}</td>"
            f"<td><span class='tag {tag[0]}'>{esc(tag[1])}</span></td></tr>"
        )

    # --- other dependencies table ---
    other_rows = "".join(
        f"<tr><td>{esc(d['artifact'])}</td><td><code>{esc(d['version'])}</code></td>"
        f"<td>{esc(SOURCE_LABEL.get(d['source'], d['source']))}</td></tr>"
        for d in deps
        if d["ga"] not in rem
    )

    # --- scanner section ---
    sev = Counter(f["severity"] for f in findings)
    sev_txt = ", ".join(f"{sev[s]} {s}" for s in ("CRITICAL", "HIGH") if sev.get(s)) or "none"
    if not trivy_ok:
        sev_txt = "not available (Trivy did not run - see the job log)"
    if stage == "before":
        rem_findings = [f for f in findings if f["ga"] in rem]
        cells = "".join(
            f"<tr><td>{esc(f['ga'].split(':')[-1])}</td><td><code>{esc(f['id'])}</code></td>"
            f"<td><span class='sev'>{esc(f['severity'])}</span></td><td>{esc(f['installed'])}</td>"
            f"<td>{esc(f['fixed'])}</td></tr>"
            for f in sorted(rem_findings, key=lambda f: (f["severity"] != "CRITICAL", f["ga"], f["id"]))
        )
        scanner_html = f"""
        <section>
          <h2>Trivy on the remediated set (HIGH/CRITICAL)</h2>
          <p class="hint">Whole app: {esc(sev_txt)}. Rows below: the {len(rem)} libraries Lightwell remediates.</p>
          <table><thead><tr><th>Library</th><th>CVE</th><th>Sev</th><th>Installed</th><th>Fixed upstream in</th></tr></thead>
          <tbody>{cells}</tbody></table>
        </section>"""
    else:
        trivy_line = f"Trivy still reports {sev_txt} findings." if trivy_ok else f"Trivy result: {sev_txt}."
        scanner_html = f"""
        <section>
          <h2>Scanner note</h2>
          <p>{esc(trivy_line)} Version-matching scanners compare the
          upstream version string (for example <code>1.4.18</code> inside <code>1.4.18.rhlw-00006</code>)
          against public advisories, so they cannot tell that Lightwell backported the fix.</p>
          <p class="hint">Use <strong>Lightwell Lens</strong> on the before and after SBOMs to see
          the CVEs Lightwell fixes. Full Trivy output: <code>trivy-after.txt</code>.</p>
        </section>"""

    src_summary = " · ".join(f"{n} from {SOURCE_LABEL.get(s, s)}" for s, n in sources.most_common())
    problems_html = (
        "<section><h2>Check failed</h2><ul>" + "".join(f"<li>{esc(p)}</li>" for p in problems) + "</ul></section>"
        if problems else ""
    )
    sbom_name = f"sbom-{stage}.cdx.json"
    accent = "#b42318" if stage == "before" else "#027a48"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Lightwell Java Demo - {esc(stage)}</title>
<style>
  :root {{ --bg:#0f1419; --panel:#171d25; --text:#e7ecf3; --muted:#9aa7b8; --line:#2a3441; --accent:{accent};
    --font:"IBM Plex Sans","Segoe UI",system-ui,sans-serif; --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:var(--font); background:radial-gradient(1200px 600px at 10% -10%,#1b2838 0%,transparent 55%),var(--bg); color:var(--text); line-height:1.45; }}
  .wrap {{ max-width:980px; margin:0 auto; padding:2rem 1.25rem 3rem; }}
  header.hero {{ border:1px solid var(--line); background:linear-gradient(180deg,#1c2430,var(--panel)); border-radius:18px; padding:1.75rem; margin-bottom:1.25rem; }}
  .eyebrow {{ text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; color:var(--muted); }}
  h1 {{ margin:.35rem 0 .5rem; font-size:clamp(1.6rem,3vw,2.2rem); font-weight:650; }}
  .status {{ display:inline-flex; font-weight:700; padding:.35rem .75rem; border-radius:999px; font-size:.85rem; }}
  .status.bad {{ background:#f044381a; color:#ffb4ab; border:1px solid #f0443866; }}
  .status.good {{ background:#12b76a1a; color:#6ce9a6; border:1px solid #12b76a66; }}
  .status.warn {{ background:#f790091a; color:#fec84b; border:1px solid #f7900966; }}
  .blurb {{ color:var(--muted); max-width:66ch; margin:.9rem 0 0; }}
  .meta {{ margin-top:1rem; font-size:.85rem; color:var(--muted); }}
  .meta a {{ color:#84caff; }}
  section {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.2rem; margin-bottom:1rem; }}
  h2 {{ margin:0 0 .75rem; font-size:1.05rem; }}
  table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
  th, td {{ text-align:left; padding:.45rem .35rem; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ color:var(--muted); font-weight:600; font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; }}
  code {{ font-family:var(--mono); font-size:.92em; }}
  .tag {{ font-size:.72rem; padding:.2rem .5rem; border-radius:999px; border:1px solid var(--line); white-space:nowrap; }}
  .tag-bad {{ background:#f0443814; color:#ffb4ab; }} .tag-good {{ background:#12b76a14; color:#6ce9a6; }} .tag-warn {{ background:#f7900914; color:#fec84b; }}
  .sev {{ color:#ffb4ab; font-weight:650; }} .hint {{ color:var(--muted); font-size:.9rem; }}
  .cta {{ border:1px solid color-mix(in srgb,var(--accent) 45%,var(--line)); background:color-mix(in srgb,var(--accent) 12%,var(--panel)); }}
  .steps {{ display:grid; gap:.45rem; margin:.6rem 0 0; padding-left:1.1rem; color:var(--muted); }}
  details summary {{ cursor:pointer; color:var(--muted); }}
</style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div class="eyebrow">Lightwell Java Demo Report · Acme Orders (Spring)</div>
      <h1>{esc(headline)}</h1>
      <span class="status {status_class}">{esc(status)}</span>
      <p class="blurb">{blurb}</p>
      <div class="meta">Generated {esc(stamp)}{" · <a href='" + esc(run_url) + "'>GitHub Actions run</a>" if run_url else ""}
        <br/>Resolved runtime jars: {len(deps)} · {esc(src_summary)}</div>
    </header>
    {problems_html}
    <section>
      <h2>Remediated set ({len(rem)} libraries)</h2>
      <table><thead><tr><th>Library</th><th>Version</th><th>Served by</th><th></th></tr></thead>
      <tbody>{''.join(rem_rows)}</tbody></table>
    </section>
    {scanner_html}
    <section>
      <details><summary>Other runtime dependencies ({len(deps) - len([d for d in deps if d['ga'] in rem])})</summary>
      <table><thead><tr><th>Library</th><th>Version</th><th>Served by</th></tr></thead><tbody>{other_rows}</tbody></table>
      </details>
    </section>
    <section class="cta">
      <h2>Observation points</h2>
      <ol class="steps">
        <li>Upload <code>{esc(sbom_name)}</code> to <a href="{LENS_URL}" style="color:#84caff">Lightwell Lens</a>.</li>
        <li>{next_step}</li>
      </ol>
    </section>
  </div>
</body>
</html>
"""
    LIVE.mkdir(parents=True, exist_ok=True)
    (LIVE / f"demo-report-{stage}.html").write_text(page, encoding="utf-8")

    # --- markdown for the Job Summary ---
    md = [
        f"# Lightwell Java Demo Report - {headline}",
        "",
        f"**Status:** `{status}` · generated {stamp}",
        "",
        f"## Remediated set ({len(rem)} libraries)",
        "",
        "| Library | Version | Served by |",
        "|---------|---------|-----------|",
    ]
    for ga in rem:
        d = by_ga.get(ga, {"version": "not resolved", "source": "unknown"})
        md.append(f"| `{ga.split(':')[1]}` | `{d['version']}` | {SOURCE_LABEL.get(d['source'], d['source'])} |")
    md += ["", f"Runtime jars: **{len(deps)}** · {src_summary}", ""]
    if stage == "before":
        md += [f"Trivy (whole app, HIGH/CRITICAL): {sev_txt}.", ""]
    else:
        md += [
            (f"Trivy still reports {sev_txt}: it matches the upstream version inside `rhlw` builds. "
             if trivy_ok else f"Trivy result: {sev_txt}. ")
            +
            "Compare the before and after SBOMs in Lightwell Lens.",
            "",
        ]
    if problems:
        md += ["### Check failed", ""] + [f"- {p}" for p in problems] + [""]
    md += [f"**SBOM for Lens:** `{sbom_name}`", ""]
    (LIVE / f"demo-report-{stage}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # --- inventory (bundle extra) ---
    inv = [f"Stage: {stage}", "", f"{'artifact':<28} {'version':<24} source", "-" * 80]
    inv += [f"{d['artifact']:<28} {d['version']:<24} {d['source']}" for d in deps]
    (LIVE / f"sbom-{stage}-inventory.txt").write_text("\n".join(inv) + "\n", encoding="utf-8")

    # --- stage summary file expected by stage-artifact-bundle.sh ---
    if stage == "before":
        summary = [
            "# Scan BEFORE - public Maven Central (vulnerable)",
            "",
            f"The app pins the Lightwell Java Remediated set at **public** versions ({len(rem)} libraries).",
            f"Trivy (HIGH/CRITICAL, whole app): {sev_txt}.",
            "",
            "Download `sbom-before.cdx.json` from this run and upload it to Lightwell Lens.",
            "",
            "Next: run **J2 · Java Remediate (Lightwell)**, then upload the after SBOM.",
        ]
        (LIVE / "scan-before-summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    else:
        verdict = (
            f"**PASS** - all {len(rem)} libraries of the remediated set are `rhlw` builds from Lightwell Java Remediated."
            if ok else "**FAIL** - " + "; ".join(problems)
        )
        proof = [
            "# Lightwell Java Demo - proof",
            "",
            f"Generated: {stamp}",
            "",
            "1. Same application code and tests as the before run.",
            "2. Maven resolved the remediated set from **Lightwell Java Remediated** (`rhlw`).",
            "3. Other dependencies came from **Lightwell Java Validated** when available, otherwise Maven Central.",
            "",
            f"Runtime jars: {len(deps)} · {src_summary}",
            "",
            "## Pass/fail",
            "",
            verdict,
        ]
        (LIVE / "lightwell-proof.md").write_text("\n".join(proof) + "\n", encoding="utf-8")

    print(f"Wrote demo-report-{stage}.html/.md, sbom-{stage}-inventory.txt")
    for p in problems:
        print(f"::error::{p}")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"before", "after"}:
        raise SystemExit("usage: java-report.py before|after")
    sys.exit(render(sys.argv[1]))
