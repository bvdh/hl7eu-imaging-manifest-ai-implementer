#!/usr/bin/env python3
"""Convert IHE MADO PDF to per-volume Markdown files.

Outputs: mado-md/volume1.md, volume2.md, volume3.md
- Markdown headings with HTML anchors for prose sections
- HTML <table> with <caption> and <a id> for tabular content

Usage:
    python mado-pdf-to-md.py [--pdf PATH] [--out DIR]
    python mado-pdf-to-md.py  # uses defaults
"""

import argparse
import html
import os
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Run: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_PDF = ".cache/IHE_RAD_Suppl_MADO.pdf"
DEFAULT_OUT = "mado-md"

# Page geometry thresholds — measured from TOP of page (pdfplumber 'top' coordinate)
# page.height ≈ 792pt (US letter).  Header occupies top ~70pt; footer bottom ~80pt.
HEADER_TOP_MAX = 70   # lines with top < HEADER_TOP_MAX are running header
FOOTER_TOP_MIN = 700  # lines with top > FOOTER_TOP_MIN are footer

# Font-size thresholds
SIZE_VOLUME_TITLE = 18.0   # 22pt → Volume N heading
SIZE_H2 = 13.5             # 14pt → top-level section
SIZE_CAPTION = 10.5        # 11pt bold → table/figure caption label
BODY_SIZE = 12.0           # dominant body text

# Trailing line-number pattern (IHE supplements embed margin numbers like " 215")
LINE_NUM_RE = re.compile(r'\s+\d{3,4}\s*$')

# Section-number prefix for subsection headings
SECTION_NUM_RE = re.compile(
    r'^(?:\d+(?:\.\d+){1,4}(?:\.\d+)?'    # numeric: 4.107.4.0.1
    r'|[A-Z]+\.\d+(?:\.\d+)*'             # annex: XA.1, A.2.3
    r'|Annex\s+\w+'                        # Annex XA
    r'|Appendix\s+\w+'                     # Appendix A
    r')\s+\S',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Slug / anchor helpers
# ---------------------------------------------------------------------------
_seen_slugs: dict[str, int] = {}


def make_slug(text: str) -> str:
    """Return a unique HTML anchor slug derived from text."""
    global _seen_slugs
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    s = s.strip('-')
    base = s or 'section'
    count = _seen_slugs.get(base, 0)
    _seen_slugs[base] = count + 1
    return base if count == 0 else f"{base}-{count + 1}"


def reset_slugs() -> None:
    global _seen_slugs
    _seen_slugs = {}


# ---------------------------------------------------------------------------
# Page line extraction
# ---------------------------------------------------------------------------
def extract_lines(page: Any) -> list[dict]:
    """Return page words grouped into lines, filtered to content area, with spacing."""
    # Use extract_words to get proper word boundaries and spacing
    try:
        words = page.extract_words(extra_attrs=['fontname', 'size'])
    except Exception:
        words = page.extract_words()

    # Group words into lines by 'top' coordinate (distance from page top)
    by_top: dict[int, list[dict]] = defaultdict(list)
    for w in words:
        top = round(w.get('top', 0))
        by_top[top].append(w)

    lines = []
    for top in sorted(by_top.keys()):
        # Filter header / footer
        if top < HEADER_TOP_MAX or top > FOOTER_TOP_MIN:
            continue
        line_words = sorted(by_top[top], key=lambda w: w['x0'])
        if not line_words:
            continue

        # Reconstruct text with gaps as spaces
        parts = []
        prev_x1 = None
        for w in line_words:
            text = w['text']
            if not text.strip():
                continue
            if prev_x1 is not None and w['x0'] - prev_x1 > 1.5:
                parts.append(' ')
            parts.append(text)
            prev_x1 = w['x1']
        text = ''.join(parts).strip()
        if not text:
            continue

        # Font properties from first word
        first = line_words[0]
        size = round(float(first.get('size', BODY_SIZE)), 1)
        fontname = first.get('fontname', '')
        bold = 'Bold' in str(fontname) or 'Heavy' in str(fontname)

        lines.append({
            'top': top,       # from page top (used for table overlap checks)
            'text': text,
            'size': size,
            'bold': bold,
        })
    return lines


def strip_line_number(text: str) -> str:
    """Remove trailing IHE margin line numbers (e.g. ' 215')."""
    return LINE_NUM_RE.sub('', text).rstrip()


# ---------------------------------------------------------------------------
# Heading classification
# ---------------------------------------------------------------------------
def classify_line(line: dict, body_size: float = BODY_SIZE) -> str:
    """Return one of: 'volume', 'h2', 'h3', 'h4', 'caption', 'body', 'small'."""
    size = line['size']
    bold = line['bold']
    text = line['text']

    if size >= SIZE_VOLUME_TITLE:
        return 'volume'
    if size >= SIZE_H2 and bold:
        return 'h2'
    if size >= body_size - 0.5 and bold:
        # 12pt bold: numbered heading takes priority over caption check
        if SECTION_NUM_RE.match(text):
            prefix = text.split()[0]
            dots = prefix.count('.')
            return 'h4' if dots >= 2 else 'h3'
        # 12pt bold without a section number
        return 'body'
    if size >= SIZE_CAPTION and bold:
        # 11pt bold: table / figure caption label
        return 'caption'
    if size < body_size - 1.5:
        return 'small'  # 9pt/10pt — likely table content
    return 'body'


# ---------------------------------------------------------------------------
# Volume boundary detection
# ---------------------------------------------------------------------------
def find_volume_boundaries(pdf: Any) -> dict[int, int]:
    """Return {volume_number: page_index} by scanning for 22pt 'Volume N' lines."""
    boundaries: dict[int, int] = {}
    for i, page in enumerate(pdf.pages):
        lines = extract_lines(page)
        for line in lines:
            if line['size'] >= SIZE_VOLUME_TITLE:
                m = re.match(r'Volume\s+(\d+)', line['text'], re.IGNORECASE)
                if m:
                    n = int(m.group(1))
                    if n not in boundaries:
                        boundaries[n] = i
    return boundaries


# ---------------------------------------------------------------------------
# Table rendering
# ---------------------------------------------------------------------------
def render_table(table: list[list], title: str, page_num: int, table_idx: int) -> str:
    """Render a pdfplumber table as HTML with caption and anchor."""
    effective_title = title if title else f"Table (page {page_num}, table {table_idx})"
    slug = make_slug(effective_title)

    # Find first non-empty row as header
    header_row = None
    data_rows = []
    for i, row in enumerate(table):
        cleaned = [html.escape(str(cell or '').strip()) for cell in row]
        if any(cleaned):
            if header_row is None:
                header_row = cleaned
            else:
                data_rows.append(cleaned)

    if header_row is None:
        return ''  # empty table, skip

    # If all header cells are blank, use Col N labels
    if not any(header_row):
        header_row = [f'Col {i+1}' for i in range(len(header_row))]

    ncols = len(header_row)

    lines = [
        f'<a id="{slug}"></a>',
        '<table>',
        f'  <caption>{html.escape(effective_title)}</caption>',
        '  <thead>',
        '    <tr>' + ''.join(f'<th>{h}</th>' for h in header_row) + '</tr>',
        '  </thead>',
        '  <tbody>',
    ]
    for row in data_rows:
        # Pad or trim to ncols
        row = (row + [''] * ncols)[:ncols]
        lines.append('    <tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>')
    lines += ['  </tbody>', '</table>', '']
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Table title extraction from page
# ---------------------------------------------------------------------------
def find_table_title(page_lines: list[dict], table_bbox: tuple) -> str:
    """Find the nearest caption/heading line just above a table bounding box.

    table_bbox = (x0, top, x1, bottom) where top/bottom are from page top.
    """
    table_top = table_bbox[1]  # distance from page top to table top edge

    # Collect lines that mention Table/Figure, are above the table (smaller top value),
    # and are close to it (within 60pt)
    candidates = []
    for line in page_lines:
        kind = classify_line(line)
        if kind not in ('caption', 'h2', 'h3', 'h4', 'body'):
            continue
        line_top = line['top']
        if line_top < table_top and re.search(r'\bTable\b|\bFigure\b',
                                               line['text'], re.IGNORECASE):
            candidates.append((line_top, line['text']))

    if not candidates:
        return ''
    # Return the one closest above the table (largest top value still < table_top)
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


# ---------------------------------------------------------------------------
# Per-volume page conversion
# ---------------------------------------------------------------------------
def convert_pages(pdf: Any, page_indices: list[int], volume_num: int) -> str:
    """Convert a sequence of PDF pages to Markdown string."""
    reset_slugs()
    out_lines: list[str] = []
    total_pages = len(pdf.pages)

    for page_idx in page_indices:
        if page_idx >= total_pages:
            continue
        page = pdf.pages[page_idx]
        pdf_page_num = page_idx + 1

        # Extract tables with their bboxes
        raw_tables = page.extract_tables()
        table_areas = page.find_tables()  # for bboxes

        # Extract text lines
        page_lines = extract_lines(page)

        # --- Emit page comment ---
        out_lines.append(f'\n<!-- page {pdf_page_num} -->\n')

        # --- Figure detection placeholder ---
        # (images are not embedded; just comment)
        images = page.images
        if images:
            out_lines.append(f'<!-- figure: page {pdf_page_num} -->\n')

        # Determine which top-ranges are occupied by tables so we skip those lines
        table_top_ranges: list[tuple[float, float]] = []
        for ta in table_areas:
            # ta.bbox = (x0, top, x1, bottom) — top and bottom from page top
            table_top_ranges.append((ta.bbox[1], ta.bbox[3]))

        def in_table(top: float) -> bool:
            for t_top, t_bot in table_top_ranges:
                if t_top - 5 <= top <= t_bot + 5:
                    return True
            return False

        # --- Emit non-table page content ---
        prev_kind = None
        pending_para: list[str] = []

        def flush_para():
            nonlocal pending_para
            if pending_para:
                out_lines.append(' '.join(pending_para) + '\n')
                pending_para = []

        for line in page_lines:
            top = line['top']
            text = strip_line_number(line['text'])
            if not text:
                continue

            # Skip lines that are inside a detected table area
            if in_table(line['top']):
                continue

            kind = classify_line(line)

            if kind == 'volume':
                flush_para()
                slug = make_slug(text)
                out_lines.append(f'\n<a id="{slug}"></a>\n# {text}\n')

            elif kind == 'h2':
                flush_para()
                slug = make_slug(text)
                out_lines.append(f'\n<a id="{slug}"></a>\n## {text}\n')

            elif kind == 'h3':
                flush_para()
                slug = make_slug(text)
                out_lines.append(f'\n<a id="{slug}"></a>\n### {text}\n')

            elif kind == 'h4':
                flush_para()
                slug = make_slug(text)
                out_lines.append(f'\n<a id="{slug}"></a>\n#### {text}\n')

            elif kind == 'caption':
                flush_para()
                # Table/figure caption — emit as bold paragraph
                out_lines.append(f'\n**{text}**\n')

            elif kind == 'small':
                # 9/10pt text outside table area — likely a note or footer remnant
                flush_para()
                out_lines.append(f'*{text}*\n')

            else:  # body
                # Accumulate into paragraph
                pending_para.append(text)

            prev_kind = kind

        flush_para()

        # --- Emit tables in page order (top to bottom) ---
        for t_idx, (raw_table, ta) in enumerate(zip(raw_tables, table_areas)):
            title = find_table_title(page_lines, ta.bbox)
            out_lines.append(
                render_table(raw_table, title, pdf_page_num, t_idx + 1)
            )

    return '\n'.join(out_lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='Convert MADO PDF to Markdown files')
    parser.add_argument('--pdf', default=DEFAULT_PDF,
                        help=f'Path to MADO PDF (default: {DEFAULT_PDF})')
    parser.add_argument('--out', default=DEFAULT_OUT,
                        help=f'Output directory (default: {DEFAULT_OUT})')
    args = parser.parse_args()

    pdf_path = args.pdf
    out_dir = Path(args.out)

    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found at '{pdf_path}'.", file=sys.stderr)
        print("Download with:", file=sys.stderr)
        print(f'  curl -L "https://www.ihe.net/uploadedFiles/Documents/Radiology/'
              f'IHE_RAD_Suppl_MADO.pdf" -o {pdf_path}', file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Opening {pdf_path} …")
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"  Total pages: {total}")

        # Detect volume boundaries
        boundaries = find_volume_boundaries(pdf)
        if not boundaries:
            print("WARNING: No 'Volume N' headings detected. "
                  "Using hard-coded fallback page indices.", file=sys.stderr)
            boundaries = {1: 9, 2: 31, 3: 38}

        vol_nums = sorted(boundaries.keys())
        print(f"  Volumes detected: {vol_nums}")
        for n in vol_nums:
            print(f"    Volume {n} → page index {boundaries[n]} "
                  f"(PDF page {boundaries[n]+1})")

        # Build page ranges for each volume
        vol_ranges: dict[int, list[int]] = {}
        for i, n in enumerate(vol_nums):
            start = boundaries[n]
            end = (boundaries[vol_nums[i+1]] - 1) if i + 1 < len(vol_nums) else total - 1
            vol_ranges[n] = list(range(start, end + 1))

        # Volume titles
        vol_titles: dict[int, str] = {}
        for n, start_idx in boundaries.items():
            page = pdf.pages[start_idx]
            lines = extract_lines(page)
            for line in lines:
                if line['size'] >= SIZE_VOLUME_TITLE:
                    vol_titles[n] = line['text'].strip()
                    break
            else:
                vol_titles[n] = f'Volume {n}'

        # Convert each volume
        stats: dict[int, dict] = {}
        for n in vol_nums:
            page_range = vol_ranges[n]
            title = vol_titles[n]
            print(f"\nConverting Volume {n}: '{title}' "
                  f"(pages {page_range[0]+1}–{page_range[-1]+1}) …")

            md = convert_pages(pdf, page_range, n)

            # Count sections, tables, anchors
            anchors = len(re.findall(r'<a id=', md))
            tables = len(re.findall(r'</table>', md))
            headings = len(re.findall(r'^#{1,4} ', md, re.MULTILINE))
            stats[n] = {'anchors': anchors, 'tables': tables, 'sections': headings}

            # File header
            header = (
                f'# IHE RAD MADO – {title}\n\n'
                f'<!-- Source: {pdf_path} '
                f'pages {page_range[0]+1}–{page_range[-1]+1} -->\n\n'
            )
            out_path = out_dir / f'volume{n}.md'
            out_path.write_text(header + md, encoding='utf-8')
            size_kb = out_path.stat().st_size / 1024
            print(f"  → {out_path}  ({size_kb:.1f} KB, "
                  f"{headings} headings, {tables} tables, {anchors} anchors)")

    # Output contract summary
    print('\n=== Output Contract ===')
    for n in vol_nums:
        s = stats[n]
        out_path = out_dir / f'volume{n}.md'
        print(f"Volume {n}: {out_path}  "
              f"({s['sections']} sections, {s['tables']} tables, {s['anchors']} anchors)")

    # Validation
    print('\n=== Validation ===')
    failed = []
    for n in vol_nums:
        out_path = out_dir / f'volume{n}.md'
        size_kb = out_path.stat().st_size / 1024
        s = stats[n]
        if size_kb < 5:
            failed.append(f"volume{n}.md is only {size_kb:.1f} KB (expected > 5 KB)")
        if s['anchors'] < 5:
            failed.append(f"volume{n}.md has only {s['anchors']} anchors (expected >= 5)")
    if stats.get(3, {}).get('tables', 0) < 10:
        failed.append(f"volume3.md has only {stats.get(3,{}).get('tables',0)} tables "
                      f"(expected >= 10)")
    if failed:
        print("FAILED:")
        for f in failed:
            print(f"  ✗ {f}")
        sys.exit(1)
    else:
        print("All validation checks passed.")


if __name__ == '__main__':
    main()
