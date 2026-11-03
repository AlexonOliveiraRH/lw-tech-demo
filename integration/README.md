# Integration snippets

| Path | Audience | Purpose |
|------|----------|---------|
| [artifactory/](artifactory/) | Artifactory Admin | Compose + **both** Python remotes (remediated + validated) → virtual |
| [nexus/](nexus/) | Optional | Nexus compose; Console notes mTLS — prefer Artifactory for working resolve |
| [poetry/](poetry/) | Developers (primary live path) | validated primary + remediated explicit (or Artifactory virtual) |
| [pipenv/](pipenv/) | Pipenv teams | index redirect sample |
| [pip/](pip/) | pip / CI images | `pip.conf` / Console snippet |

Feeds: [docs/lightwell-feeds.md](../docs/lightwell-feeds.md) (four Console repos; two Python in this kit).

Live demo shows **Poetry** end-to-end; mention Pipenv and pip as drop-in equivalents.
