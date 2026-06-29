---
name: create-dicom-sr-tids-tables
description: 'Extract DICOM SR TID node rows only from IHE-MADO Volume 3 and generate authoritative SR CSV plus SR manual-review queue.'
argument-hint: 'Optional output filenames and flags; defaults write SR outputs under ai-result/'
user-invocable: true
---

# Create DICOM SR TID Tables

## Outcome
Generate SR-only outputs:
- ai-result/step10-dicom-templates.csv
- ai-result/step10-dicom-templates-manual-review.csv

## Procedure
1. Run SR TID-focused extraction flow in .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py.
2. Validate SR required fields:
- Template Name
- Template ID
- No
- REL with Parent
- VT
- Concept Name
- Concept URL
- DICOM Section URL
- MADO Page URL
3. Keep rows with missing required fields in SR manual-review CSV.
4. Summarize SR counts and parser gaps.

## Validation
```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py --no-download --skip-url-check
wc -l ai-result/step10-dicom-templates.csv ai-result/step10-dicom-templates-manual-review.csv
```

## Notes
- This skill does not optimize module extraction.
- Prefer MADO values; annotate DICOM differences in DICOM Difference Note.
