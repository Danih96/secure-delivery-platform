# Threat Model — secure-delivery-platform

**Status:** Stub — created Week 1. To be completed in Week 12 using STRIDE methodology.

---

## Assets

*What are we protecting?*

- [ ] Source code and git history
- [ ] Pipeline secrets and tokens (`GITHUB_TOKEN`, scanner API keys)
- [ ] Build artefacts (Docker images, deployment packages)
- [ ] Running application and its data
- [ ] Infrastructure (Proxmox nodes, VMs, network)

---

## Trust Boundaries

*Where does trust change between components?*

- [ ] Developer workstation → GitHub (push)
- [ ] GitHub Actions runner → source code (checkout)
- [ ] GitHub Actions runner → external scanner APIs (Semgrep, OSV)
- [ ] Pipeline → deployment target
- [ ] Internet → application

---

## Threats (STRIDE)

*To be completed Week 12. For each threat: component affected, likelihood, impact, existing control, gap.*

| Category | Threat | Component | Control | Gap |
|---|---|---|---|---|
| Spoofing | | | | |
| Tampering | | | | |
| Repudiation | | | | |
| Information disclosure | | | | |
| Denial of service | | | | |
| Elevation of privilege | | | | |

---

## Existing Controls

*Summary of controls in place — update as each week adds a new layer.*

| Week | Control | What it protects |
|---|---|---|
| 1 | SAST (Semgrep) | Insecure code patterns |
| 1 | SCA (pip-audit) | Vulnerable dependencies |
| 1 | Secret scanning (Gitleaks) | Committed credentials |
| 1 | Least-privilege CI permissions | Pipeline token abuse |

---

## Gaps

*Known gaps to address — update as threat model is completed.*

- [ ] No image scanning yet (Week 2)
- [ ] No runtime detection yet (Week 3)
- [ ] No IaC scanning yet (Week 7)
- [ ] No K8s hardening yet (Week 11)
- [ ] Threat model not yet complete (Week 12)
