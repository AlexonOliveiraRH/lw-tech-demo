# Sample scanner reports (demo backup)

| File | Use |
|------|-----|
| `trivy-before.txt` / `.json` | Public PyPI `sqlparse==0.5.5` — HIGH CVEs |
| `trivy-after.txt` | After Lightwell Remediated `0.5.5+rhlw.1` — version column shows `+rhlw.1`; CVE IDs may remain until Lens VEX |

Honest demo beat: binary/provenance change first, Lens VEX for scanner-noise elimination.
