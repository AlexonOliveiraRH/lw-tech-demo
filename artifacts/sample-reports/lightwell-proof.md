# Lightwell demo proof (sample)

## Remediated set — installed versions

| Package | Installed version | Expected |
|---------|-------------------|----------|
| `sqlparse` | `0.5.5+rhlw.1` | OK — Lightwell remediated |
| `PyPDF2` | `3.0.1+rhlw.1` | OK — Lightwell remediated |
| `tokenizers` | `0.23.1+rhlw.1` | OK — Lightwell remediated |

## After (pip-audit)

**CVE records cleared for the Lightwell builds:** pip-audit reports the `+rhlw.1` packages as *not found on public PyPI*.

```
pypdf2     Dependency not found on PyPI and could not be audited: pypdf2 (3.0.1+rhlw.1)
sqlparse   Dependency not found on PyPI and could not be audited: sqlparse (0.5.5+rhlw.1)
tokenizers Dependency not found on PyPI and could not be audited: tokenizers (0.23.1+rhlw.1)
```

**Remediated** feed → those three. **Validated** feed → FastAPI and the rest of the catalog.
