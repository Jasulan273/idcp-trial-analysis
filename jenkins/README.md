# Local Jenkins for Assignment 5

This is a trusted, single-user teaching setup, bound to `127.0.0.1:8085`.
It is not a production Jenkins configuration. Anonymous users may read results;
only the local administrator can configure or start jobs. The Docker socket grants
the job host-level Docker authority: do not build untrusted branches or PRs here.
For a shared service, use isolated agents and restrictive authorization instead.

Requirements: a running Docker engine and Docker Compose. On the author's Mac,
the engine runs inside Colima. Other running containers are not changed.

From the repository root, create a private password file (never commit it):

```sh
mkdir -p jenkins/.secrets
chmod 700 jenkins/.secrets
python3 -c "import secrets; from pathlib import Path; p=Path('jenkins/.secrets/admin_password'); p.write_text(secrets.token_urlsafe(32)); p.chmod(0o600)"
docker build -t idcp-assignment5-jenkins:local jenkins/
docker compose -p assignment5 -f jenkins/compose.yml up -d --no-build
```

Open `http://127.0.0.1:8085`, sign in as `assignment-admin` with the password in
that local file, and run `idcp-trial-analysis-ci` once. The job reads `Jenkinsfile`
from this public repository. After that bootstrap build, it polls `main` every minute.
A new detected commit triggers testing, a runtime image build, an offline analysis
and archived JSON/SVG/provenance outputs. Polling may group commits between polls;
it is not an internet webhook. The existing GitHub Actions push checks also remain.

The Python runtime runs as UID/GID 10001. Only code, tests and synthetic input
enter its build context. It requires no network during testing or analysis.
The built image stays local; Docker Hub publishing and Kubernetes deployment
are not configured. Stop the controller when finished:

```sh
docker compose -p assignment5 -f jenkins/compose.yml stop
```

The Docker volume retains the build history. Use `start` to resume it.
