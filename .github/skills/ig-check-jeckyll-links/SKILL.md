---
name: ig-check-jeckyll-links
description: Check that pages using a Jekyll alias token define the alias, include it in the page, and render it correctly in the generated IG output.
argument-hint: alias token | page scope | build mode
---

# IG Check Jekyll Links

## What This Skill Produces
- A focused validation pass for Jekyll alias usage across the IG source and rendered output.
- A short report that identifies:
  - pages that reference the alias token
  - pages where the alias is not defined or not included
  - rendered output that does not reflect the source alias mapping
  - the first fix to make if the check fails

## When To Use
- Validate alias-driven page links in IG pagecontent, includes, or templates.
- Confirm that a supplied Jekyll alias token is defined before release.
- Compare source pages with generated output after a fresh build.
- Review broken or missing internal links caused by alias changes.

## Preconditions
- Require a fresh build before checking links.
- Treat the check as invalid if the rendered `output/` content is older than the corresponding `input/` content.
- If the build artifacts are stale, rebuild first and re-run the check.

## Scope
- Treat the alias token as a source-level Jekyll reference that must exist in:
  - the page source where it is used
  - the alias definition or include that supplies it
  - the rendered HTML or generated IG output
- Focus on repository-scoped page content rather than broad site-wide link auditing.

## Procedure
1. Find candidate pages
- Search the relevant pagecontent, include, and template files for alias references that match the supplied token.
- Identify every page that uses the alias and every file that defines or imports it.

2. Verify source consistency
- Confirm the alias is defined where the page expects it.
- Confirm the alias is actually included in the page content and not only declared elsewhere.
- Confirm the alias target matches the intended page or include path.

3. Verify rendered output
- Confirm the IG has been built after the latest source changes.
- Confirm the rendered `output/` files are newer than the source `input/` files being checked.
- Compare the generated output against the source pages.
- Confirm the rendered output contains the expected link or alias-expanded text.

4. Triage failures
- If the alias is missing in source, add or restore the definition first.
- If the alias is defined but not included, fix the page include or template wiring.
- If the rendered output is stale, rebuild before changing content.
- If source and output disagree after a fresh build, inspect the owning template or page include.

## Decision Logic
1. If the build is stale, rebuild before evaluating links.
2. If the alias is used in source but not defined, treat that as a source defect.
3. If the alias is defined but does not appear in the page, treat that as an include or wiring defect.
4. If the output is stale relative to the source, rebuild before evaluating the page.
5. If source is correct but output is wrong after a fresh build, treat that as a rendering or template defect.
6. If the alias is present in source and output, pass the page.

## Completion Checks
- Every page that uses the alias has a matching alias definition.
- The alias is present in the page source where required.
- The rendered output was produced by a fresh build and is newer than the checked source content.
- The rendered IG output shows the expected alias-expanded content or link.
- Any mismatch is reduced to a single owning file or include to fix next.

## Scripts

Two scripts in this skill directory automate the mechanical steps of the procedure.
Use them to gather evidence before reasoning about failures.

### `check-alias-tokens.sh` — covers Procedure steps 1 & 2
Scans `input/pagecontent/*.md` and `input/includes/` without requiring a build.
Reports per page:
- `MISSING_INCLUDE` — page uses `{{token}}` but has no `{% include variable-definitions.md %}`
- `UNDEFINED_TOKEN` — token is used but absent from the `{% assign %}` definitions in includes
- `MALFORMED_TOKEN` — triple-brace `{{{token}}}` that leaks a literal `}` into output
- `PASS` — page is clean

```bash
./.github/skills/ig-check-jeckyll-links/check-alias-tokens.sh
```

Exit code equals the number of defects found (0 = pass).

### `check-rendered-tokens.sh` — covers Procedure step 3
Runs against `output/en/` after a build. Reports per page:
- `STALE` — source file is newer than rendered HTML; rebuild required
- `SKIP` — no rendered output exists (page not in sushi-config pages list)
- `FAIL` — literal `{{token}}` found in the rendered HTML (alias was not expanded)
- `PASS` — output is fresh and contains no unresolved token strings

```bash
./.github/skills/ig-check-jeckyll-links/check-rendered-tokens.sh
```

Exit code equals the number of failures plus stale pages (0 = pass).

### Recommended workflow

```bash
# 1. Source check first (no build needed)
./.github/skills/ig-check-jeckyll-links/check-alias-tokens.sh

# 2. Build
./_build.sh build

# 3. Output check
./.github/skills/ig-check-jeckyll-links/check-rendered-tokens.sh
```

Step 4 (triage and fix) remains in agent reasoning — use Decision Logic above.

## Example Prompts
- Check the alias token for the current IG pages.
- Validate that the alias is defined and rendered for the page group I changed.
- Recheck rendered output after a build for broken Jekyll alias links.
