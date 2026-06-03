# Week 1: Security Scanners Explained

## What each scanner does and why it matters

---

### 1. SAST — Semgrep

**What it is:** Static Application Security Testing. Analyses source code without running it.

**What it finds:**
- Hardcoded secrets/passwords in code
- Dangerous function calls (`eval`, `shell=True`, `pickle.loads`)
- OWASP Top 10 patterns: injection, path traversal, insecure deserialization
- Framework-specific misconfigurations

**Why it matters in DevSecOps:** Catches bugs at the earliest possible stage (before code runs anywhere). Faster and cheaper to fix than production incidents.

**Free tier:** Semgrep OSS (no account needed). Optional free cloud dashboard at semgrep.dev.

**Test it finds in `app/main.py`:**
- `shell=True` → command injection risk
- Hardcoded `SECRET_KEY` and `DB_PASSWORD`
- Path traversal in `read_file()`

---

### 2. SCA — pip-audit

**What it is:** Software Composition Analysis. Checks your third-party dependencies for known CVEs.

**What it finds:**
- Dependencies with public CVEs (from OSV database)
- Transitive (indirect) dependency vulnerabilities

**Why it matters:** ~80% of modern application code is third-party libraries. One outdated dependency can expose the whole app (e.g., Log4Shell, SolarWinds).

**Test it finds in `requirements.txt`:**
- `flask==0.12.2` → CVE-2018-1000656 (ReDoS in `url_encode`)
- `Jinja2==2.10` → CVE-2019-10906 (sandbox bypass)
- `requests==2.18.0` → historical CVEs

---

### 3. Secret Scanning — Gitleaks

**What it is:** Scans git history (all commits) and current files for accidentally committed secrets.

**What it finds:**
- AWS/GCP/Azure keys
- API tokens (Stripe, GitHub, Slack, etc.)
- Passwords and private keys
- Custom regex patterns you define

**Why it matters:** Secrets committed to git are permanently in history even if you delete the file. Attackers scan GitHub continuously. A leaked AWS key can rack up thousands of dollars in charges within minutes.

**Test it finds in `app/main.py`:**
- `supersecret123` and `admin1234` — Gitleaks will flag these as potential passwords.

---

## Where results appear

| Scanner | Results location |
|---------|-----------------|
| Semgrep | GitHub Security tab → Code Scanning (if SARIF upload enabled) |
| pip-audit | Actions artifact: `pip-audit-results.json` |
| Gitleaks | Action logs + GitHub Security tab |

---

## Running locally (before pushing)

```bash
# SAST
pip install semgrep
semgrep --config p/python --config p/secrets app/

# SCA
pip install pip-audit
pip-audit --requirement requirements.txt

# Secrets
brew install gitleaks        # macOS
gitleaks detect --source .
```
