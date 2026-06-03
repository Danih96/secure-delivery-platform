# Supply Chain Security

Documents the security controls in this pipeline, what threat each one addresses, and what it found.

---

## What is supply-chain security?

A software supply-chain attack targets the tools, dependencies, or pipeline used to build software — not the application itself. Examples: a malicious npm package, a compromised CI runner, a leaked deploy key. Defending against this means treating the pipeline as part of the attack surface.

---

## Controls in this pipeline

### 1. SAST — Semgrep

| | |
|---|---|
| **What it defends against** | Insecure code patterns introduced by developers — command injection, path traversal, hardcoded secrets, OWASP Top 10 patterns |
| **Where it runs** | On every push and pull request to `main`, before any code is deployed |
| **How it works** | Analyses source code statically (without running it) using rule sets (`p/python`, `p/secrets`, `p/owasp-top-ten`) |
| **Results location** | GitHub Security tab → Code Scanning alerts (SARIF upload) |
| **Week 1 finding** | `shell=True` command injection, hardcoded credentials, path traversal in `app/main.py` |
| **Limitation** | Cannot find runtime issues or vulnerabilities in third-party libraries |

### 2. SCA — pip-audit

| | |
|---|---|
| **What it defends against** | Known CVEs in third-party Python dependencies |
| **Where it runs** | On every push and pull request to `main` |
| **How it works** | Checks `requirements.txt` against the OSV vulnerability database. Reports CVE ID, affected version, and fixed version |
| **Results location** | Actions artifact: `pip-audit-results.json` (download from Actions → run → Artifacts) |
| **Week 1 finding** | CVEs in `flask==0.12.2`, `Jinja2==2.10`, `requests==2.18.0` |
| **Limitation** | Only covers direct dependencies in `requirements.txt`; does not scan transitive deps by default without a virtual environment |

### 3. Secret Scanning — Gitleaks

| | |
|---|---|
| **What it defends against** | Accidentally committed secrets — API keys, passwords, tokens, private keys |
| **Where it runs** | On every push and pull request to `main`; scans full git history (`fetch-depth: 0`) |
| **How it works** | Matches patterns (regex + entropy) against all files and all commits in history |
| **Results location** | Actions job logs; also reports to GitHub Security tab |
| **Week 1 finding** | Hardcoded password strings in `app/main.py` (`supersecret123`, `admin1234`) |
| **Limitation** | Pattern-based — can miss novel secret formats; can produce false positives on test fixtures |

---

## Pipeline permissions

Each job is scoped to the minimum permissions it needs:

| Job | Permissions |
|---|---|
| `sast` | `security-events: write` (SARIF upload) + `contents: read` |
| `sca` | `contents: read` |
| `secrets` | `contents: read` |

This follows the principle of least privilege applied to the CI pipeline itself. A compromised third-party action cannot use the `GITHUB_TOKEN` beyond its declared scope.

---

## Where each scanner fits in the pipeline

```
Developer commits code
        ↓
  GitHub Actions triggers
        ↓
  ┌─────────────────────────────────────┐
  │  SAST (Semgrep)    — code patterns  │
  │  SCA (pip-audit)   — dependencies   │  ← all run in parallel
  │  Secrets (Gitleaks)— credentials    │
  └─────────────────────────────────────┘
        ↓
  Results → Security tab / artifacts / logs
```

All three jobs run in parallel on the same trigger. None block the others — a finding in one job does not cancel the other jobs.

---

## Interview answer

> *"I treat the pipeline as part of the attack surface, not just a delivery mechanism. SAST catches insecure patterns before code runs anywhere. SCA flags CVEs in third-party libraries — where ~80% of real-world vulnerabilities live. Secret scanning checks every commit in history, because a secret deleted from a file is still in git history. Each CI job is scoped to least-privilege permissions so a compromised action can't use the token to push code or exfiltrate secrets."*
