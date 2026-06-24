---
name: generate-ehds-mapping-pages
description: 'Generate per-profile EHDS Xt-EHR mapping include files from xtehr-model-mapping.csv. Use when creating or refreshing imaging-manifest-fork/input/pagecontent/*.md so they match the HL7 Europe Imaging Report xtehr-mapping table layout.'
argument-hint: 'Optional EHDS profile names to limit output; default is all EHDS profiles present in xtehr-model-mapping.csv with mappings'
user-invocable: true
---

# Generate EHDS Mapping Pages

## Outcome

Generate one markdown include file in `imaging-manifest-fork/input/pagecontent/` for each EHDS profile that is included by `imaging-manifest-fork/input/pagecontent/xtehr-mapping.md` and/or appears in `xtehr-model-mapping.csv` with at least one mapping.

Within each generated file, include **all fields defined by the EHDS logical model for that profile**, not only the subset that already has a mapping in xtehr-model-mapping.csv.

Each file must contain a mapping table shaped like the current HL7 Europe Imaging Report Xt-EHR mapping includes, not the older three-column legacy format.

The current xtehr-model-mapping.csv source contains these profile groups:

- `EHDSImagingStudy`
- `EHDSPatient`

Treat those as examples only. Do not hardcode them.

## When To Use

- Generate EHDS mapping pages
- Refresh Xt-EHR mapping includes
- Rebuild `input/pagecontent/*.md` from xtehr-model-mapping.csv
- Create per-profile mapping markdown for the imaging-manifest fork from authoritative Xt-EHR model mappings

## Inputs

- `xtehr-model-mapping.csv` (authoritative Xt-EHR model mapping source)
- `imaging-manifest-fork/input/pagecontent/xtehr-mapping.md` (authoritative include list for rendered Xt-EHR sections)
- An authoritative EHDS logical model field source for each profile being generated
   - preferred: the Xt-EHR logical model `StructureDefinition-<EHDSProfile>` snapshot or differential
   - acceptable fallback: the current upstream per-profile include file when it already reflects the full logical-model row set
- Target directory: `imaging-manifest-fork/input/pagecontent/`
- Table style reference: the published Imaging Report `xtehr-mapping` page and its per-profile include files

## Outputs

- One file per EHDS profile: `<EHDSProfile>-mapping.md`
- Example outputs:
- `imaging-manifest-fork/input/pagecontent/EHDSImagingStudy-mapping.md`
- `imaging-manifest-fork/input/pagecontent/EHDSPatient-mapping.md`

## Required Table Shape

Use HTML inside markdown so the output matches the current upstream page structure.

Each generated file must contain:

1. A profile heading:

```md
#### EHDSImagingStudy
```

2. The standard alignment callout block:

```html
<div class="model-map-block">
   <div class="callout-wrapper">
      <div class="callout-box">

<strong>Ongoing alignment:</strong>
The Xt-EHR logical models are under active revision and continuous refinement.
Updates from Xt-EHR will be progressively incorporated into this Implementation
Guide to maintain alignment with the evolving EHDS specifications.

      </div>
   </div>
</div>
```

3. The standard intro sentence:

```md
The following table shows the mapping from EHDSImagingStudy logical model elements to FHIR profiles.
```

4. A mapping-context block linking the logical model:

```html
<div class="table-wrap">
 <strong>Mapping Context</strong>
 <ul>
 <li>
 <strong>Source logical model:</strong>
 <a href="https://www.xt-ehr.eu/fhir/models/0.3.0/StructureDefinition-EHDSImagingStudy.html" target="_blank">EHDSImagingStudy</a>
 </li>
 </ul>
</div>
```

5. A five-column HTML table with caption and two-row header:

```html
<div class="table-wrap">
 <table summary="EHDSImagingStudy → FHIR Profiles (R4)">
 <caption>EHDSImagingStudy → FHIR Profiles (R4)</caption>
 <thead>
 <tr>
 <th colspan="1" class="src-head">EHDSImagingStudy (Logical Model)</th>
 <th colspan="2" class="tgt-fhir-head">Target FHIR Resource</th>
 <th colspan="1" class="tgt-dicom-head">Target DICOM elements</th>
 <th colspan="1" class="tgt-rationale-head">Rationale</th>
 </tr>
 <tr>
 <th class="src-sub">Element</th>
 <th class="tgt-fhir-sub">Resource</th>
 <th class="tgt-fhir-sub">Element</th>
 <th class="tgt-dicom-sub">DICOM KOS</th>
 <th class="tgt-rationale-sub">Rationale</th>
 </tr>
 </thead>
 <tbody>
 <!-- rows -->
 </tbody>
 </table>
</div>
<!--
Generated file. Do not edit.
-->
```

## Row Generation Rules

Build each table from two sources:

- the EHDS logical model field inventory, which defines the complete set and order of rows
- `xtehr-model-mapping.csv`, which provides Xt-EHR to FHIR profile mappings

### Xt-EHR Model Mapping Data

1. Read rows from `xtehr-model-mapping.csv` with headers representing EHDS classes and field-to-resource mappings.

2. Parse each row to extract:
   - EHDS profile class name (e.g., `EHDSImagingStudy`, `EHDSPatient`)
   - EHDS field name
   - Target EU FHIR profile name
   - Target field name in the EU FHIR profile

3. Group mapping data by EHDS profile name.

4. For each EHDS field, collect zero, one, or many mappings from xtehr-model-mapping.csv.

5. The target profile and element are read directly from xtehr-model-mapping.csv, which serves as the authoritative Xt-EHR source.

6. Preserve the profile name and field names as they appear in xtehr-model-mapping.csv.

### EHDS Logical Model Row Source

8. For each EHDS profile being generated, load the full logical model field inventory from an authoritative source.

9. The logical-model source must provide the complete row set, including:
   - mapped elements
   - unmapped leaf elements
   - unmapped container rows when they are part of the published logical model view
   - rows that have blank target cells
   - rows that use `N/A` notes when that is present in the authoritative source

10. Preserve the logical-model row order from the authoritative EHDS source. Do not reorder rows alphabetically when generating the final page.

11. For each logical-model row, match xtehr-model-mapping.csv rows by exact field name within the corresponding EHDS profile.

12. If a logical-model row has one or more xtehr-model-mapping.csv mappings, emit one rendered table row per mapping.

13. If a logical-model row has no xtehr-model-mapping.csv mapping, still emit the row with blank target cells, preserving any authoritative notes such as `N/A` from the logical-model source.

14. Populate table cells as follows (in column order):
   - `Element`: EHDS element path from the logical-model source without the profile prefix
   - `Resource`: target profile name from the xtehr-model-mapping.csv mapping, preferably as an HTML link to `./StructureDefinition-<TargetProfile>.html`; blank when unmapped
   - `Element`: target element path from the xtehr-model-mapping.csv mapping without the profile prefix; blank when unmapped
   - `DICOM KOS`: DICOM KOS reference from the xtehr-model-mapping.csv `DICOM-KOS` column; if older exports are encountered, accept legacy `KOS (first occurance)` / `KOS (first occurrence)` headers as fallback; blank when not available
   - `Rationale`: merge of mapping rationale and logical-model notes into a single cell; combine authoritative logical-model notes (e.g., `N/A`) with xtehr-model-mapping.csv `Rationale` column when both are available; use one or the other if only one is available; blank when neither is available

16. Preserve exact slice notation and choice notation from both sources:
   - `identifier[accession-number]`
   - `series.instance.extension[number-of-frames]`
   - `value[x]`

17. Preserve full element paths. Do not collapse to the last segment.

18. Deduplicate final table rows within each file by the full rendered cell tuple:
   - EHDS element
   - target resource
   - target element
   - rationale (merged notes and rationale)
   - DICOM KOS

19. When a single EHDS element has multiple overlay mappings, keep those sibling rows grouped under that EHDS element in the same order as the overlays are resolved.

## Non-Negotiable Constraints

- Do not treat xtehr-model-mapping.csv as the complete EHDS row source. It is only the mapping source; logical model fields must come from the authoritative EHDS logical model source.
- Do not omit EHDS logical-model fields merely because they have no mapping in xtehr-model-mapping.csv.
- Do not fabricate unmapped parent rows, blank rows, or `N/A` notes unless an authoritative EHDS logical-model source explicitly supplies them.
- Do not use the obsolete three-column table format found in older generated artifacts.
- Do not discard slice names or reduce full paths to leaf names.
- Do not mix multiple EHDS profiles into one file.
- Do not write files outside `imaging-manifest-fork/input/pagecontent/`.

## Procedure

1. Confirm that `xtehr-model-mapping.csv` exists and is current.
2. Discover all EHDS profiles represented in xtehr-model-mapping.csv with at least one mapping.
3. Discover all EHDS profiles included by `imaging-manifest-fork/input/pagecontent/xtehr-mapping.md` (`{% include <EHDSProfile>-mapping.md %}`).
4. Use the union of mapping-discovered and include-discovered profiles as the generation target set.
5. For each EHDS profile, load the full logical-model field inventory from the authoritative EHDS source.
6. For that same EHDS profile, gather all matching xtehr-model-mapping.csv rows, including logical-model fields where no mapping exists.
7. Merge the complete logical-model row set with the xtehr-model-mapping.csv mappings.
8. Render the per-profile markdown include file with the exact heading, callout, context block, and HTML table wrapper.
9. Write the file to `imaging-manifest-fork/input/pagecontent/<EHDSProfile>-mapping.md`.
10. Repeat for every EHDS profile selected by the union of mapping discovery and include discovery.
11. Run this skill before any IG build (`./_build.sh ...`) whenever mappings, CSV content, or mapping-table layout requirements change.
12. Validate the generated files before finishing.

## Validation Checklist

- A file exists for every EHDS profile with at least one xtehr-model-mapping.csv mapping.
- No file exists for EHDS profiles that have no mappings in xtehr-model-mapping.csv unless the run explicitly asked for them.
- Every file starts with `#### <EHDSProfile>`.
- Every file includes the standard ongoing-alignment callout block.
- Every file uses the five-column HTML table shape: Element | Resource | Element | DICOM KOS | Rationale.
- The source logical model link matches the EHDS profile in the filename.
- Every EHDS logical-model field defined for that profile is present in the table, even when no xtehr-model-mapping.csv mapping exists.
- Table rows preserve full element paths and slice notation exactly.
- Rationale cells combine mapping rationale from xtehr-model-mapping.csv `Rationale` column and authoritative logical-model notes such as `N/A`; include both when available, one or the other when only one is available, otherwise blank.
- No duplicate rendered rows remain in a file.

## Current Workspace Expectations

Based on the current `xtehr-model-mapping.csv`, the generator should currently create:

- `EHDSImagingStudy-mapping.md`
- `EHDSPatient-mapping.md`

Those files must contain the full EHDS logical-model row set for their respective profiles, not just the currently mapped subset from xtehr-model-mapping.csv.

Treat this as a validation example, not as a permanent rule.

## Out Of Scope

- Editing `xtehr-mapping.md` to include the generated files unless explicitly requested
- Reconstructing additional metadata from sources outside xtehr-model-mapping.csv
- Regenerating `xtehr-model-mapping.csv` itself