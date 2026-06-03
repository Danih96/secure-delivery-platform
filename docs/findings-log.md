# Findings Log

Tracks scanner findings, triage decisions, and fix status. Updated after each pipeline run.

---

## Week 1 — Initial scan (first push to main)

| # | Scanner | File | Finding | Severity | Status | Notes |
|---|---------|------|---------|----------|--------|-------|
| 1 | Semgrep (SAST) | `app/main.py` | `shell=True` in subprocess call | High | Open | OS command injection risk — user input passed to shell. Fix: use list form `subprocess.run(["cmd", arg])`. |
| 2 | Semgrep (SAST) | `app/main.py` | Hardcoded `SECRET_KEY` | High | Accepted (test) | Intentional for scanner testing. In a real app: use env var or secrets manager. |
| 3 | Semgrep (SAST) | `app/main.py` | Hardcoded `DB_PASSWORD` | High | Accepted (test) | Same as above. |
| 4 | Semgrep (SAST) | `app/main.py` | Path traversal in `read_file()` | Medium | Open | User-controlled path with no sanitisation. Fix: validate path is within allowed directory. |
| 5 | pip-audit (SCA) | `requirements.txt` | `flask==0.12.2` — CVE-2018-1000656 | High | Open | ReDoS in `url_encode`. Fixed in Flask 0.12.3+. Upgrade to current stable. |
| 6 | pip-audit (SCA) | `requirements.txt` | `Jinja2==2.10` — CVE-2019-10906 | High | Open | Sandbox bypass. Fixed in Jinja2 2.10.1+. |
| 7 | pip-audit (SCA) | `requirements.txt` | `requests==2.18.0` — multiple CVEs | Medium | Open | Several historical CVEs. Upgrade to current stable. |
| 8 | Gitleaks (secrets) | `app/main.py` | Hardcoded password string (`supersecret123`) | High | Accepted (test) | Intentional fake credential for scanner testing. Not a real secret. |
| 9 | Gitleaks (secrets) | `app/main.py` | Hardcoded password string (`admin1234`) | High | Accepted (test) | Same as above. |

---

## Triage notes

**Accepted (test):** findings intentionally introduced to verify scanners fire. These are not real risks — `app/main.py` is a learning artefact, not deployed code.

**Open:** findings that would require a real fix in a production app. Left open here to preserve scanner signal for learning purposes.

**Priority if this were a real app:** fix findings #1 (command injection) and #5/#6 (CVEs with public exploits) first. Both have straightforward fixes and high exploitability.

---

## Reflection (Week 1)

*Which scanner was most useful vs most noisy?*

> Fill in after running the pipeline and reviewing results.
