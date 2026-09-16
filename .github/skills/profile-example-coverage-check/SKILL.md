---
name: profile-example-coverage-check
description: 'Check whether IG examples actually exercise the constraints a profile defines — slices, mandatory elements, fixed/pattern values, must-support flags, type constraints and strong bindings. Use for a named profile or the whole IG, when authoring missing examples, or as a pre-ballot/pre-PR completeness gate.'
argument-hint: '[ProfileName|--all] [--version 4.0.1|all]'
---

# Profile Example Coverage Check

Answer the question *"do the examples in this IG actually demonstrate what the profile constrains?"*

A profile can build with zero errors and still have slices, mandatory elements and fixed values that no example ever populates. Those constraints are effectively untested: a change to them breaks nothing locally, and implementers get no worked illustration of how to use them.

## When To Use
- Authoring missing profile examples (the deferred item 3 of [FHIR-58174](https://jira.hl7.org/browse/FHIR-58174)) and needing a precise worklist.
- Before a ballot or PR, to confirm new or changed constraints are demonstrated.
- After changing a profile's slicing, to see whether any example still exercises the changed slice.
- To find profiles that have no conforming instance at all.

## Prerequisite

The IG must have been built, because slicing discriminators are only present in the publisher-generated snapshots under `imaging-manifest-fork/output/`. SUSHI's `fsh-generated/resources/` contains differentials only.

```bash
cd imaging-manifest-fork && bash _build.sh
```

If snapshots are missing the script warns and reports most slices as UNVERIFIABLE.

## Procedure

Run from the repository root.

```bash
# One profile
python3 .github/skills/profile-example-coverage-check/scripts/check-profile-example-coverage.py EuMadoComposition

# Every profile, listing example files and unverifiable targets
python3 .github/skills/profile-example-coverage-check/scripts/check-profile-example-coverage.py --all --version 4.0.1 -v

# Machine-readable output for reporting
python3 .github/skills/profile-example-coverage-check/scripts/check-profile-example-coverage.py --all --json
```

### Options

| Option | Effect |
|---|---|
| `PROFILE` / `--all` | Check one profile (by name, id or canonical) or every profile. Default `--all`. |
| `--version` | `4.0.1` or `all` (default). |
| `--fork-root` | Explicit `imaging-manifest-fork` path. Otherwise resolved from the workspace root. |
| `--include-inherited` | Also require coverage of constraints inherited from IG-local parent profiles. |
| `--include-obligations` | Include `*Obligation*` overlays, skipped by default because they are never instantiated. |
| `-v` / `--verbose` | List example files and unverifiable targets with reasons. |
| `--json` | Emit JSON instead of the text report. |
| `--warn-only` | Always exit 0. |

Exit code is `1` when any target is uncovered, `2` on a setup error.

## What Counts As A Coverage Target

Every element in the profile's differential that carries at least one of:

- **slice** — a named slice introduced by `contains`
- **mandatory** — `min >= 1`
- **fixed** / **pattern** — a fixed or pattern value
- **must-support** — flagged `mustSupport`
- **type-constraint** — a `profile` or `targetProfile` restriction
- **binding** — a `required` or `extensible` binding

A target is **covered** when at least one conforming example populates it.

## How Examples Are Found

Any resource whose `meta.profile` names the profile. The scan walks Bundle entries and contained resources, so an example only reachable inside a document Bundle still counts.

## How Slices Are Matched

| Discriminator | Handling |
|---|---|
| `value` / `pattern` | Compares the slice's fixed/pattern value against the instance, including values declared on child elements. |
| `profile` | Resolves the reference (by `Type/id`, Bundle `fullUrl` or `#contained`) and compares the target's `meta.profile`. |
| `exists` | Compares element presence against the slice's cardinality. |
| extension slices | Matched on `url`. |
| `type` | Reported as UNVERIFIABLE, except type slices on a choice element, which are matched by key name. |

`$this` and `resolve()` are stripped from discriminator paths.

## Reading The Report

- **UNCOVERED** — a real gap. Either no example populates it, or the examples that appear to populate it do not actually satisfy the slice discriminator.
- **UNVERIFIABLE** — the checker cannot decide statically. Review manually; the reason is shown with `-v`.

A frequent and important UNCOVERED case: an entry references an instance that does **not** declare the required profile in `meta.profile`. The reference looks right in the FSH, but the target falls outside the slice. Because slicing is open, the build stays green while the slice goes unexercised.

An UNVERIFIABLE reason of *"no fixed/pattern value at discriminator"* usually means the slice is under-specified — a `value` discriminator with nothing fixed at the discriminator path cannot distinguish its slice. That is worth fixing in the profile, not in the examples.

## Decision Rules

- Treat `examples: NONE` as the highest priority: the profile is entirely undemonstrated.
- Prioritise uncovered **mandatory** and **slice** targets over must-support and binding ones.
- Do not chase UNVERIFIABLE counts to zero; confirm them by inspection instead.
- Obligation overlays are excluded by default; do not add examples for them.

## Quality Criteria

The check is complete when:

1. The IG has been built, so no snapshot warning is emitted.
2. Every profile in scope has been reported.
3. Each UNCOVERED target is either resolved by a new or extended example, or recorded as a deliberate exclusion with a reason.
4. Each UNVERIFIABLE target has been manually reviewed at least once.
5. Re-running the check after example authoring shows the intended reduction in uncovered targets.

## Related Skills

- **ig-preprocess-build-check** — produces the snapshots this check depends on.
- **ig-qa-check** — broader publisher QA; this skill covers example completeness, which QA does not.
