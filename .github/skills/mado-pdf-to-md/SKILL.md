---
name: mado-pdf-to-md
description: 'Parse the IHE MADO supplement PDF and generate structured Markdown files (one per volume) in mado-md/. Use markdown for prose sections, embedded HTML for tables. Every section heading includes an HTML anchor. Use when asked to convert, extract, or render the MADO PDF as markdown; or when updating mado-md/ after a new MADO PDF revision.'
argument-hint: 'Optional: path to PDF (default: .cache/IHE_RAD_Suppl_MADO.pdf); optional output dir (default: mado-md/)'
user-invocable: true
---

# MADO PDF to Markdown

## What This Skill Produces
One Markdown file per MADO volume placed in `mado-md/`:

| File | Content |
|------|---------|
| `mado-md/volume1.md` | Introduction, actors, use cases, options, groupings |
| `mado-md/volume2.md` | Transactions and message semantics |
| `mado-md/volume3.md` | Content modules, DICOM attribute tables, SR templates |

Each file uses:
- Standard Markdown headings (`#`, `##`, `###`) for prose sections.
- An HTML anchor immediately before each heading: `<a id="section-X-Y"></a>`.
- An HTML `<table>` block (with `<thead>` / `<tbody>`) wherever the PDF contains a data table.
- Plain Markdown paragraphs, bullet lists, and code blocks for all other content.

## Prerequisites
```bash
pip install pdfplumber
```
`pdfplumber` is already used by the extract-dicom-tables script in this repo.

## Bundled Script
`.github/skills/mado-pdf-to-md/scripts/mado-pdf-to-md.py`

Run directly — no extra arguments needed for the defaults:
```bash
python .github/skills/mado-pdf-to-md/scripts/mado-pdf-to-md.py
# or with overrides:
python .github/skills/mado-pdf-to-md/scripts/mado-pdf-to-md.py \
       --pdf .cache/IHE_RAD_Suppl_MADO.pdf \
       --out mado-md
```

## Input
| Item | Default location |
|------|-----------------|
| MADO PDF | `.cache/IHE_RAD_Suppl_MADO.pdf` |
| Output directory | `mado-md/` |

If the PDF is missing, download it first:
```bash
mkdir -p .cache
curl -L "https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_MADO.pdf" \
     -o .cache/IHE_RAD_Suppl_MADO.pdf
```

## Procedure

### Step 1 — Discover volume boundaries
The MADO PDF contains explicitly separated volumes — each volume starts with a clear `Volume N` title page.
Open the PDF with `pdfplumber` and locate each volume boundary by finding pages where the full-page heading text matches `Volume 1`, `Volume 2`, or `Volume 3` (case-insensitive, large font, often centred).

Algorithm:
```python
volume_starts = {}  # {volume_number: page_index}
for i, page in enumerate(pdf.pages):
    words = page.extract_words()
    text = ' '.join(w['text'] for w in words).strip()
    m = re.match(r'^Volume\s+(\d+)', text, re.IGNORECASE)
    if m:
        volume_starts[int(m.group(1))] = i
```
Each volume's page range is `[volume_starts[N], volume_starts[N+1] - 1]`; the last volume runs to the final page.

Record `{volume: N, start_page: X, end_page: Y}` for each volume found.  
If a volume title page is not detected, fall back to scanning the table of contents (usually pages 1–6) for TOC entries that reference `Volume N`.

### Step 2 — Extract and classify each page

For each page within a volume's range:

1. **Tables**: if `page.extract_tables()` returns non-empty results, treat as table content (processed in Step 4).
2. **Headings**: stay close to the visual rendering in the PDF. Use `page.chars` to detect heading lines by combining two signals:
   - **Font size** — any line whose average `char['size']` is ≥ 1.2× the median body font size on that page.
   - **Bold weight** — any line where the majority of chars have `'fontname'` containing `Bold` or `Heavy`.
   A line is a heading candidate if it satisfies **either** condition. Then confirm with numbering pattern `^\d+(\.\d+)*\s+\S` or an `Annex`/`Appendix` prefix.
3. **Body text**: everything else.

Heading level mapping (from font size relative to body):
- ≥ 2.0×  → `#` (H1, volume title only)
- ≥ 1.5×  → `##` (H2, top-level section)
- ≥ 1.2×  → `###` (H3, subsection)
- Bold only, no size increase → `####` (H4, sub-subsection)

Heading numbering patterns to recognise:
- `1`, `1.1`, `1.1.1` — section/subsection/subsubsection
- Annex headings: `Annex A`, `Appendix A`
- IHE transaction-style: `4.ZM.1`, `RAD-ZM`

### Step 3 — Build anchor IDs

For each heading, derive a slug:
```python
import re
def anchor(heading_text: str) -> str:
    slug = heading_text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug
```

Emit before each heading:
```markdown
<a id="SLUG"></a>
## Heading Text
```

### Step 4 — Render tables as HTML

For each extracted table:
1. Derive the table title from the immediately preceding heading or bold label on the same page (e.g. `"Table 4.ZM.1-1. Constraints on ITI-65 ..."`). If none is found, use `"Table (page N, table M)"` as the fallback title.
2. Create an anchor slug from the title using the same `anchor()` function as headings.
3. Treat the first non-empty row as the header row.
4. Normalise cell text: strip whitespace, replace `None` with empty string, escape `<` and `>` as `&lt;` and `&gt;`.
5. Emit the anchor immediately before the table, then the table with a `<caption>`:

```html
<a id="SLUG"></a>
<table>
  <caption>Table 4.ZM.1-1. Constraints on ITI-65 ...</caption>
  <thead>
    <tr><th>Col A</th><th>Col B</th></tr>
  </thead>
  <tbody>
    <tr><td>val1</td><td>val2</td></tr>
  </tbody>
</table>
```

Do not convert tables to Markdown pipe syntax — use HTML throughout to preserve multi-line cells and colspan structure.
Do not emit a separate Markdown heading for the table; the `<caption>` carries the title and the `<a id>` provides the anchor.

### Step 5 — Assemble per-volume Markdown files

For each volume, create `mado-md/volume{N}.md` with:

```markdown
# IHE RAD MADO – Volume N: <Volume Title>

<!-- Source: .cache/IHE_RAD_Suppl_MADO.pdf pages X–Y -->

<a id="SLUG"></a>
## Section Heading

Paragraph text …

<a id="table-slug"></a>
<table>
  <caption>Table N.X-Y. Table Title</caption>
  <thead>…</thead>
  <tbody>…</tbody>
</table>

```

Note: tables are placed inline at the position they appear in the PDF, immediately after the surrounding prose paragraph. Do not group all tables at the end of a section.

Preserve the original section numbering from the PDF in both the anchor ID and the heading text.

### Step 6 — Validate outputs

```bash
# All three files exist and are non-empty
ls -lh mado-md/volume*.md

# Each file contains at least one anchor
grep -c '<a id=' mado-md/volume1.md
grep -c '<a id=' mado-md/volume2.md
grep -c '<a id=' mado-md/volume3.md

# No broken HTML table tags
grep -c '</table>' mado-md/volume3.md
```

Expected results:
- Each `volume*.md` file > 5 KB.
- Each file has at least 5 anchors.
- `volume3.md` contains at least 10 `</table>` close tags (DICOM attribute tables).
- Every `</table>` is preceded by a `<caption>` and an `<a id=` anchor.

## Decision Logic

| Situation | Action |
|-----------|--------|
| PDF not found at default path | Download with curl (Step 1 block above) then continue |
| Volume title page not detected | Fall back to TOC page numbers; volumes are always explicitly separated so a miss means PDF is non-standard — log a warning |
| Heading not detectable by font size/bold | Fall back to section-number pattern (`^\d+(\.\d+)*`) to assign heading level |
| Page has both text and table | Emit text first, then the table in a subsection |
| Table header row is empty | Use column index labels (`Col 1`, `Col 2`, …) |
| Table title not found near table | Use fallback `Table (page N, table M)` as both caption text and anchor slug base |
| Heading level > 4 | Flatten to `####` (do not emit `#####` or deeper) |
| Duplicate anchor slug | Append `-2`, `-3`, … suffixes |
| Page text is garbled (OCR artefacts) | Log a warning and include raw text in an HTML comment: `<!-- raw: … -->` |

## Output Contract

After each run, report:
```
Volume 1: mado-md/volume1.md  (<N> sections, <N> tables, <N> anchors)
Volume 2: mado-md/volume2.md  (<N> sections, <N> tables, <N> anchors)
Volume 3: mado-md/volume3.md  (<N> sections, <N> tables, <N> anchors)
```

If any validation check fails, list the failures and stop before writing partial files.

## Notes
- Do not embed images from the PDF. Log page numbers where figures appear as `<!-- figure: page N -->`.
- Preserve IHE section numbers verbatim (e.g. `4.ZM.1`, `A.1.1`) in both headings and anchor slugs.
- The `mado-md/` directory is gitignored by default (generated output). Check `.gitignore` before committing.
