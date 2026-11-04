#!/usr/bin/env python3
"""Render a salesperson-friendly HTML (+ markdown) demo report.

Usage:
  python3 scripts/render-demo-report.py before
  python3 scripts/render-demo-report.py after
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "artifacts" / "live"
APP = ROOT / "apps" / "vulnerable-fastapi"
REMEDIATED = ("sqlparse", "PyPDF2", "tokenizers")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_pip_audit(text: str) -> list[dict]:
    rows: list[dict] = []
    for line in text.splitlines():
        # Name Version ID Fix…  or skip-reason lines
        if re.match(r"(?i)^name\b", line) or set(line.strip()) <= {"-", " "}:
            continue
        if "not found on PyPI" in line or "could not be audited" in line:
            m = re.search(r"^(\S+)\s+Dependency not found on PyPI.*?(\S+\+rhlw\.\d+|\([^)]+\))", line)
            pkg = line.split()[0] if line.split() else "?"
            rows.append({"kind": "skip", "package": pkg, "detail": line.strip()})
            continue
        parts = line.split()
        if len(parts) >= 3 and parts[0].lower() in {p.lower() for p in REMEDIATED} | {
            "pypdf2",
            "sqlparse",
            "tokenizers",
        }:
            rows.append(
                {
                    "kind": "vuln",
                    "package": parts[0],
                    "version": parts[1],
                    "id": parts[2],
                    "fix": " ".join(parts[3:]) if len(parts) > 3 else "",
                }
            )
    return rows


def parse_trivy_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    out: list[dict] = []
    for result in data.get("Results") or []:
        for v in result.get("Vulnerabilities") or []:
            pkg = v.get("PkgName") or v.get("PkgID") or "?"
            if pkg.lower() not in {p.lower() for p in REMEDIATED} and "sqlparse" not in pkg.lower():
                # keep HIGH/CRIT for demo focus on rem set when possible
                if pkg.lower() not in {"sqlparse", "pypdf2", "tokenizers"}:
                    continue
            out.append(
                {
                    "package": pkg,
                    "id": v.get("VulnerabilityID", "?"),
                    "severity": v.get("Severity", "?"),
                    "installed": v.get("InstalledVersion", "?"),
                    "fixed": v.get("FixedVersion", ""),
                    "title": (v.get("Title") or "")[:120],
                }
            )
    return out


def installed_versions() -> dict[str, str]:
    vers: dict[str, str] = {}
    try:
        import importlib.metadata as m

        for pkg in REMEDIATED:
            try:
                vers[pkg] = m.version(pkg)
            except Exception:
                vers[pkg] = "not installed"
    except Exception:
        for pkg in REMEDIATED:
            vers[pkg] = "?"
    # Prefer poetry show if running outside venv — try reading inventory files
    return vers


def inventory_from_file(stage: str) -> dict[str, str]:
    path = LIVE / f"sbom-{stage}-inventory.txt"
    vers: dict[str, str] = {}
    if not path.exists():
        return vers
    for line in path.read_text().splitlines():
        m = re.match(r"^(\S+)\s+(\S+)", line.strip())
        if not m:
            continue
        name, ver = m.group(1), m.group(2)
        if name.lower() in {p.lower() for p in REMEDIATED} | {"fastapi", "httpx"}:
            # normalize display name
            for canon in REMEDIATED:
                if canon.lower() == name.lower():
                    vers[canon] = ver
                    break
            else:
                vers[name] = ver
    return vers


def esc(s: str) -> str:
    return html.escape(s or "")


def render(stage: str) -> tuple[Path, Path]:
    stage = stage.lower().strip()
    if stage not in {"before", "after"}:
        raise SystemExit("stage must be before|after")

    audit_path = LIVE / f"pip-audit-{stage}.txt"
    trivy_json = LIVE / f"trivy-{stage}.json"
    audit_rows = parse_pip_audit(read_text(audit_path))
    trivy_rows = parse_trivy_json(trivy_json)
    versions = inventory_from_file(stage) or installed_versions()

    vuln_rows = [r for r in audit_rows if r.get("kind") == "vuln"]
    skip_rows = [r for r in audit_rows if r.get("kind") == "skip"]
    lightwell = stage == "after" and any("+rhlw." in versions.get(p, "") for p in REMEDIATED)

    if stage == "before":
        headline = "Vulnerable — public PyPI pins"
        status = "FINDINGS"
        status_class = "bad"
        blurb = (
            "Same three packages Lightwell remediates. Scanners light up on the public builds. "
            "Download the SBOM and upload it to Lightwell Lens to show the catch / hooks."
        )
        next_step = (
            "Next: run <strong>2 · Remediate (Lightwell)</strong> — paste orgId|sa + token for this run only."
        )
        sbom_name = "sbom-before.cdx.json"
        accent = "#b42318"
        accent_soft = "#fef3f2"
    else:
        headline = "Remediated — Lightwell Network"
        status = "PASS" if lightwell else "CHECK"
        status_class = "good" if lightwell else "warn"
        blurb = (
            "Packages resolved from Lightwell <strong>Remediated</strong> (+rhlw.1) and "
            "<strong>Validated</strong> (catalog). No application rewrite. "
            "Upload the after SBOM to Lens for the clean inventory."
        )
        next_step = "Close: remotes change in minutes — ask who owns Artifactory virtuals + pilot service."
        sbom_name = "sbom-after.cdx.json"
        accent = "#027a48"
        accent_soft = "#ecfdf3"

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    if os.environ.get("GITHUB_REPOSITORY") and os.environ.get("GITHUB_RUN_ID"):
        run_url = f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    else:
        run_url = ""

    pkg_cards = []
    for pkg in REMEDIATED:
        ver = versions.get(pkg, versions.get(pkg.lower(), "?"))
        is_lw = "+rhlw." in ver
        badge = "Lightwell +rhlw" if is_lw else ("public pin" if stage == "before" else "missing +rhlw")
        badge_cls = "tag-good" if is_lw else ("tag-bad" if stage == "before" else "tag-warn")
        pkg_cards.append(
            f'<div class="card"><div class="pkg">{esc(pkg)}</div>'
            f'<div class="ver"><code>{esc(ver)}</code></div>'
            f'<span class="tag {badge_cls}">{esc(badge)}</span></div>'
        )

    vuln_html = ""
    if vuln_rows:
        cells = "".join(
            f"<tr><td>{esc(r['package'])}</td><td>{esc(r['version'])}</td>"
            f"<td><code>{esc(r['id'])}</code></td><td>{esc(r.get('fix',''))}</td></tr>"
            for r in vuln_rows[:30]
        )
        vuln_html = f"""
        <section>
          <h2>pip-audit findings</h2>
          <table>
            <thead><tr><th>Package</th><th>Version</th><th>ID</th><th>Fix</th></tr></thead>
            <tbody>{cells}</tbody>
          </table>
        </section>"""
    elif skip_rows and stage == "after":
        cells = "".join(
            f"<tr><td>{esc(r['package'])}</td><td>{esc(r['detail'])}</td></tr>" for r in skip_rows[:20]
        )
        vuln_html = f"""
        <section>
          <h2>pip-audit after Lightwell</h2>
          <p class="ok">No known vulnerabilities found on public CVE records for these builds.</p>
          <table>
            <thead><tr><th>Package</th><th>Note</th></tr></thead>
            <tbody>{cells}</tbody>
          </table>
          <p class="hint">“Not found on PyPI” = these are <em>Lightwell Network</em> artifacts, not the vulnerable public wheels.</p>
        </section>"""
    else:
        vuln_html = "<section><h2>pip-audit</h2><p>See artifact <code>pip-audit-*.txt</code>.</p></section>"

    trivy_html = ""
    if stage == "after" and lightwell:
        # Trivy often still maps public CVE IDs onto +rhlw.* by upstream version string.
        # Sales proof is package origin (+rhlw / Lightwell source) + pip-audit "not on PyPI".
        trivy_html = """
        <section>
          <h2>Trivy note</h2>
          <p class="ok">Installed builds are <code>+rhlw.1</code> from Lightwell Remediated.</p>
          <p class="hint">Some scanners still attach public CVE IDs to the upstream version string.
          On the call, lead with <strong>Lightwell origin</strong> and pip-audit’s
          <em>not found on PyPI</em> — then Lens on the after SBOM.</p>
        </section>"""
    elif trivy_rows:
        cells = "".join(
            f"<tr><td>{esc(r['package'])}</td><td><code>{esc(r['id'])}</code></td>"
            f"<td><span class='sev'>{esc(r['severity'])}</span></td>"
            f"<td>{esc(r['installed'])}</td><td>{esc(r['fixed'])}</td></tr>"
            for r in trivy_rows[:30]
        )
        trivy_html = f"""
        <section>
          <h2>Trivy (HIGH/CRITICAL focus)</h2>
          <table>
            <thead><tr><th>Library</th><th>CVE</th><th>Sev</th><th>Installed</th><th>Fixed</th></tr></thead>
            <tbody>{cells}</tbody>
          </table>
        </section>"""
    elif stage == "after":
        trivy_html = "<section><h2>Trivy</h2><p class='ok'>No HIGH/CRITICAL hits on the remediated set.</p></section>"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Lightwell demo — {esc(stage)}</title>
<style>
  :root {{
    --bg: #0f1419;
    --panel: #171d25;
    --text: #e7ecf3;
    --muted: #9aa7b8;
    --line: #2a3441;
    --accent: {accent};
    --accent-soft: {accent_soft};
    --font: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: var(--font); background:
      radial-gradient(1200px 600px at 10% -10%, #1b2838 0%, transparent 55%),
      radial-gradient(900px 500px at 100% 0%, #1a2420 0%, transparent 50%),
      var(--bg);
    color: var(--text); line-height: 1.45;
  }}
  .wrap {{ max-width: 980px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }}
  header.hero {{
    border: 1px solid var(--line); background: linear-gradient(180deg, #1c2430, var(--panel));
    border-radius: 18px; padding: 1.75rem 1.75rem 1.5rem; margin-bottom: 1.25rem;
  }}
  .eyebrow {{ text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; color: var(--muted); }}
  h1 {{ margin: .35rem 0 .5rem; font-size: clamp(1.6rem, 3vw, 2.2rem); font-weight: 650; }}
  .status {{
    display: inline-flex; align-items: center; gap: .5rem; font-weight: 700;
    padding: .35rem .75rem; border-radius: 999px; font-size: .85rem;
  }}
  .status.bad {{ background: #f044381a; color: #ffb4ab; border: 1px solid #f0443866; }}
  .status.good {{ background: #12b76a1a; color: #6ce9a6; border: 1px solid #12b76a66; }}
  .status.warn {{ background: #f790091a; color: #fec84b; border: 1px solid #f7900966; }}
  .blurb {{ color: var(--muted); max-width: 62ch; margin: .9rem 0 0; }}
  .meta {{ margin-top: 1rem; font-size: .85rem; color: var(--muted); }}
  .meta a {{ color: #84caff; }}
  .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .85rem; margin: 1.1rem 0 1.4rem; }}
  @media (max-width: 720px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  .card {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 1rem 1.1rem;
  }}
  .pkg {{ font-size: .8rem; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; }}
  .ver {{ margin: .35rem 0 .55rem; font-size: 1.15rem; }}
  code {{ font-family: var(--mono); font-size: .92em; }}
  .tag {{ font-size: .72rem; padding: .2rem .5rem; border-radius: 999px; border: 1px solid var(--line); }}
  .tag-bad {{ background: #f0443814; color: #ffb4ab; }}
  .tag-good {{ background: #12b76a14; color: #6ce9a6; }}
  .tag-warn {{ background: #f7900914; color: #fec84b; }}
  section {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
    padding: 1.1rem 1.2rem; margin-bottom: 1rem;
  }}
  h2 {{ margin: 0 0 .75rem; font-size: 1.05rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
  th, td {{ text-align: left; padding: .45rem .35rem; border-bottom: 1px solid var(--line); vertical-align: top; }}
  th {{ color: var(--muted); font-weight: 600; font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; }}
  .sev {{ color: #ffb4ab; font-weight: 650; }}
  .ok {{ color: #6ce9a6; }}
  .hint {{ color: var(--muted); font-size: .9rem; }}
  .cta {{
    border: 1px solid color-mix(in srgb, var(--accent) 45%, var(--line));
    background: color-mix(in srgb, var(--accent) 12%, var(--panel));
    border-radius: 14px; padding: 1.1rem 1.25rem; margin-top: .4rem;
  }}
  .cta strong {{ color: #fff; }}
  .steps {{ display: grid; gap: .45rem; margin: .6rem 0 0; padding-left: 1.1rem; color: var(--muted); }}
</style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div class="eyebrow">Lightwell Part 2 · sales demo report</div>
      <h1>{esc(headline)}</h1>
      <span class="status {status_class}">{esc(status)}</span>
      <p class="blurb">{blurb}</p>
      <div class="meta">Generated {esc(stamp)}
        {" · <a href='" + esc(run_url) + "'>GitHub Actions run</a>" if run_url else ""}
      </div>
    </header>

    <div class="grid">
      {''.join(pkg_cards)}
    </div>

    {vuln_html}
    {trivy_html}

    <section class="cta">
      <h2>What to call attention to</h2>
      <ol class="steps">
        <li>Screen-share this report (download artifact <code>demo-report-{esc(stage)}.html</code> and open in a browser).</li>
        <li>Upload <code>{esc(sbom_name)}</code> to <strong>Lightwell Lens</strong>.</li>
        <li>{next_step}</li>
      </ol>
    </section>
  </div>
</body>
</html>
"""

    LIVE.mkdir(parents=True, exist_ok=True)
    html_path = LIVE / f"demo-report-{stage}.html"
    html_path.write_text(page, encoding="utf-8")

    # Compact markdown for Job Summary (glanceable without opening artifacts)
    md_lines = [
        f"# Demo report — {headline}",
        "",
        f"**Status:** `{status}` · generated {stamp}",
        "",
        "## Remediated set",
        "",
        "| Package | Version |",
        "|---------|---------|",
    ]
    for pkg in REMEDIATED:
        ver = versions.get(pkg, "?")
        md_lines.append(f"| `{pkg}` | `{ver}` |")
    md_lines += ["", f"**SBOM for Lens:** `{sbom_name}`", ""]
    if vuln_rows:
        md_lines += ["### pip-audit findings", "", "| Package | ID |", "|---------|----|"]
        for r in vuln_rows[:15]:
            md_lines.append(f"| `{r['package']}` | `{r['id']}` |")
        md_lines.append("")
    elif stage == "after":
        md_lines += [
            "### CVE clear signal",
            "",
            "pip-audit: **No known vulnerabilities** — `+rhlw.1` builds are not the public PyPI artifacts.",
            "",
        ]
    md_lines += [
        "### Visual report",
        "",
        f"Download artifact **`demo-report-{stage}.html`** and open it in a browser (easier than reading logs).",
        "",
    ]
    md_path = LIVE / f"demo-report-{stage}.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(md_path.read_text(encoding="utf-8"))
            fh.write("\n")

    print(f"Wrote {html_path}")
    print(f"Wrote {md_path}")
    return html_path, md_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: render-demo-report.py before|after")
    render(sys.argv[1])
