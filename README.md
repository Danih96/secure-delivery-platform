# secure-delivery-platform

A DevSecOps portfolio project demonstrating security controls at every stage of the software delivery pipeline — built progressively over 13 weeks.

**The problem:** most CI/CD pipelines deliver code fast but treat security as a post-deploy concern. Vulnerabilities, leaked credentials, and vulnerable dependencies reach production because no gate exists to catch them earlier.

**The approach:** shift security left — wire automated scanning into the pipeline so every commit is checked before it can progress. Add security controls one layer at a time: pipeline → container → detection → infrastructure → IaC → cloud → Kubernetes.

---

## Security controls

| Week | Layer | Tool | What it catches |
|------|-------|------|-----------------|
| 1 ✅ | Pipeline — SAST | Semgrep | Insecure code patterns: injection, path traversal, hardcoded secrets |
| 1 ✅ | Pipeline — SCA | pip-audit | Vulnerable dependencies (CVEs via OSV database) |
| 1 ✅ | Pipeline — Secrets | Gitleaks | Accidentally committed credentials in code and git history |
| 2 | Container | Trivy + Hadolint | Image CVEs, Dockerfile misconfigurations |
| 3 | Detection | Prometheus + Alertmanager | Auth failures, container anomalies, outbound connections |
| 4 | Response | — | Incident simulation, postmortem |
| 5 | Infrastructure | — | Proxmox hardening, backup/restore security |
| 6–8 | IaC | Pulumi + Checkov + OPA | Misconfigurations before deploy; policy gates |
| 9 | Cloud | — | Security architecture concepts (Azure / AWS) |
| 10–11 | Kubernetes | kubescape | RBAC, NetworkPolicy, Pod Security |

All Week 1 pipeline jobs run in parallel on every push and PR to `main`. Each job is scoped to `permissions: contents: read` — least privilege applied to the pipeline itself.

→ [`docs/supply-chain.md`](docs/supply-chain.md) — how each control works and what it found  
→ [`docs/findings-log.md`](docs/findings-log.md) — triaged findings with severity and fix status  
→ [`docs/threat-model.md`](docs/threat-model.md) — STRIDE threat model (stub, completed Week 12)

---

## Pipeline (Week 1)

```
push / pull_request to main
          ↓
  ┌───────────────────────────────────────┐
  │  sast     Semgrep     code patterns   │
  │  sca      pip-audit   CVEs            │  ← parallel
  │  secrets  Gitleaks    credentials     │
  └───────────────────────────────────────┘
          ↓
  Results → Security tab / artifacts / job logs
```

View results:
- **Code Scanning alerts:** Security tab → Code scanning
- **SCA report:** Actions → run → Artifacts → `pip-audit-results`
- **Secret scan:** Actions → `secrets` job logs

---

## Repo structure

```
.github/workflows/
  security-scan.yml     ← pipeline: SAST + SCA + secret scanning

app/
  main.py               ← intentionally vulnerable app (scanner test target)

docs/
  supply-chain.md       ← controls: threat, placement, findings, interview answer
  findings-log.md       ← triaged findings with severity and fix status
  threat-model.md       ← STRIDE stub (completed Week 12)
  week1-scanners.md     ← scanner deep-dives and local run instructions

requirements.txt        ← pinned to CVE-carrying versions (SCA test target)
CHECKLIST-WEEK1.md      ← Week 1 exercises
```

> `app/main.py` and `requirements.txt` are **deliberately insecure** for scanner testing. Do not deploy.

---

## Run scanners locally

```bash
pip install semgrep pip-audit
brew install gitleaks       # macOS

# SAST
semgrep --config p/python --config p/owasp-top-ten app/

# SCA
pip-audit --requirement requirements.txt

# Secrets
gitleaks detect --source .
```

---

## Security tradeoff

This repo is **public** to enable free GitHub Advanced Security (SARIF upload to the Security tab). The intentionally vulnerable app is clearly labelled as a learning artefact. No real secrets, credentials, or production data are committed — enforced by `.gitignore` and Gitleaks on every push.
