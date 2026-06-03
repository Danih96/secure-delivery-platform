# Runbook — Credential Leak Response

**Trigger:** Gitleaks alert fires, or a credential is discovered in git history, logs, or a public location.
**Owner:** On-call engineer
**Last tested:** 2026-06-03 (tabletop — INC-001)
**Review cadence:** Quarterly

---

## Severity classification

| Severity | Condition | SLA |
|---|---|---|
| Critical | Credential is in a public repo or public log | Rotate within 5 minutes |
| High | Credential is in a private repo's history | Rotate within 15 minutes |
| Medium | Credential found in internal logs, no external exposure | Rotate within 1 hour |

Default to one severity higher when uncertain.

---

## Step 1 — First 5 minutes

**Goal: close the exposure window.**

1. **Do not panic and do not delete the commit.** Deleting the commit does not remove the credential from git history. Focus on invalidation first.

2. **Identify the credential:**
   - Which service does it belong to?
   - What permissions does it have? (read-only vs read-write vs admin)
   - When was it committed? (`git log --all -S "partial-key-string"`)

3. **Invalidate immediately:**
   - Log into the service that issued the credential.
   - Revoke or rotate the key — do not wait for investigation.
   - Record the exact time of invalidation. This defines the exposure window.

4. **Notify:**
   - Inform the repository owner and team lead.
   - If the repo is public: escalate to Critical regardless of original assessment.

---

## Step 2 — Assess blast radius

**Goal: determine if the credential was used.**

1. Pull the audit log from the issuing service:
   - Look for API calls between the commit timestamp and the invalidation timestamp.
   - Note source IPs — anything outside your known ranges is suspicious.

2. Check if the repo was recently cloned or forked:
   - GitHub: Insights → Traffic → Clones (limited to 14 days).
   - If public: assume the credential was scraped — bots scan GitHub continuously.

3. Document findings in the findings register (Notion from Week 7 onward).

---

## Step 3 — Contain

1. **Suspend the affected developer's push access** to the repository until eradication is complete. This prevents additional commits that complicate the history rewrite.

2. If the credential had write/admin scope, **audit what it could have modified:**
   - Was any data written during the exposure window?
   - Were any permissions changed?

3. If evidence of misuse exists — **stop here and escalate to a full incident.** Do not attempt eradication until the scope is understood.

---

## Step 4 — Eradicate

**Goal: remove the credential from git history.**

> ⚠️ This rewrites history and requires a force-push. Get explicit authorisation from the repository owner before proceeding.

### 4a. Identify what to remove

```bash
# Find the file containing the credential
git log --all --full-history -- path/to/file

# Verify the credential is in the file
git show <commit-hash>:path/to/file
```

### 4b. Rewrite history with git filter-repo

```bash
# Install git-filter-repo (preferred over git filter-branch)
pip install git-filter-repo

# Remove the specific file from all history
git filter-repo --path path/to/file --invert-paths

# Or remove a specific string pattern
git filter-repo --replace-text <(echo 'ACTUAL_SECRET==>REDACTED')
```

### 4c. Force-push

```bash
# Confirm the rewrite looks correct
git log --oneline -10

# Force-push all branches (requires repo owner authorisation)
git push origin --force --all
git push origin --force --tags
```

### 4d. Notify all collaborators

All local clones are now diverged. Everyone must re-clone:

```
The repository history has been rewritten to remove a leaked credential.
Please delete your local clone and re-clone: git clone <repo-url>
Do NOT git pull or git merge — this will reintroduce the old history.
```

### 4e. Rotate any forks

If the repo has forks, GitHub does not automatically update them. Contact fork owners or request GitHub Support to delete fork network history.

---

## Step 5 — Recover

1. **Generate a new credential** with the minimum permissions required (not what was there before — use this as a forcing function for least privilege).

2. **Store it correctly:**
   - GitHub Actions: Settings → Secrets → Actions → New repository secret.
   - Reference in workflow: `${{ secrets.SECRET_NAME }}` — never echo or log this value.
   - Never store in `.env` files that are tracked by git.

3. **Update `.gitignore`** to exclude the file type that caused the leak:
   ```
   *.env
   config/secrets.yml
   credentials.json
   ```

4. **Verify the pipeline is clean:**
   - Push a test commit and confirm Gitleaks reports no findings.

---

## Step 6 — Post-incident

1. **Write the incident report** (`docs/incident-report.md`):
   - Timeline, root cause, impact, IR phases, lessons.
   - Blameless — focus on process gaps, not individuals.

2. **Update the findings register:**
   - Add a row for the credential leak finding.
   - Status: Resolved. Link to incident report.

3. **Action items from this runbook:**
   - [ ] Add Gitleaks pre-commit hook to catch secrets before push:
     ```bash
     # In .git/hooks/pre-commit (or via pre-commit framework)
     gitleaks protect --staged
     ```
   - [ ] Audit all existing credentials for least-privilege scope.
   - [ ] Schedule next runbook test (quarterly).

---

## Quick reference card

```
1. INVALIDATE the credential first — before anything else
2. CHECK the audit log for use during the exposure window
3. git filter-repo --path <file> --invert-paths
4. FORCE-PUSH (authorised)
5. NOTIFY collaborators to re-clone
6. NEW credential — least privilege — stored in Secrets
7. POSTMORTEM — blameless
```

---

## Interview answer

> *"My first action is always to invalidate the credential — not investigate, not delete the commit, not notify the team. Close the exposure window first. Then assess blast radius from the audit log. Eradication means rewriting git history with git filter-repo, not deleting the file — deleting a file leaves the credential in history forever. The force-push step requires explicit authorisation because it affects every collaborator. The whole process goes in a blameless postmortem with a timeline and action items."*
