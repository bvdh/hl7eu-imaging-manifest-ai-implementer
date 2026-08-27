---
name: ig-qa-check
description: "Validate a FHIR Implementation Guide for profile-reference correctness and publisher quality. Use when checking [[[profile]]] links, direct profile references, MADO/MHD references, Jekyll aliases, rendered hyperlinks, broken links, SUSHI output, or IG QA before release."
argument-hint: "IG path and scope, e.g. imaging-manifest-fork profile links"
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
- Run a pre-release FHIR IG QA pass after narrative, profile, dependency, or link changes.

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

### 2. Check spelling and grammar

Review all in-scope Markdown, FSH descriptions, and newly edited link text for spelling and grammar errors. Preserve FHIR, MADO, MHD, DICOM, Xt-EHR, profile ids, URLs, code, query examples, and other domain-specific identifiers exactly as written.

Check for:

- Misspellings and inconsistent capitalization of artifact names.
- Subject-verb agreement, articles, singular/plural agreement, and punctuation.
- Sentence fragments, duplicated words, awkward wording, and inconsistent terminology.
- Consistent use of `FHIR`, `MADO`, `MHD`, `DICOM`, `DocumentReference`, `StructureDefinition`, and actor names.
- Grammar inside Markdown link labels without changing their destinations.

Use an available spellchecker or linter when present, but manually review domain terms and every proposed correction. Do not treat unknown FHIR or IHE identifiers as spelling errors. Keep editorial corrections separate from link and structural changes so they can be reviewed clearly.

### 3. Apply the smallest source changes

Keep changes limited to the owning source files:

- Add missing `fsh-link-references.md` imports to pages that use resolvable triple-bracket tokens.
- Correct token names when they do not match the declared artifact id.
- Replace unsupported triple-bracket references in FSH descriptions with explicit Markdown links to the authoritative external profile page.
- Reuse existing aliases and link templates before adding new definitions.
- Do not hand-edit generated link-reference files or generated HTML.

### 4. Run focused checks

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

### 5. Build the IG

Run the supported build from inside the guide root:

```sh
./_build.sh build
```

Use `./_build.sh notx` only when terminology-service connectivity blocks the normal build. Do not use a no-SUSHI build when FSH source descriptions or profile definitions changed.

Confirm these files are regenerated:

- `output/qa.json`
- `output/qa-time-report.json`
- `output/qa-time-report.tsv`

### 6. Validate rendered profile links

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

### 7. Report QA results

Read the summary fields from `output/qa.json`:

- `errs`
- `warnings`
- `hints`
- build timestamp and version

Report errors first. Distinguish pre-existing warnings from warnings introduced by the change when a baseline is available. A successful build with warnings is not the same as a clean QA result.

## Completion Criteria

The check is complete when:

- All named profile, actor, and capability references in scope have an authoritative target.
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
