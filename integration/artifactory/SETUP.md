# Artifactory sandbox — two Lightwell Python remotes → one virtual

Rehearsal path for **segment 2**. Console shows **four** repos (Python Remediated, Python Validated, Java Remediated, Java); this demo wires the **two Python** remotes.

## Start

Compose runs **Artifactory OSS 7.x + PostgreSQL** (OSS no longer boots on embedded Derby). First boot generates/uses keys under `secrets/` (gitignored).

```bash
cd integration/artifactory
# secrets/master.key + join.key are created on first scripted bring-up; compose expects them
docker compose up -d
# First boot can take 3–5 minutes
curl -sf -u admin:password http://localhost:8082/artifactory/api/system/ping
```

UI: http://localhost:8082/ui/

## Create remotes (UI)

### 1) Python Remediated (highest priority)

1. **Administration** → **Repositories** → **Remote** → package type **PyPI**
2. Repository key: `pypi-lightwell-remediated`
3. **URL** (Console → Artifactory tab on *Python Remediated*):
   `https://packages.redhat.com/api/pulp-content/lightwell/python/remediated/`
4. Registry / index suffix: `simple` (leave default)
5. Basic auth: username `11009103|dasmlwsvc`, password = service account token

### 2) Python Validated (broad catalog)

1. Remote PyPI key: `pypi-lightwell-validated`
2. **URL**:
   `https://packages.redhat.com/api/pulp-content/lightwell/python/validated/`
3. Same basic auth service account

### 3) Virtual used by engineering

1. Virtual PyPI key: `pypi-virtual`
2. Include **in order**:
   1. `pypi-lightwell-remediated`
   2. `pypi-lightwell-validated`
   3. (optional) public `pypi` remote
3. Simple index for Poetry/pip:
   `http://localhost:8082/artifactory/api/pypi/pypi-virtual/simple`

```bash
export PYPI_INDEX_URL=http://localhost:8082/artifactory/api/pypi/pypi-virtual/simple
export ARTIFACTORY_USER=admin
export ARTIFACTORY_PASSWORD='<changed-password>'
export USE_LIGHTWELL=true
./scripts/configure-poetry-source.sh
```

## License note (important)

**Artifactory OSS cannot create remote/virtual PyPI repositories** (REST returns “available only in Artifactory Pro”). This Compose stack is still useful to:

- show the admin UI shape during rehearsal
- practice first-boot / Postgres / ports
- apply a **Pro trial license** when available, then run bootstrap

Until Pro/trial is applied, the **working resolve path** in this kit is direct Lightwell Poetry (`USE_LIGHTWELL=true ./scripts/configure-poetry-source.sh`) — already proven against `packages.redhat.com` with `11009103|dasmlwsvc`.

## Automated bootstrap (requires Pro/trial)

```bash
./scripts/artifactory-bootstrap.sh
```

## Talk track

> “Admins add two remotes once — remediated for patched eligible packages, validated for the rest of the RH-built catalog. Developers only see the virtual.”

## Stop

```bash
docker compose down
```
