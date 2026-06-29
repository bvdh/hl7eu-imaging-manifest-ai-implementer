# Create DICOM Tables Skill

This directory contains the `create-dicom-tables` skill for extracting DICOM module and SR template definitions from the IHE MADO PDF specification.

## Quick Start

```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py
```

This generates:

- `ai-result/step10-dicom-modules.csv` — authoritative modules rows (one row per attribute)
- `ai-result/step10-dicom-templates.csv` — authoritative template rows (one row per node)
- `ai-result/step10-dicom-modules-manual-review.csv` — incomplete module rows for manual curation
- `ai-result/step10-dicom-templates-manual-review.csv` — incomplete template rows for manual curation
- `ai-result/step10-dicom-summary.json` — run summary, counts, URL check status

## Files in This Skill

- `SKILL.md` — Complete skill documentation with procedures and column definitions
- `scripts/extract-dicom-tables.py` — Python 3 extraction script
- `README.md` — This file

## Installation & Dependencies

Before running the script, ensure Python 3.7+ is installed and install required package:

```bash
pip install pdfplumber
```

**Versions tested:**

- pdfplumber >= 0.7.0
- Python >= 3.7

## Usage Examples

### Extract with default settings

```bash
cd /path/to/hl7eu-imaging-manifest-ai-implementer
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py
```

### Use custom output directory

```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py \
  --output-dir my-data/
```

### Download fresh PDF copy

```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py \
  --verbose
```

### Enable verbose logging

```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py \
  --verbose
```

### Use custom PDF from alternative source

```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py \
  --pdf-url https://mirror.example.com/IHE_RAD_Suppl_MADO.pdf
```

### Skip online URL checks

```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py \
  --skip-url-check
```

## Expected Output

### `step10-dicom-modules.csv`

```csv
Module Name,Attribute Name,Tag,Type,Optionality/Cardinality,IHE Usage,Attribute Description,DICOM Section URL,MADO Page URL,DICOM Difference Note
General Equipment Module,Manufacturer,(0008,0070),2,1,SHALL,Equipment manufacturer,https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.5.html,https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_MADO.pdf#page=43,
```

### `step10-dicom-templates.csv`

```csv
Template Name,Template ID,No,NL,REL with Parent,VT,Concept Name,Concept URL,VM,Req Type (DICOM),Req Type (IHE),Condition,ValueSet Constraint,DICOM Section URL,MADO Page URL,DICOM Difference Note
Key Object Selection Document,1602,1,1,CONTAINS,CODE,Document Title,https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_TID_1602.html,1,M,SHALL,,,https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_TID_1602.html,https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_MADO.pdf#page=45,
```

### Manual-review outputs

Rows with missing required fields are written to:

- `step10-dicom-modules-manual-review.csv`
- `step10-dicom-templates-manual-review.csv`

Each file includes `Missing Fields`, `Parse Notes`, `Source Snippet`, and `Source Page` columns.

## Troubleshooting

### "pdfplumber not installed"

**Solution:** Run `pip install pdfplumber pandas`

### "PDF download failed"

**Solution:** Check internet connection, or manually download PDF and use `--no-download`

```bash
# Download manually, then use:
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py --no-download
```

### "No tables extracted"

**Solution:** The PDF structure may differ from expected. Check with:

```bash
python3 -c "
import pdfplumber
with pdfplumber.open('.cache/IHE_RAD_Suppl_MADO.pdf') as pdf:
    for i, page in enumerate(pdf.pages[:5]):
        print(f'Page {i}: {len(page.extract_tables())} tables')
"
```

### Empty output CSVs

**Solution:** This indicates PDF parsing didn't find expected tables. Options:

1. Manually review PDF and populate CSVs based on Volume 3 content
2. Inspect PDF structure with verbose flag: `--verbose`
3. File an issue with PDF extraction details

### Too many manual-review rows

**Solution:** Parser captured ambiguous rows. Check `Missing Fields` and update extraction logic for those table patterns.

### URL check failures

**Solution:** Re-run with `--skip-url-check` for offline environments, or resolve network/access issues.

## Integration Points

The generated CSVs can be consumed by:

- **Step 11 Enrichment** (extend extract-mado-ms-obligations.py)
  - Join module/template data to DICOM-KOS column from Step 8-9
  - Add module/template obligation signals

- **Volume 3 Documentation** (mado-volume3.md)
  - Replace "[TBD: What do the XtEHR requirements mean for the DICOM manifest? Add table with obligation linked to DICOM elements.]" with module/template data

- **Downstream Mapping Pages**
  - Generate DICOM KOS mapping includes (similar to EHDSImagingStudy-mapping.md)

## Performance Notes

- **Download time:** ~10-15 seconds (first run; cached thereafter)
- **Parse time:** ~5-20 seconds for ~100+ page PDF depending on table density and URL checks
- **Output files:** ~50-200 KB each (depending on extracted content)

## Related Skills

- [extract-mado-ms-obligations](../extract-mado-ms-obligations/SKILL.md)
- [generate-ehds-mapping-pages](../generate-ehds-mapping-pages/SKILL.md)

## Contributing

If PDF parsing fails or produces incorrect results:

1. Run with `--verbose` and capture output
2. Manually inspect a few pages of the PDF Volume 3 section
3. Document the expected table structure
4. Update `parse_pdf_tables()` in `extract-dicom-tables.py` to handle that structure
