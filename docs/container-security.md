# Container Security

Documents the container hardening controls in this project, what threat each one addresses, and what it found.

---

## What problem does container security solve?

A default Docker setup — `FROM python:latest`, root user, no image scanning — ships an attack surface before a line of app code runs. If an attacker exploits a vulnerability in the app, they inherit whatever privileges the container process has. Hardening limits the blast radius of that exploit and ensures the image itself doesn't carry known CVEs into production.

---

## Controls

### 1. Hardened Dockerfile

**File:** `docker/Dockerfile`

| Control | What it defends against |
|---|---|
| Pinned base image (`python:3.12.10-slim`) | Prevents surprise CVEs from base image updates; reproducible builds; Trivy can report exact CVEs |
| Non-root user (`appuser`) | If the app is exploited, the attacker gets `appuser`, not `root` — limits container escape risk |
| `--shell /bin/false` | Prevents interactive shell login as `appuser` even if `docker exec` is available |
| `--no-create-home` | No writable home directory — removes a convenient place to drop malicious files |
| Dependency layer before app code | Layer caching: `pip install` only reruns when `requirements.txt` changes, not on every code change |
| `--no-cache-dir` on pip install | Smaller image; no pip cache left on disk for an attacker to read |
| `HEALTHCHECK` | Lets the container runtime detect a stuck or crashed process; required by some orchestrator security policies |

**Limitation:** Non-root breaks apps that bind to ports < 1024 (requires `NET_BIND_SERVICE` capability) or write to paths owned by root. Test before enforcing in production.

---

### 2. Dockerfile Lint — Hadolint

| | |
|---|---|
| **What it defends against** | Dockerfile misconfigurations: running as root, using `latest` tag, `ADD` instead of `COPY`, missing `--no-cache-dir`, unpinned `apt-get` versions |
| **Where it runs** | On every push and pull request to `main`, before the image is built |
| **How it works** | Static analysis of the Dockerfile against a rule set; exits non-zero on errors |
| **Results location** | Actions job logs — `hadolint` job |
| **Week 2 finding** | No errors — Dockerfile was written to spec |
| **Limitation** | Lints the Dockerfile only; cannot detect CVEs in the resulting image or vulnerabilities in app code |

---

### 3. Image Scan — Trivy

| | |
|---|---|
| **What it defends against** | CVEs in OS packages (Debian/Alpine) and Python dependencies inside the built image |
| **Where it runs** | On every push and pull request to `main`, after the image is built |
| **How it works** | Builds the image, then scans it against the Trivy vulnerability database (OS + pip). Fails the job on CRITICAL or HIGH findings |
| **Results location** | Actions job logs — `trivy` job |
| **Week 2 finding** | CRITICAL/HIGH CVEs in `flask==0.12.2`, `Jinja2==2.10`, `requests==2.18.0` (intentional — requirements.txt is a scanner test target) |
| **Limitation** | Only catches vulnerabilities with published CVEs; zero-days and logic flaws are out of scope. Image must be rebuilt and rescanned after a base image update |

---

## How the controls layer

```
Developer writes Dockerfile
        ↓
  Hadolint — is the Dockerfile correctly written?
        ↓
  docker build — image is built
        ↓
  Trivy — does the image carry known CVEs?
        ↓
  Runtime — non-root user, no shell, healthcheck active
```

Hadolint catches problems at write time. Trivy catches what slips through at build time. The non-root user limits blast radius at runtime. Each layer has a different scope.

---

## Security tradeoffs

| Tradeoff | Notes |
|---|---|
| Pinned vs floating base image | Pinning gives reproducibility and known CVE state; floating gets automatic security patches. Prefer pinned + a Dependabot or Renovate rule to propose updates. |
| Fail on HIGH vs CRITICAL only | Failing on HIGH catches more real risk but produces more noise from base image CVEs with no fix available. Teams often start at CRITICAL and lower the threshold over time. |
| Slim vs distroless | `slim` is smaller than the full image but still has a shell and package manager. Distroless removes both — harder to debug, harder to exploit. |

---

## Interview answer

> *"I treat the Docker image as part of the attack surface. Hadolint catches Dockerfile misconfigurations before a build — things like running as root or using `latest`. Trivy scans the built image for CVEs in OS packages and Python dependencies. At runtime, the container runs as a non-root user with no shell, so an exploit in the app code doesn't automatically give an attacker root. The key interview point: these are layered controls — build-time linting, build-time scanning, and runtime privilege reduction each catch different things."*
