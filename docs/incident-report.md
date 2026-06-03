# Incident Report — INC-001: Leaked API Credential

**Type:** Credential exposure — accidental commit to git
**Status:** Simulated (tabletop exercise — 2026-06-03)
**Severity:** High
**Duration:** 30 minutes (detection to containment)

---

## Timeline

| Time | Event |
|---|---|
| T+0 | Developer pushes `feature/add-integration` to origin. Gitleaks detects an API key in the commit. Pipeline job fails and alert fires. |
| T+3 | Alert routed to `#security-alerts` webhook. On-call engineer acknowledges. |
| T+8 | Investigation starts: credential identified, service confirmed, blast radius assessed. |
| T+15 | Credential invalidated in the integration service admin panel. Exposure window closed. |
| T+22 | Git history audit complete — no evidence of external access during the 15-minute window. |
| T+28 | `git filter-repo` run locally to scrub credential from all history. Force-push authorised. |
| T+35 | New credential generated with minimum required scope. Stored in GitHub Secrets. |
| T+45 | Incident closed. Postmortem scheduled. Findings register updated. |

---

## What happened

A developer was testing a third-party API integration and stored the API key directly in a config file to avoid context-switching to the secrets store. The file was added to git without checking `.gitignore`. It was pushed to a feature branch and caught by Gitleaks on the next push.

---

## Root cause

**Primary:** No pre-commit hook to detect secrets before push. Gitleaks runs in CI — it catches secrets after they reach the remote, not before. A pre-commit hook (local Gitleaks) would have blocked the push at the developer's machine.

**Contributing:** The API key had broader permissions than the integration required (read + write instead of read-only). Least-privilege was not applied when the credential was provisioned.

---

## Impact assessment

| Dimension | Assessment |
|---|---|
| Exposure window | ~15 minutes (T+0 to T+15) |
| Who could see the credential | Anyone with access to the repository and its git history |
| What the credential could do | Read + write access to the integration service |
| Evidence of misuse | None — audit log reviewed, no calls from unknown IPs in the window |
| Worst case if misused | Data read from the integration service; potential write operations |

The 15-minute window is short but non-zero. In a real incident this would trigger a mandatory review of the service's audit log to rule out access.

---

## IR phases

### Detect
- Gitleaks alert fired automatically on push.
- Without the pipeline, detection would have relied on a code reviewer noticing the credential — unreliable and potentially days later.
- **Gap identified:** Gitleaks runs in CI but not as a pre-commit hook. Detection happens after the credential reaches the remote.

### Contain
1. Credential invalidated immediately in the integration service admin panel.
2. Developer notified; feature branch push access temporarily suspended pending investigation.
3. Blast radius assessed: no evidence of access in audit log.

### Eradicate
1. `git filter-repo --path config-file --invert-paths` run locally to remove the file from all history.
2. Force-push authorised by repository owner (documented in runbook).
3. All collaborators notified to re-clone — their local history is now diverged.
4. Branch deleted from origin.

**Why not just delete the file and commit?** The credential is still in git history. Anyone who cloned the repo before the rewrite has the credential. `git filter-repo` rewrites history; deleting the file does not.

### Recover
1. New API key generated in the integration service with read-only scope (least-privilege applied this time).
2. Key stored in GitHub Secrets (`INTEGRATION_API_KEY`), referenced in workflow as `${{ secrets.INTEGRATION_API_KEY }}`.
3. `.gitignore` updated to exclude the config file pattern.
4. Monitoring confirmed no unauthorized use during or after the window.

---

## Lessons learned

| # | Lesson | Action |
|---|---|---|
| 1 | CI-only secret scanning catches leaks after push, not before | Add Gitleaks as a pre-commit hook (local detection) |
| 2 | Credentials provisioned with excessive scope | Audit all existing credentials for least-privilege scope |
| 3 | No documented eradication procedure existed | This runbook (`runbook-credential-leak.md`) is the fix — test quarterly |

---

## Reflection

**Where instinct matched IR:** detection and containment — a Gitleaks alert is unambiguous, and rotating the credential immediately is instinctive.

**Where the framework added value:** eradication. The instinct is to delete the file and move on. The correct action — `git filter-repo` + force-push + collaborator notification — is non-obvious and would be missed without a runbook. The 15-minute exposure window also required an audit log review that wouldn't happen without a formal IR process prompting it.

**What this incident shows a security interviewer:** you understand that git history is permanent without a deliberate rewrite, you know the difference between containment (stop the bleeding) and eradication (remove the root cause), and you treat postmortems as blameless process improvements rather than blame assignments.
