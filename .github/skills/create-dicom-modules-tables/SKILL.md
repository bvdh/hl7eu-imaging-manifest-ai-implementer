---
name: create-dicom-modules-tables
description: 'Extract DICOM module rows only from IHE-MADO Volume 3 and generate authoritative module CSV plus module manual-review queue.'
argument-hint: 'Optional output filenames and flags; defaults write module outputs under ai-result/'
user-invocable: true
---

# Create DICOM Module Tables

## Outcome
Generate module-only outputs:
- ai-result/step10-dicom-modules.csv
- ai-result/step10-dicom-modules-manual-review.csv

## Procedure
1. Run module-focused extraction flow in .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py.
2. Validate module required fields:
- Module Name
- Attribute Name
- Tag
- Type
- DICOM Section URL
- MADO Page URL
3. Keep rows with missing required fields in module manual-review CSV.
4. Summarize module counts and parser gaps.

## Validation
```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py --no-download --skip-url-check
wc -l ai-result/step10-dicom-modules.csv ai-result/step10-dicom-modules-manual-review.csv
```

## Notes
- This skill does not optimize SR TID extraction.
- Prefer MADO values; annotate DICOM differences in DICOM Difference Note.
