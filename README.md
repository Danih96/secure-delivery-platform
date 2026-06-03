# secure-delivery-platform

A minimal, progressive DevSecOps learning repo. Each week adds one layer of security practice.

**Week 1 focus:** Security scanning in CI — SAST, SCA, secret detection.

---

## Repo structure

```
.github/workflows/
  security-scan.yml   ← GitHub Actions pipeline (3 scan jobs)

app/
  main.py             ← Intentionally vulnerable Python app (for scanner testing only)

docs/
  week1-scanners.md   ← What each scanner does, why it matters, how to read results

requirements.txt      ← Pinned to known-vulnerable versions (for SCA testing)
CHECKLIST-WEEK1.md    ← Step-by-step exercises for Week 1
.gitignore
```

---

## What the pipeline does

Three jobs run in parallel on every push/PR to `main`:

| Job | Tool | Scans for |
|-----|------|-----------|
| `sast` | Semgrep | Insecure code patterns |
| `sca` | pip-audit | Vulnerable dependencies |
| `secrets` | Gitleaks | Leaked credentials |

See [`docs/week1-scanners.md`](docs/week1-scanners.md) for details on each tool.

---

## Quickstart

### 1. Push to GitHub

```bash
cd secure-delivery-platform
git init
git add .
git commit -m "Week 1: security scanning scaffold"
git remote add origin https://github.com/YOUR_USERNAME/secure-delivery-platform.git
git push -u origin main
```

### 2. Watch Actions run

Go to your repo → **Actions** tab → click the `Security Scan` workflow.

All three jobs should run. SAST and SCA will find intentional issues — that's expected.

### 3. View results

- **Code Scanning Alerts:** Security tab → Code scanning alerts (Semgrep SARIF)
- **SCA results:** Actions → select the run → Artifacts → `pip-audit-results`
- **Gitleaks:** check the `secrets` job logs

### 4. Run locally

```bash
# Install tools
pip install semgrep pip-audit
brew install gitleaks   # macOS; or: https://github.com/gitleaks/gitleaks#installing

# SAST
semgrep --config p/python --config p/secrets app/

# SCA
pip-audit --requirement requirements.txt

# Secrets
gitleaks detect --source .
```

---

## Important

`app/main.py` and `requirements.txt` are **deliberately insecure** for learning purposes. Do not deploy them.

---

## Roadmap

- Week 1: Security scanning (SAST, SCA, secrets) ← you are here
- Week 2: Container security (Docker image scanning, least-privilege)
- Week 3: IaC security (Terraform/Ansible linting)
- Week 4: CI/CD hardening (branch protection, signed commits, OIDC)
