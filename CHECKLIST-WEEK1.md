# Week 1 Checklist — Security Scanning Pipeline

## Setup
- [ ] Create a GitHub repo and push this scaffold
- [ ] Enable GitHub Actions (Settings → Actions → Allow all)
- [ ] For public repos: GitHub Advanced Security is free — no extra setup needed
- [ ] Optional: create a free Semgrep account at semgrep.dev and add `SEMGREP_APP_TOKEN` as a repo secret

## Run the pipeline
- [ ] Push to `main` (or open a PR) and watch the Actions tab
- [ ] SAST job: Semgrep runs and flags findings in `app/main.py`
- [ ] SCA job: pip-audit flags vulnerable deps — download the `pip-audit-results.json` artifact
- [ ] Secrets job: Gitleaks flags hardcoded credentials in `app/main.py`
- [ ] View Code Scanning Alerts: Security tab → Code scanning

## Understand the results
- [ ] Read `docs/week1-scanners.md` — can you explain what each scanner found and why it matters?
- [ ] For each Semgrep finding: look up the CWE number it references
- [ ] For each pip-audit CVE: look it up on https://osv.dev

## Run locally
- [ ] Run `semgrep --config p/python app/` on your machine — findings match CI?
- [ ] Run `pip-audit --requirement requirements.txt` locally
- [ ] Run `gitleaks detect --source .` locally

## Fix one finding (stretch goal)
- [ ] Fix ONE Semgrep finding in `app/main.py` (e.g. remove `shell=True`)
- [ ] Update one dep in `requirements.txt` to a non-vulnerable version
- [ ] Verify the fix removes the finding in CI

## Done means:
All three scanner jobs ran in GitHub Actions. You can explain to someone what each scanner found, why it's a risk, and roughly how you'd fix it.
