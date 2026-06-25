# Commit in Both Repos

## What This Skill Produces

- Staged changes committed in both the root repository and the `imaging-manifest-fork` sub-repository
- Single atomic commit message applied to both repos for consistency and traceability
- Clear report of commit hashes and changed file counts per repository
- Suggested commit message if none is provided (analyzed from staged changes)

## When To Use

- Synchronize changes across the dual-repo structure when modifications span both root-level automation/scripts and IG content
- Ensure related changes in both repos are tracked with identical commit messages for cross-repo traceability
- Atomic multi-repo commits without manual per-repo workflows
- Maintain consistency when both `.github/` (root) and `imaging-manifest-fork/` (sub-repo) have correlated changes

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

### Phase 2: Determine Commit Message

**If message provided as argument:**
- Use provided message directly

**If no message provided:**
- Analyze staged file patterns in both repos
- Identify primary areas (FSH files, markdown pages, scripts, config, etc.)
- Generate suggested message following pattern:
  - `[area] Descriptive title (root + fork changes)` if both repos modified
  - `[area] Descriptive title (fork only)` if only fork modified
  - `[area] Descriptive title (root only)` if only root modified
- Include count of modified files: `(N files total)`
- Examples:
  - `docs: Update volume pages with outline fixes and FHIR/DICOM section (mado-volume1, mado-volume3 profiles; 2 files)`
  - `pages: Add FHIR and DICOM section to Volume 3 specification (2 files)`
  - `automation: Extend build-ig skill with QA artifact verification (3 root files; 1 fork file)`
- Report suggested message and require user confirmation before proceeding

### Phase 3: Stage Changes (if needed)

- If user wants to proceed but changes are unstaged, offer to stage all changes
- Confirm user wants to include untracked files (if any)
- Stage via `git add .` in each repo

### Phase 4: Execute Commits

1. Commit in root repo (if staged changes exist):
   ```bash
   cd /home/nly98977/SwArchives/bvdh/hl7eu-imaging-manifest-ai-implementer
   git commit -m "MESSAGE"
   ```
   - Capture commit hash and short message

2. Commit in `imaging-manifest-fork/` (if staged changes exist):
   ```bash
   cd /home/nly98977/SwArchives/bvdh/hl7eu-imaging-manifest-ai-implementer/imaging-manifest-fork
   git commit -m "MESSAGE"
   ```
   - Capture commit hash and short message

### Phase 5: Report Results

Format report with:
- **Commit message**: Exact message used
- **Root repo**: Commit hash, file count
- **Fork repo**: Commit hash, file count
- **Total changed files** across both repos
- **Next action** (if any suggested): push, or further work

## Guardrails

- Always use identical commit message in both repos for consistency
- Require explicit message before committing if analyzing changes
- Do not force-push or rewrite history; only forward commits allowed
- Report both successes and failures clearly (if one repo fails, note both attempts)
- Preserve sub-repo independence: do not alter `imaging-manifest-fork` as a Git submodule dependency (treat as independent repo)

## Completion Checks

- Both repos have new commits with identical messages (where changes existed)
- Commit hashes are distinct (one per repo)
- `git log --oneline -n 1` in each repo shows the new commit
- Changed file count is reasonable (not accidentally committing everything)

## Related Skills

- `agent-customization` — customize this skill or create new automation skills
- `build-ig` — often used after commits to verify build succeeds
- Dual-repo sync patterns in other modernization workflows

