# Commit in Both Repos

## What This Skill Produces

- Staged changes committed in both the root repository and the `imaging-manifest-fork` sub-repository
- **Separate, repo-scoped commit messages** applied to each repo (root message for root changes, fork message for fork changes)
- Clear report of commit hashes and changed file counts per repository
- Suggested commit messages if none provided (analyzed separately from staged changes in each repo)

## When To Use

- Synchronize changes across the dual-repo structure when modifications span both root-level automation/scripts and IG content
- Commit with repo-scoped messages that reflect only each repo's own changes
- Atomic multi-repo commits without manual per-repo workflows
- Maintain clean git history where root-level work is documented in root commits and fork-level work in fork commits

## Decision Logic

1. **Message provided**: Use provided message exactly; skip analysis phase.
2. **No message provided**: Analyze staged changes in both repos; propose descriptive message; confirm with user before commit.
3. **Staged state**: If changes exist but are not staged, offer to stage or abort.
4. **Empty state**: If no changes in either repo, report status and skip commit.

## Procedure

### Phase 1: Collect Change Information

1. Check `git status` in root repo (`/home/nly98977/SwArchives/bvdh/hl7eu-imaging-manifest-ai-implementer`)
   - Count staged changes
   - List staged file paths (first 5)
   - Note unstaged/untracked files
2. Check `git status` in `imaging-manifest-fork/`
   - Count staged changes
   - List staged file paths (first 5)
   - Note unstaged/untracked files

### Phase 2: Determine Commit Messages

**If single message provided as argument:**
- Apply provided message to both repos (root and fork)

**If no message provided:**
- Analyze staged file patterns **separately per repo**
- Generate **distinct** messages for root repo and fork repo:
  - **Root repo message**: Include only root-level changes (skills, scripts, automation, .github/ config)
  - **Fork repo message**: Include only fork-level changes (FSH, markdown pages, diagrams, input/)
- Each message should reflect only its repo's scope:
  - Root example: `skills: Add commit-in-both-repos workflow skill (1 file)`
  - Fork example: `docs: Update volume pages with FHIR/DICOM section and outline fixes (4 files)`
- Report both suggested messages and require user confirmation before proceeding

### Phase 3: Stage Changes (if needed)

- If user wants to proceed but changes are unstaged, offer to stage all changes
- Confirm user wants to include untracked files (if any)
- Stage via `git add .` in each repo

### Phase 4: Execute Commits

1. Commit in root repo (if staged changes exist):
   ```bash
   cd /home/nly98977/SwArchives/bvdh/hl7eu-imaging-manifest-ai-implementer
   git commit -m "ROOT_MESSAGE"
   ```
   - Capture commit hash and short message
   - Use root-specific message (skills, automation, .github/ config)

2. Commit in `imaging-manifest-fork/` (if staged changes exist):
   ```bash
   cd /home/nly98977/SwArchives/bvdh/hl7eu-imaging-manifest-ai-implementer/imaging-manifest-fork
   git commit -m "FORK_MESSAGE"
   ```
   - Capture commit hash and short message
   - Use fork-specific message (pages, profiles, diagrams, input/)
   - **Do NOT mention root-level skills or automation in this message**

### Root repo commit message**: Exact message used (if commit created)
  - Phase 5: Report Results

Format report with:
- **Root repo commit message**: Exact message used (if commit created)
  - Commit hash and file count
- **Fork repo commit message**: Exact message used (if commit created)
  - Commit hash and file count
- **Total changed files** across both repos
- **Next action** (if any suggested): push, or further work
- **Note**: Messages are repo-scoped—root mentions skills/automation, fork mentions content/profiles only

## Guardrails

- **Use repo-scoped messages** (NOT identical messages): root message reflects root changes only, fork message reflects fork changes only
- Require explicit message before committing if analyzing changes (unless user provides single message to apply to both)
- Do not force-push or rewrite history; only forward commits allowed
- Report both successes and failures clearly (if one repo fails, note both attempts)
- Preserve sub-repo independence: do not alter `imaging-manifest-fork` as a Git submodule dependency (treat as independent repo)
- Do not mention root-level changes (skills, scripts) in fork repo commit messages
## Completion Checks

- Both repos have new commits with repo-scoped messages (where changes existed)
- Commit hashes are distinct (one per repo)
- `git log --oneline -n 1` in each repo shows the new commit
- Root commit message reflects only root-level changes
- Fork commit message reflects only fork-level changes (no mention of root skills/automation)

## Related Skills

- `agent-customization` — customize this skill or create new automation skills
- `build-ig` — often used after commits to verify build succeeds
- Dual-repo sync patterns in other modernization workflows

