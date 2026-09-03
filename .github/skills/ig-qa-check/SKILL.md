---
name: ig-qa-check
description: "Validate a FHIR Implementation Guide for profile-reference correctness and publisher quality. Use when checking [[[profile]]] links, direct profile references, MADO/MHD references, Jekyll aliases, rendered hyperlinks, broken links, SUSHI output, or IG QA before release."
Run a focused quality check for a FHIR Implementation Guide, with special attention to references to profiles and other named FHIR artifacts. The check covers source content, FSH descriptions, Jekyll aliases, generated links, publisher QA output, and example coverage for local profiles and named slices.
---

# IG QA Check

## Purpose

Run a focused quality check for a FHIR Implementation Guide, with special attention to references to profiles and other named FHIR artifacts. The check covers source content, FSH descriptions, Jekyll aliases, generated links, and publisher QA output.

This skill is intended for the repository layout where the guide is under `imaging-manifest-fork/`. Adapt the paths if the IG root is supplied explicitly.

The skill's persistent memory of known specification URLs is maintained in [spec-locations.md](./references/spec-locations.md).

## When to Use

- Check whether `[[[ProfileName]]]` references render as hyperlinks.
- Find direct, unlinked references to local profiles, dependency profiles, actors, or capability statements.
- Validate MADO or MHD profile references in narrative pages and FSH descriptions.
- Check that references to specifications declared in `sushi-config.yaml` use the correct dependency version, including build URLs for `dev` and `build` dependencies.
- Confirm that generated StructureDefinition descriptions do not retain unresolved profile tokens.
- Audit example coverage for local profiles and named slices.
- Check that every FHIR element carrying an obligation is marked Must Support.
- Flag lower-case `may`, `should`, and `shall` in narrative prose that reads as an RFC 2119 keyword, and suggest either rewording or upper-casing.
- Run a pre-release FHIR IG QA pass after narrative, profile, dependency, example, or link changes.

## Scope Rules

- Treat `input/` as authoritative source.
- Inspect `input/pagecontent/**/*.md`, `input/includes/**`, and `input/fsh/**/*.fsh`.
- Include both triple-bracket references and direct named-artifact text.
- Distinguish named artifacts from generic FHIR resource words. Do not automatically link generic terms such as `Patient`, `Bundle`, `DocumentReference`, or `ImagingStudy` unless the task explicitly requests it.
- Map local StructureDefinitions to `StructureDefinition-<id>.html`, local ActorDefinitions to `ActorDefinition-<id>.html`, and local CapabilityStatements to `CapabilityStatement-<id>.html`.
- Use explicit Markdown links for external dependency artifacts when the publisher cannot resolve a triple-bracket token.
- Never edit `fsh-generated/`, `temp/`, `output/`, `input-cache/`, or other generated/cache directories.
- Do not edit imported source material such as `mado-md/` unless the user explicitly includes it in scope.

## Procedure

### 1. Check profile and artifact references

1. Confirm the guide root contains `ig.ini`, `sushi-config.yaml`, and `_build.sh`.
2. Check the worktree before changing anything:

```sh
git status --short
```

3. Note pre-existing changes and do not revert them.
4. Identify the relevant declared dependencies and page list in `sushi-config.yaml`.
5. Read [spec-locations.md](./references/spec-locations.md) and use it as a starting point for specification URL comparison. Treat the target guide's `sushi-config.yaml` and current package metadata as authoritative when the memory file is stale.

Search authoritative inputs, excluding generated folders:

```sh
rg -n '\[\[\[[^]]+\]\]\]' input/pagecontent input/fsh
rg -n 'Profile:|Instance:|Parent:|Mado[A-Za-z]+|EuMado[A-Za-z]+|ActorDefinition|CapabilityStatement|StructureDefinition' input/pagecontent input/fsh
```

Classify every finding as:

- Local StructureDefinition
- Dependency StructureDefinition, such as IHE-MADO or IHE-MHD
- Local ActorDefinition
- Local CapabilityStatement
- Generic FHIR resource
- ValueSet, CodeSystem, or other non-profile artifact
- Specification or transaction reference

Record the source file, exact displayed name, expected target, and preferred link form.

Audit specification-version consistency for every dependency named in `sushi-config.yaml`:

- Collect all aliases, direct Markdown/HTML links, and prose references for each declared specification, including MADO, MHD, HL7 EU packages, Xt-EHR, and other named dependencies.
- Compare each discovered location with the matching entry in [spec-locations.md](./references/spec-locations.md), and flag missing, stale, or conflicting entries for verification.
- For a dependency pinned to a release such as `4.2.3`, verify that references point to that release, or to the documented release URL for that exact version.
- For a dependency whose version is `dev` or `build` (including a possible `dec` typo that should be interpreted as `dev` only after confirming the configuration), require references to the corresponding `build.fhir.org` build site rather than a released `profiles.*` site or an older versioned release.
- Treat `current` similarly to a moving build reference unless the repository explicitly documents another target.
- When a source refers to the IHE-MADO PDF, use the PDF document linked from the authoritative RAD-MADO Volume 1 page as the target. Do not construct a different PDF URL or substitute a release/build URL without verifying that it is the PDF referenced by that Volume 1 page.
- Check that repeated references to the same specification use one consistent version and URL family; flag a mixture of build and release URLs.
- Distinguish web links from FHIR canonical, package, `fullUrl`, and `Canonical(...)` values. Do not rewrite canonical identifiers merely because their web documentation has a different URL.

Report each mismatch with the dependency package id and configured version, the source reference, the URL currently used, and the expected release or build target.

After the check, update [spec-locations.md](./references/spec-locations.md) with newly verified specification locations or corrected version mappings. Do not update it from an unverified guess; mark an unknown release path as `not recorded` instead.

Map every finding to its authoritative target using the following evidence in order:

1. `Profile:`, `Instance:`, and `Parent:` declarations in `input/fsh/`.
2. Dependencies in `sushi-config.yaml`.
3. Existing definitions in `input/includes/variable-definitions.md`.
4. The generated `fsh-link-references.md`, only as build evidence.
5. Existing links in the source pages.
6. Generated artifact filenames in `output/en/`, only to confirm the expected destination.

For a local named artifact, prefer the publisher's link-reference syntax when the name is resolvable. For an external MADO/MHD artifact, use its authoritative dependency URL when no generated link reference exists.

Validate source link wiring:

A page using `[[[Name]]]` must import the generated link references where the page-processing pipeline requires it:

```md
{% include fsh-link-references.md %}
```

It may also import `variable-definitions.md` for Jekyll aliases. Confirm that:

- Every token has a matching reference definition or an intentional explicit-link fallback.
- The token spelling exactly matches the artifact id. Do not silently substitute a similar actor name.
- FSH descriptions do not rely on page-only Jekyll includes. Use explicit Markdown links in FSH descriptions when those descriptions are serialized into generated resources.
- Direct named profile references are linkified only when they identify a specific artifact, not when they are generic resource prose or query syntax.

### 1a. Check obligation and Must Support consistency

Audit every local generated `StructureDefinition` for FHIR elements that carry an obligation extension. This includes producer and consumer obligations and applies to obligations introduced by the local differential or inherited into the generated snapshot.

Use the generated JSON as the authoritative structural representation after SUSHI has run:

```sh
find output -maxdepth 1 -name 'StructureDefinition-*.json' -print
rg -n 'http://hl7.org/fhir/StructureDefinition/obligation|"mustSupport"' output/StructureDefinition-*.json
```

For each obligation-bearing element:

1. Identify the exact `ElementDefinition.id`, including slice names and nested paths.
2. Locate the same element in the generated `snapshot.element` array. Use the differential only to identify the local source of the constraint; do not infer the final Must Support state from differential omission.
3. Require `mustSupport: true` on that exact element. A Must Support flag on a parent, unsliced element, or similarly named slice does not satisfy the check.
4. Check both obligation codes when both producer and consumer obligations are present. The number of obligations does not change the single Must Support requirement.
5. Trace failures back to the owning FSH rule or insert, and report the profile, element id, obligation code(s), source file, and generated artifact.

Do not treat an obligation on a non-element metadata object as an element-level requirement unless it is attached to an `ElementDefinition`. Do not hand-edit generated JSON to fix a failure. Report dependency-only failures separately when the obligation originates in an external parent profile and cannot be changed locally.

Report the audit in a table:

| Profile | Element id | Obligation code(s) | Must Support | Source / generated evidence | Result |
|---|---|---|---|---|---|
| `StructureDefinition-id` | `Resource.element[slice]` | `SHALL:populate` | `true` or `false` | FSH path and JSON path | `Pass` or `Fail` |

The check fails if any locally authored obligation-bearing element has `mustSupport` absent or set to `false`. Summarize the total number checked, passed, and failed. This audit is independent of example coverage: an example may exercise an element, but it cannot substitute for the profile's Must Support flag.

### 2. Check spelling and grammar

Review all in-scope Markdown, FSH descriptions, and newly edited link text for spelling and grammar errors. Preserve FHIR, MADO, MHD, DICOM, Xt-EHR, profile ids, URLs, code, query examples, and other domain-specific identifiers exactly as written.

Check for:

- Misspellings and inconsistent capitalization of artifact names.
- Subject-verb agreement, articles, singular/plural agreement, and punctuation.
- Sentence fragments, duplicated words, awkward wording, and inconsistent terminology.
- Consistent use of `FHIR`, `MADO`, `MHD`, `DICOM`, `DocumentReference`, `StructureDefinition`, and actor names.
- Grammar inside Markdown link labels without changing their destinations.

Use an available spellchecker or linter when present, but manually review domain terms and every proposed correction. Do not treat unknown FHIR or IHE identifiers as spelling errors. Keep editorial corrections separate from link and structural changes so they can be reviewed clearly.

### 3. Check work-note validity

When the guide contains `worknote.html` includes, audit every included work note against the current authoritative source and build state. Do not assume that an item is still open because it appears in the note, and do not assume it is complete because the IG builds.

1. Scan the authoritative IG source for every `worknote.html` include, including Markdown and HTML attributes:

```sh
rg -n -i 'worknote\.html' input
```

2. List every match before evaluating it. Record the exact source file and line, plus the complete `text` or equivalent note content.
3. Enumerate each distinct request, proposed wording change, technical change, and follow-up in each discovered include. Split compound notes into separate checks when they can have different outcomes.
4. Locate the owning source for each item in `input/`, `sushi-config.yaml`, scripts, or the resolved dependency package.
5. Check the current implementation and, where relevant, the generated artifact or publisher QA result.
6. Classify each item as one of:
	- `Completed`: implemented and supported by current source/build evidence.
	- `Still required`: not implemented and still applicable.
	- `Partially completed`: some requested aspects are implemented, but a remaining aspect is open.
	- `No longer applicable`: superseded by a newer specification, dependency, design, or decision.
	- `Blocked`: still applicable, but verification or implementation depends on an unavailable external change.
	- `Needs decision`: the note is ambiguous or requires an explicit product/specification decision.
7. Report every discovered include and each actionable item in a table. The `Work-note file` column must identify the exact note or checklist file containing the item, using a workspace-relative path when possible. Include notes with no actionable items as `No actionable request` rather than silently omitting them:

| Work-note file | Include location | Work-note item | Current evidence | Status | Remaining action or rationale |
|---|---|---|---|---|---|
| `input/pagecontent/index.md` | `worknote.html` at line 39 | Exact short description | Source path, generated artifact, build output, or dependency evidence | One classification above | What remains, or why it is complete/outdated |

8. For completed items, cite the current source or generated evidence. For open items, identify the smallest owning change. For no-longer-applicable items, state what superseded them. If an item is derived from multiple notes, list each relevant work-note file. Do not edit the work note as part of this audit unless the user explicitly requests note maintenance.

### 3a. Check lower-case normative language (may/should/shall)

Narrative pages sometimes use `may`, `should`, or `shall` in ordinary prose where a reader could mistake the word for an RFC 2119 conformance keyword, or where the author actually intended a conformance keyword but left it lower-case. Both cases need a human-reviewable suggestion, not a silent rewrite.

1. Search authoritative narrative source, excluding generated folders, for the whole-word, lower-case forms:

```sh
rg -n -w 'may|should|shall' input/pagecontent input/includes
```

2. Discard matches that are already upper-case (`MAY`, `SHOULD`, `SHALL`), matches inside code spans, URLs, or link destinations, and matches that are part of an unrelated compound term.
3. For every remaining match, read the full sentence or paragraph containing it and classify the intent:
	- **Genuine normative requirement** — the sentence states a conformance expectation for implementers (what a system SHALL, SHOULD, or MAY do). Proposed fix: capitalize the keyword to the RFC 2119 form. Note the candidate strength (`MAY`, `SHOULD`, or `SHALL`) based on the sentence's own wording, but flag it for author confirmation rather than assuming a stronger or weaker obligation than written.
	- **Descriptive or explanatory prose** — the sentence is not stating a conformance rule (e.g., background, rationale, or a colloquial use of the word). Proposed fix: reword to avoid the ambiguous keyword instead of capitalizing it (for example, replace informal "should" with "is expected to", "typically", or "can"; replace informal "may" with "can" or "is permitted to").
4. Do not apply either fix automatically; this check is report-first, matching the other audits in this skill. Only make the edit if the user separately confirms the specific wording.
5. Report every finding in a table:

| Page | Line | Paragraph / sentence | Proposed change |
|---|---|---|---|
| `input/pagecontent/example.md` | 42 | Full quoted sentence containing the match | "Capitalize to SHALL (normative requirement)" or "Reword to '...' (not a conformance rule)" |

6. Include a row for a page with no lower-case matches only if the user asked for full coverage confirmation; otherwise omit clean pages from the table and state the total pages scanned.

### 4. Apply the smallest source changes

Keep changes limited to the owning source files:

- Add missing `fsh-link-references.md` imports to pages that use resolvable triple-bracket tokens.
- Correct token names when they do not match the declared artifact id.
- Replace unsupported triple-bracket references in FSH descriptions with explicit Markdown links to the authoritative external profile page.
- Reuse existing aliases and link templates before adding new definitions.
- Do not hand-edit generated link-reference files or generated HTML.

### 5. Run focused checks

From the repository root, run the source checker if its path assumptions match the workspace:

```sh
./.github/skills/ig-check-jeckyll-links/check-alias-tokens.sh
```

For a nested `imaging-manifest-fork/` layout, run the equivalent checks from the guide root or inspect the script first. A checker that searches a non-existent root `input/pagecontent/` is not a valid pass; report or work around that path mismatch.

Also run:

```sh
cd imaging-manifest-fork
git diff --check
rg -n '\[\[\[' input/pagecontent input/fsh
```

The final `rg` should return no unresolved tokens unless a specific token is intentionally retained and documented.

### 6. Build the IG

Run the supported build from inside the guide root:

```sh
./_build.sh build
```

Use `./_build.sh notx` only when terminology-service connectivity blocks the normal build. Do not use a no-SUSHI build when FSH source descriptions or profile definitions changed.

Confirm these files are regenerated:

- `output/qa.json`
- `output/qa-time-report.json`
- `output/qa-time-report.tsv`

### 7. Validate rendered profile links

After a fresh build, run:

```sh
../.github/skills/ig-check-jeckyll-links/check-rendered-tokens.sh
```

Then inspect the affected rendered pages and profile artifacts. Check that:

- No literal `{{token}}` or unresolved `[[[Profile]]]` remains in rendered narrative HTML.
- Local links target the expected `StructureDefinition-*.html`, `ActorDefinition-*.html`, or `CapabilityStatement-*.html` file.
- External MADO/MHD links target the intended dependency URL.
- Generated StructureDefinition descriptions contain the intended external link text/URL rather than the old triple-bracket token.
- Rendered pages do not contain links to stale actor ids or similarly named artifacts.

Useful checks include:

```sh
rg -n '\[\[\[|\{\{[^}]+\}\}' output/en
rg -n 'StructureDefinition-|ActorDefinition-|CapabilityStatement-' output/en/<affected-page>.html output/en/StructureDefinition-*.html
```

### 8. Report QA results

Read the summary fields from `output/qa.json`:

- `errs`
- `warnings`
- `hints`
- build timestamp and version

Produce a complete QA report containing every check that was performed and every issue found. Do not report only the final build status.

First report the checks performed in a table:

| Check ID | Check performed | Scope / command | Evidence inspected | Result |
|---|---|---|---|---|
| `QA-01` | Profile and artifact references | `input/pagecontent`, `input/fsh` | Source references and dependency metadata | Pass / Fail / Not run |

Include rows for every applicable procedure section, at minimum:

- Profile, actor, capability, and specification-reference checks.
- Jekyll alias and rendered-token checks.
- Work-note include discovery and per-note validity checks.
- Obligation-to-Must-Support consistency checks.
- Lower-case `may`/`should`/`shall` normative-language review.
- Profile and named-slice example coverage checks.
- Spelling and grammar review.
- IG build and example validation.
- Publisher QA, broken-link, and required-artifact checks.

Then report issues in severity order in a separate table:

| Severity | Issue ID | Finding | File / artifact | Evidence | Status or next action |
|---|---|---|---|---|---|
| `Error` | `ISSUE-001` | Concrete problem | Workspace-relative path or generated artifact | Command output or source evidence | Required fix or disposition |

Use these severity levels: `Error`, `Warning`, `Info`, and `Note`. Include publisher warnings and unresolved coverage gaps when applicable, even if the build succeeds. Mark pre-existing issues separately from issues introduced by the current change when a baseline is available. If no issues are found, include an explicit `No issues found` row. Do not hide skipped or unavailable checks; mark them `Not run` with the reason.

Report errors first in the narrative summary, followed by warnings, informational findings, and notes. Include the QA counts (`errs`, `warnings`, `hints`, broken links), build timestamp/version, check count by result, and issue count by severity. A successful build with warnings or skipped checks is not a clean QA result.

## Completion Criteria

The check is complete when:

- All named profile, actor, and capability references in scope have an authoritative target.
- Every actionable work-note item in scope has been checked against current source and classified with evidence.
- The final report lists every applicable check performed, including scope, evidence, and result.
- The final report lists every issue found, ordered by severity, including file/artifact, evidence, and disposition; skipped checks are reported with reasons.
- Every locally authored obligation-bearing FHIR element has been checked in the generated snapshot and is marked `mustSupport: true`, or any dependency-only exception is reported explicitly.
- Every lower-case `may`, `should`, or `shall` found in narrative prose has been classified as a normative requirement or descriptive text, with a proposed capitalization or rewording reported in a table (page, line, paragraph, proposed change).
- Every reference to a dependency specification matches the version configured in `sushi-config.yaml`; `dev` and `build` dependencies use the corresponding `build.fhir.org` URL.
- The skill memory in [spec-locations.md](./references/spec-locations.md) records the verified locations used by the check, including any newly discovered or corrected mappings.
- Local triple-bracket references resolve through the generated link-reference mechanism.
- FSH descriptions use explicit links where page-level token resolution is unavailable.
- No unintended unresolved profile token remains in authoritative source or rendered output.
- The fresh IG build completes successfully.
- Rendered-token validation passes.
- `output/qa.json` is inspected and its error/warning counts are reported.
- Generated files were not manually edited.

## Common Failure Modes

- **False source-check pass:** the checker assumes a root `input/pagecontent/` directory, but the guide is nested. Run it from the correct root or adapt the command.
- **Literal triple-bracket text:** the page does not import `fsh-link-references.md`, the token spelling is wrong, or the token is used in a serialized FSH description rather than a Jekyll page.
- **Stale generated include:** rebuild with SUSHI before judging generated link-reference contents.
- **Wrong actor link:** compare the token with the exact `Instance:` id and generated `ActorDefinition-*.html` filename.
- **Broken dependency link:** verify the dependency's canonical URL and version before changing the IG dependency declaration.
- **Unrelated QA noise:** compare against the pre-change QA artifact and avoid fixing unrelated publisher warnings.
