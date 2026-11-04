#!/usr/bin/env python3
"""Normalize a CycloneDX JSON SBOM for Lightwell Lens upload.

Lens requires a Package URL (purl) on each component. Trivy/Syft directory
scans often emit junk entries (poetry.lock, filesystem path metadata) with
no purl — those show up as “packages skipped” in Lens.

Usage:
  python3 scripts/sbom-lens-normalize.py path/to/file.cdx.json
  python3 scripts/sbom-lens-normalize.py in.cdx.json -o out.cdx.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def app_meta_from_pyproject(app_dir: Path) -> dict:
    name, version = "vulnerable-fastapi", "0.1.0"
    pyproject = app_dir / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        m = re.search(r'(?m)^name\s*=\s*"([^"]+)"', text)
        if m:
            name = m.group(1)
        m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
        if m:
            version = m.group(1)
    purl = f"pkg:pypi/{name}@{version}"
    return {
        "type": "application",
        "name": name,
        "version": version,
        "bom-ref": purl,
        "purl": purl,
    }


def normalize(data: dict, app_dir: Path | None = None) -> tuple[dict, dict]:
    before_n = len(data.get("components") or [])
    kept = []
    dropped = []
    for c in data.get("components") or []:
        purl = c.get("purl")
        ctype = c.get("type") or ""
        name = c.get("name") or ""
        # Lens: every identifiable package needs a purl. Drop lockfile / path junk.
        if not purl:
            dropped.append({"name": name, "type": ctype, "reason": "missing purl"})
            continue
        if ctype == "application" and name.endswith(".lock"):
            dropped.append({"name": name, "type": ctype, "reason": "lockfile application"})
            continue
        kept.append(c)

    data["components"] = kept

    # Fix metadata.component (Trivy sets it to a filesystem path with no purl).
    meta = data.setdefault("metadata", {})
    root = app_meta_from_pyproject(app_dir) if app_dir else {
        "type": "application",
        "name": "vulnerable-fastapi",
        "version": "0.1.0",
        "purl": "pkg:pypi/vulnerable-fastapi@0.1.0",
        "bom-ref": "pkg:pypi/vulnerable-fastapi@0.1.0",
    }
    meta["component"] = root

    # Drop dependency edges that reference removed bom-refs.
    valid_refs = {c.get("bom-ref") for c in kept if c.get("bom-ref")}
    valid_refs.add(root.get("bom-ref"))
    deps_in = data.get("dependencies") or []
    deps_out = []
    for d in deps_in:
        ref = d.get("ref")
        if ref and ref not in valid_refs and not str(ref).startswith("pkg:"):
            # keep only if still present
            continue
        depends = [x for x in (d.get("dependsOn") or []) if x in valid_refs]
        if ref in valid_refs:
            deps_out.append({"ref": ref, "dependsOn": depends} if depends else {"ref": ref})
    data["dependencies"] = deps_out

    stats = {
        "components_before": before_n,
        "components_after": len(kept),
        "dropped": dropped,
    }
    return data, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", help="defaults to in-place")
    ap.add_argument("--app-dir", default="", help="path to app (for metadata name/version)")
    args = ap.parse_args()
    path = Path(args.input)
    data = json.loads(path.read_text(encoding="utf-8"))
    app_dir = Path(args.app_dir) if args.app_dir else path.resolve().parents[2] / "apps" / "vulnerable-fastapi"
    if not app_dir.is_dir():
        app_dir = None
    data, stats = normalize(data, app_dir)
    out = Path(args.output) if args.output else path
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        f"Lens-normalized {path.name}: {stats['components_before']} → {stats['components_after']} components"
    )
    for d in stats["dropped"]:
        print(f"  dropped: {d['type']} {d['name']!r} ({d['reason']})")


if __name__ == "__main__":
    main()
