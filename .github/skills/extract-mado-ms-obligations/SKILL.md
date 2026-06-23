# Extract MADO-MS-Obligations Skill

## Overview

Extract profile field inventories with Must Support indicators and obligations across seven sequential CSV outputs. This skill analyzes three FHIR profile systems (IHE-MADO base, EU imaging-manifest derived, XtEHR EHDS reference) and produces progressive cross-reference mappings with obligation data and DICOM KOS mappings.

## Use Cases

- **When to use**: Generate or refresh field inventory reports showing Must Support indicators and actor-specific obligations across IHE-MADO, EU imaging-manifest, and XtEHR EHDS systems
- **Triggers**: "extract field inventories", "generate MS obligations report", "profile field inventory", "obligations mapping"
- **Input**: FHIR StructureDefinition packages (IHE-MADO, EU imaging-manifest, XtEHR EHDS) and `imaging-manifest-fork/input/mapping/mapping.csv`
- **Output**: Seven CSV files in `ai-result/` directory with progressive enrichment

## Output Files

### Step 1: IHE-MADO Profile Fields (`step1-ihe-mado-fields.csv`)
- **Source**: `~/.fhir/packages/ihe.rad.mado#current/package/StructureDefinition-*.json`
- **Rows**: 1,024+
- **Columns**: Profile, Field, MS
- **Purpose**: Baseline inventory of all IHE-MADO profiles with Must Support flags
- **Field Format**: Element names with slice notation preserved (e.g., `entry[slicename]`, `value[x]`)
- **Deduplication**: After extraction, deduplicate rows so that each combination of (Profile, Field, MS) appears only once in the output

### Step 2: EU imaging-manifest Profile Fields (`step2-eu-mado.csv`)
- **Source**: Generated EU EuMado* profiles from `imaging-manifest-fork/output/`; base profiles via `baseDefinition`
- **Rows**: 800+
- **Columns**: Profile, Field, MS, IHE-MADO, Consumer, Producer, Documentation
- **Purpose**: EU profiles with IHE-MADO base cross-references and obligation codes
- **Field Format**: Element names with slice notation preserved (e.g., `entry[slicename]`, `value[x]`); IHE-MADO cross-references also retain slices
- **Deduplication**: After extraction, deduplicate rows so that each combination of (Profile, Field, MS, IHE-MADO, Consumer, Producer, Documentation) appears only once in the output

### Step 3: XtEHR EHDS Profile Fields with Obligations (`step3-ehds-fields.csv`)
- **Source**: `~/.fhir/packages/xtehr.eu.ehds.models#1.0.0/package/StructureDefinition-EHDS*.json` and Obligations profiles
- **Rows**: 887+
- **Columns**: Profile, Field, Cross-reference, MS, Consumer, Producer
- **Purpose**: EHDS element inventory with actor-specific XtEHR obligations
- **Field Format**: Element names with slice notation preserved (e.g., `entry[slicename]`, `value[x]`)
- **Deduplication**: After extraction, deduplicate rows so that each combination of (Profile, Field, Cross-reference, MS, Consumer, Producer) appears only once in the output

### Step 4: Merged IHE/EU Data (`step4-ihe-eu-mado-fields.csv`)
- **Source**: Steps 1-2 merged
- **Rows**: 973+
- **Columns**: IHE-MADO, EU-MADO, MS, Consumer, Producer, Documentation
- **Purpose**: Combined inventory with MS indicators merged across both systems
- **Cross-Reference Format**: IHE-MADO and EU-MADO columns retain slice notation from source steps (e.g., `MadoBundle.entry[slicename]`, `EuMadoComposition.value[x]`)
- **Deduplication**: After merging, deduplicate rows so that each combination of (IHE-MADO, EU-MADO, MS, Consumer, Producer, Documentation) appears only once in the output

### Step 5: IHE/EU with EHDS Cross-References (`step5-ihe-eu-mado-ehds-fields.csv`)
- **Source**: Step 4 + Step 3 obligation lookup
- **Rows**: 973+
- **Columns**: IHE-MADO, EU-MADO, MS, Consumer, Producer, Documentation, EHDS, EHDS-Consumer, EHDS-Producer
- **Purpose**: Maps IHE-MADO/EU-MADO fields to EHDS references with XtEHR obligations
- **Cross-Reference Format**: All cross-reference columns (IHE-MADO, EU-MADO, EHDS) retain slice notation from source systems
- **Deduplication**: After enrichment, deduplicate rows so that each combination of (IHE-MADO, EU-MADO, MS, Consumer, Producer, Documentation, EHDS, EHDS-Consumer, EHDS-Producer) appears only once in the output

### Step 6: All Fields with EHDS-Only Rows (`step6-all-fields.csv`)
- **Source**: Step 5 + unmapped EHDS fields from Step 3
- **Rows**: 1,800+
- **Columns**: IHE-MADO, EU-MADO, MS, Consumer, Producer, Documentation, EHDS, EHDS-Consumer, EHDS-Producer
- **Purpose**: Complete inventory including EHDS-only fields with no IHE-MADO/EU-MADO counterparts
- **Cross-Reference Format**: All cross-reference columns (IHE-MADO, EU-MADO, EHDS) retain slice notation from source systems
- **Deduplication**: After combining, deduplicate rows so that each combination of (IHE-MADO, EU-MADO, MS, Consumer, Producer, Documentation, EHDS, EHDS-Consumer, EHDS-Producer) appears only once in the output

### Step 7: DICOM KOS Mappings (`step7-mapping.csv`)
- **Source**: `imaging-manifest-fork/input/mapping/mapping.csv`
- **Rows**: 200+ plus any explicit carry-through rows for unmatched `mapping.csv` entries
- **Columns**: Concept, FHIR Imaging Study Manifest, IHE-MADO, DICOM KOS Manifest
- **Purpose**: Parse mapping.csv to extract IHE-MADO profile references and DICOM KOS mappings for use in step 8.
- **Column C (IHE-MADO)**: Contains the IHE-MADO profile path extracted from Column B (FHIR Imaging Study Manifest). If Column B contains "→", only the part after the last "→" is used.
- **Cross-Reference Format**: All cross-reference columns retain slice notation from source systems

### Step 8: DICOM KOS Mappings (`step8-all.csv`)
- **Source**: Step 6 + `step7-mapping.csv`
- **Rows**: 1,800+ plus any explicit carry-through rows for unmatched `step7-mapping.csv` entries
- **Columns**: IHE-MADO, FHIR Imaging Study Manifest, EU-MADO, MS, Consumer, Producer, Documentation, EHDS, EHDS-Consumer, EHDS-Producer, DICOM-KOS
- **Purpose**: Complete inventory with DICOM KOS Manifest references for each IHE-MADO field, while preserving `step7-mapping.csv` column C in its own column instead of copying it into `IHE-MADO`
- **Cross-Reference Format**: All cross-reference columns (IHE-MADO, FHIR Imaging Study Manifest, EU-MADO, EHDS) retain slice notation from source systems
- **Deduplication**: After enrichment, deduplicate rows so that each combination of (IHE-MADO, FHIR Imaging Study Manifest, EU-MADO, MS, Consumer, Producer, Documentation, EHDS, EHDS-Consumer, EHDS-Producer, DICOM-KOS) appears only once in the output

## Extraction Pipeline

The extraction runs seven sequential steps:

1. **IHE-MADO Baseline**: Extract all profiles and fields with Must Support flags; deduplicate by all columns
2. **EU Profiles with Obligations**: Map EU profiles to IHE-MADO bases; extract Consumer/Producer obligations; deduplicate by all columns
3. **EHDS Obligations**: Extract EHDS profiles and match with XtEHR Obligations profiles; deduplicate by all columns
4. **Merge IHE/EU**: Combine Steps 1-2, merging MS indicators; deduplicate by all columns
5. **Add EHDS References**: Find EHDS profile.field mentions in documentation; lookup obligations; deduplicate by all columns
6. **EHDS-Only Fields**: Add unmapped EHDS fields with their XtEHR obligations; deduplicate by all columns
7. **Add DICOM KOS Mappings**: Enrich Step 6 with DICOM KOS Manifest references from `imaging-manifest-fork/input/mapping/mapping.csv`; deduplicate by all columns
  - Copy `mapping.csv` column B into a dedicated `FHIR Imaging Study Manifest` column in Step 7
  - A comma in column B is treated as a separator: each trimmed token becomes its own independent entry with the same `DICOM-KOS` value
  - If a `mapping.csv` row has no matching Step 6 `IHE-MADO` row, append it to Step 7 as an explicit output line with blank `IHE-MADO`, the mapping value in `FHIR Imaging Study Manifest`, and the mapped `DICOM-KOS` value

## Obligation Data

### Consumer/Producer Codes
- **EU imaging-manifest** (Steps 2, 4-5): Extracted from obligation extensions with actor URIs:
  - `http://hl7.eu/fhir/imaging-manifest/ActorDefinition/EuMadoImagingManifestConsumer`
  - `http://hl7.eu/fhir/imaging-manifest/ActorDefinition/EuMadoImagingManifestProducer`
- **XtEHR EHDS** (Steps 3, 5-6): Extracted from obligation extensions with actor URIs:
  - `https://www.xt-ehr.eu/specifications/fhir/actor-consumer`
  - `https://www.xt-ehr.eu/specifications/fhir/actor-producer`

### Obligation Codes Examples
- `SHALL:able-to-populate` — Actor must populate this element
- `SHOULD:process` — Actor should process this element
- `MAY:ignore` — Actor may ignore this element

## Cross-Reference Format

All cross-references use format: `ProfileName.ElementPath`

Slice notation is preserved throughout the pipeline. Examples:
- Without slices: `MadoImagingStudy.bodySite` 
- With slices: `MadoBundle.entry[slicename]`, `EuMadoComposition.target[x]`, `EuMadoDicomKosDocumentReference.value[x]`

## EHDS Reference Matching

- Matches `ProfileName.ElementPath` patterns in documentation text
- Supports bracketed type placeholders: `[EHDSType]` normalized to `[x]`
- Example: `[EHDSOrganization]` matches as `[x]` for cross-profile reference

## Verification Checklist

After running the extraction:

- ✓ All seven CSV files created in `ai-result/` directory
- ✓ Each CSV has correct column headers
- ✓ Row counts match expected coverage
- ✓ Cross-references use ProfileName.ElementPath format with slice notation preserved (e.g., `entry[slicename]`, `value[x]`)
- ✓ Step 1+ Fields retain slice notation from FHIR element paths
- ✓ Step 2+ IHE-MADO cross-references retain slice notation
- ✓ Step 3+ EHDS Fields and cross-references retain slice notation
- ✓ Step 4+ IHE-MADO and EU-MADO cross-references retain slice notation
- ✓ Step 5+ all cross-reference columns (IHE-MADO, EU-MADO, EHDS) retain slice notation
- ✓ Step 6+ all cross-reference columns retain slice notation including EHDS-only rows
- ✓ Step 7+ all cross-reference columns (IHE-MADO, FHIR Imaging Study Manifest, EU-MADO, EHDS) retain slice notation
- ✓ Step 3+ obligations populated where extensions exist
- ✓ Step 4+ MS column combines indicators from both IHE and EU (124+ rows with MS)
- ✓ Step 5+ EHDS column populated where Documentation text mentions valid EHDS fields
- ✓ Step 5+ EHDS-Consumer/Producer columns populated for referenced fields
- ✓ Step 6+ includes all Step 5 rows plus 800+ EHDS-only rows
- ✓ Step 6+ EHDS-only rows have XtEHR obligations populated
- ✓ Step 7+ DICOM-KOS column populated for IHE-MADO fields found in mapping.csv
- ✓ Step 7+ preserves mapping.csv column B in a dedicated column rather than reusing IHE-MADO
- ✓ Step 7+ includes explicit rows for mapping.csv entries that do not match any Step 6 IHE-MADO row
- ✓ No invented data; only actual profile elements included
- ✓ Each output CSV contains no duplicate rows; every row is a unique combination of all its field values

## Technical Details

### Script Location
`scripts/extract-mado-ms-obligations.py`

### Input Package Paths
- IHE-MADO: `~/.fhir/packages/ihe.rad.mado#current/package/`
- XtEHR EHDS: `~/.fhir/packages/xtehr.eu.ehds.models#1.0.0/package/`
- EU profiles: `imaging-manifest-fork/output/StructureDefinition-EuMado*.json`

### Data Structures

**Obligation Extension URL**
```
http://hl7.org/fhir/StructureDefinition/obligation
```

**Sub-extensions**
- `actor` (valueCanonical): Actor URI
- `code` (valueCoding): Obligation code
- `documentation` (valueMarkdown): Requirement text

### Processing Rules

- Extract only elements with path containing '.' (filters root elements)
- Match obligations by comparing actor URI strings exactly
- For multiple EHDS references, concatenate with `'; '` separator
- Normalize bracketed type references: `[SomeType]` → `[x]` for matching

## Constraints

- DO NOT skip the IG build unless explicitly requested; when a build is required, `cd imaging-manifest-fork/` and run `./_build.sh build`
- DO NOT invent profiles, elements, or Must Support flags
- DO NOT mix systems in a single CSV; maintain sequential approach
- ONLY populate cross-references where mapping can be traced
- ONLY extract obligations from Obligations profiles with matching element IDs
