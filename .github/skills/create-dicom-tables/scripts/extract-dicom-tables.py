#!/usr/bin/env python3
"""Extract detailed DICOM modules and SR templates from IHE MADO Volume 3.

Outputs are strictly separated:
- Authoritative modules CSV (one row per attribute)
- Authoritative templates CSV (one row per template node/content item)
- Manual-review CSVs for rows missing required fields
- Run summary JSON
"""

import os
import sys
import csv
import argparse
import logging
import re
import json
from collections import defaultdict
from typing import List, Dict, Tuple, Optional, Any
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import quote_plus

try:
    from urllib.request import Request
except ImportError:  # pragma: no cover
    Request = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_PDF_URL = (
    "https://www.ihe.net/uploadedFiles/Documents/Radiology/"
    "IHE_RAD_Suppl_MADO.pdf"
)
DEFAULT_OUTPUT_DIR = "ai-result"
DEFAULT_MODULES_FILE = "step10-dicom-modules.csv"
DEFAULT_TEMPLATES_FILE = "step10-dicom-templates.csv"
DEFAULT_MODULES_REVIEW_FILE = "step10-dicom-modules-manual-review.csv"
DEFAULT_TEMPLATES_REVIEW_FILE = "step10-dicom-templates-manual-review.csv"
DEFAULT_SUMMARY_FILE = "step10-dicom-summary.json"
PDF_CACHE_DIR = ".cache"
PDF_CACHE_FILE = os.path.join(PDF_CACHE_DIR, "IHE_RAD_Suppl_MADO.pdf")

MADO_VOLUME3_PAGE_MIN = 41
MADO_VOLUME3_PAGE_MAX = 80

MODULE_COLUMNS = [
    "Module Name",
    "Attribute Name",
    "Tag",
    "Type",
    "Optionality/Cardinality",
    "IHE Usage",
    "Attribute Description",
    "DICOM Section URL",
    "MADO Page URL",
    "DICOM Difference Note",
]

TEMPLATE_COLUMNS = [
    "Template Name",
    "Template ID",
    "No",
    "NL",
    "REL with Parent",
    "VT",
    "Concept Name",
    "Concept URL",
    "VM",
    "Req Type (DICOM)",
    "Req Type (IHE)",
    "Condition",
    "ValueSet Constraint",
    "DICOM Section URL",
    "MADO Page URL",
    "DICOM Difference Note",
]

REVIEW_EXTRA_COLUMNS = ["Missing Fields", "Parse Notes", "Source Snippet", "Source Page"]

# Repairs for truncated Concept Name values at PDF page boundaries (F6)
CONCEPT_NAME_REPAIRS = {
    ("16XX", "EV (121144, DCM,"): 'EV (121144, DCM, "Document Title")',
}

MODULE_REQUIRED = [
    "Module Name",
    "Attribute Name",
    "Tag",
    "Type",
    "DICOM Section URL",
    "MADO Page URL",
]

TEMPLATE_REQUIRED = [
    "Template Name",
    "Template ID",
    "No",
    "REL with Parent",
    "VT",
    "Concept Name",
    "Concept URL",
    "DICOM Section URL",
    "MADO Page URL",
]


def ensure_dependencies() -> bool:
    """Check if required Python packages are installed."""
    try:
        import pdfplumber
        logger.info(f"✓ pdfplumber version {pdfplumber.__version__}")
        return True
    except ImportError as e:
        logger.error(f"Missing required package: {e}")
        logger.error("Install with: pip install pdfplumber")
        return False


def download_pdf(url: str, output_path: str, force_redownload: bool = False) -> bool:
    """
    Download PDF from IHE or use cached version.

    Args:
        url: PDF URL to download
        output_path: Local file path to save PDF
        force_redownload: If True, always download fresh copy

    Returns:
        True if PDF is available, False otherwise
    """
    # Use cached PDF if available and not forcing redownload
    if not force_redownload and os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✓ Using cached PDF: {output_path} ({size_mb:.1f} MB)")
        return True

    # Create cache directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        logger.info(f"Downloading PDF from {url}...")
        with urlopen(url, timeout=30) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✓ Downloaded PDF: {output_path} ({size_mb:.1f} MB)")
        return True
    except URLError as e:
        logger.error(f"✗ Failed to download PDF: {e}")
        return False


def extract_dicom_tag(text: str) -> Optional[str]:
    """
    Extract DICOM tag from text if present.

    DICOM tags are in format (XXXX,XXXX) where X is hex digit.

    Args:
        text: Text potentially containing DICOM tag

    Returns:
        Tag string like "(0010,0010)" or None if not found
    """
    match = re.search(r'\(\s*([0-9A-Fa-f]{2,4})\s*,\s*([0-9A-Fa-f]{2,4})\s*\)', text)
    if not match:
        return None
    group = match.group(1).upper().zfill(4)
    element = match.group(2).upper().zfill(4)
    return f"({group},{element})"


def extract_dicom_type(text: str) -> str:
    match = re.search(r'\b(1C|2C|1|2|3)\b', text)
    return match.group(1) if match else ""


def extract_vm(text: str) -> str:
    match = re.search(r'\b(\d+(?:-\d+)?|\d+-n|1-n)\b', text)
    return match.group(1) if match else ""


def normalize_text(text: str) -> str:
    """
    Normalize extracted PDF text.

    Removes extra whitespace, line breaks, and normalizes spacing.
    Also converts the literal string 'None' (produced by str(None)) to ''.

    Args:
        text: Raw extracted text

    Returns:
        Normalized text
    """
    if not text:
        return ""
    # Replace multiple spaces and newlines with single space
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    # pdfplumber renders empty cells as Python None; str(None) == 'None'
    if text.lower() == 'none':
        return ""
    return text


def parse_module_name_from_context(text: str) -> str:
    """Extract a canonical module/macro name from context rows."""
    if not text:
        return ""
    norm = normalize_text(text)
    # Example: "Attributes from Table C.7-1 Patient Module"
    match = re.search(r'Attributes\s+from\s+Table\s+[^\s]+\s+(.+)$', norm, re.IGNORECASE)
    if match:
        return normalize_text(match.group(1))
    return norm


def should_skip_table(header: List[str]) -> bool:
    """Return True for tables that are not DICOM attribute or template tables.

    Filters out legend, format-code, actor, option, and caption tables that
    appear in the MADO volume but do not contain attribute rows.
    """
    non_empty_cells = [h for h in header if h]
    joined = " ".join(h.lower() for h in non_empty_cells)

    # Single-cell tables (captions, continuation labels) that are not
    # "Attributes from Table …" are not attribute tables
    if len(non_empty_cells) == 1 and "attributes from table" not in joined:
        return True
    skip_indicators = [
        # IHE Usage legend tables: single-cell or two-cell explanation rows
        r'^(m\s*/\s*c\s*/\s*u|r|rc|rc\+|r\+|o|o\+)$',
        # Two-column legend tables with long description in second cell
        "as defined in dicom",
        # Format code tables
        "format code",
        "coding scheme",
        # Actors / Options tables
        "actor",
        # Single-cell IHE Usage column header fragments
        r'^(ihe|ihe usage|usage)$',
        # MHD FHIR / XDS.b mapping tables (Appendix content)
        "mhd fhir",
        "xds.b",
        "documententry",
        "mado name",
        # Vocabulary / code set tables
        "code value",
        "code meaning",
        # IHE Usage legend tables with long descriptions
        "the module is defined",
        "the attribute shall be present",
        "the attribute or its value is optional",
    ]
    for indicator in skip_indicators:
        if indicator.startswith('^') or indicator.endswith('$'):
            if re.match(indicator, joined.strip()):
                return True
        elif indicator in joined:
            return True
    return False


KNOWN_MODULE_HEADER_CELLS = [
    "Attribute Name", "Tag", "IHE Usage", "Attribute Description",
]

KNOWN_TEMPLATE_HEADER_CELLS = [
    "Rel with Parent", "VT", "Concept Name", "VM", "Req Type",
    "Condition", "Value Set Constraint", "DICOM Section URL", "MADO Page URL",
]

_TAG_RE = re.compile(r'\(\s*[0-9A-Fa-f]{2,4}\s*,\s*[0-9A-Fa-f]{2,4}\s*\)')


def normalize_header_cell(cell: str, known_cols: List[str]) -> str:
    """Snap a potentially split header fragment to the nearest known column name."""
    if not cell:
        return cell
    cell_key = cell.lower().replace(" ", "")
    for known in known_cols:
        known_key = known.lower().replace(" ", "")
        if cell_key == known_key or known_key.startswith(cell_key) or cell_key.startswith(known_key):
            return known
    return cell


def resolve_table_header(
    table: List[List],
) -> Tuple[List[str], int, str]:
    """Resolve the effective column header row and data start index.

    The MADO PDF uses two (or more) header-row patterns:

    Module tables:
        row 0: "Attributes from Table C.7-1 Patient Module"  (module name)
        rows 1…N-1: column header rows (may be split across 2-3 rows)
            e.g. row1=["Attribute Name","Tag","","IHE","","Attribute Description"]
                 row2=["","","","Usage","",""]
                 or even row2/3 splitting "Usag" + "e"
        data starts at the first row with a DICOM tag or a non-empty first cell

    Template tables:
        row 0: "Rel with | VT | Concept Name | VM | Req | Condition | Value Set"
        row 1: "Parent |    |               |    | Type|           | Constraint"
        data starts at row 2

    Returns:
        (effective_header, data_start_idx, context_module_name)
    """
    if not table or len(table) == 0:
        return [], 1, ""

    row0 = [normalize_text(str(c)) for c in table[0]]
    row0_text = " ".join(h for h in row0 if h and h.lower() not in ("none", ""))

    # --- Pattern 1: module attribute table ---
    if "attributes from table" in row0_text.lower():
        context_module_name = parse_module_name_from_context(row0_text)
        if len(table) <= 1:
            return row0, 1, context_module_name

        # Scan rows from 1 onward.  A row is a header row if:
        #   - first cell is '' or 'Attribute Name' / 'none'
        #   - all non-empty cells are ≤ 30 chars (no DICOM tag, no long description)
        # The first row that has a DICOM tag OR a non-empty first cell that is not
        # "Attribute Name" marks the start of data.
        header_rows: List[List[str]] = []
        data_start = len(table)  # fallback: no data found
        # Track which column indices have content in collected header rows
        occupied_cols: set = set()

        for i in range(1, len(table)):
            row = [normalize_text(str(c)) for c in table[i]]
            first_cell = row[0] if row else ""
            first_cell_lower = first_cell.lower()
            non_empty = [c for c in row if c]
            row_text = " ".join(non_empty)
            has_tag = bool(_TAG_RE.search(row_text))

            # An explicit header row has 'Attribute Name' in the first cell
            is_explicit_header = first_cell_lower == "attribute name"
            # A continuation row: empty first cell, all non-empty cells are short
            # word fragments (≤30 chars) AND their content columns overlap with
            # columns already used in accumulated header rows.
            row_content_cols = {ci for ci, cell in enumerate(row) if cell}
            is_continuation = (
                not first_cell          # empty first cell
                and non_empty           # has some content
                and not has_tag         # no DICOM tag
                and all(len(c) <= 30 for c in non_empty)  # short fragments only
                and (not occupied_cols or bool(row_content_cols & occupied_cols))
            )

            if has_tag or (first_cell and not is_explicit_header):
                # First data row
                data_start = i
                break
            elif is_explicit_header or is_continuation:
                header_rows.append(row)
                occupied_cols |= row_content_cols
            # else: skip rows with empty first cell but long description text or
            #       description overflow in non-header columns

        if not header_rows:
            return row0, data_start, context_module_name

        # Merge header rows column-by-column; concatenate fragments without space
        # so "IHE" + "Usag" + "e" → "IHEUsage" which snaps to "IHE Usage"
        max_len = max(len(r) for r in header_rows)
        effective: List[str] = []
        for col in range(max_len):
            parts = [r[col] for r in header_rows if col < len(r) and r[col]]
            raw_cell = "".join(parts)  # join without space to fix split words
            # Re-insert space if needed to match known canonical names
            effective.append(normalize_header_cell(raw_cell, KNOWN_MODULE_HEADER_CELLS))

        return effective, data_start, context_module_name

    # --- Pattern 2: SR template table (two-row header with continuation) ---
    if len(table) > 1:
        row1 = [normalize_text(str(c)) for c in table[1]]
        row1_non_empty = [c for c in row1 if c]
        row1_text = " ".join(row1_non_empty)
        # Template header: row 0 has "Rel with", row 1 has "Parent"
        if "rel with" in row0_text.lower() and "parent" in row1_text.lower():
            merged: List[str] = []
            for i in range(max(len(row0), len(row1))):
                h0 = row0[i] if i < len(row0) else ""
                h1 = row1[i] if i < len(row1) else ""
                raw_cell = "".join(p for p in [h0, h1] if p)
                merged.append(normalize_header_cell(raw_cell, KNOWN_TEMPLATE_HEADER_CELLS))
            return merged, 2, ""

    # --- Default: single-row header ---
    return row0, 1, ""


def normalize_tid(value: str) -> str:
    tid = extract_tid(value)
    return tid or normalize_text(value)


def mado_page_url(pdf_url: str, page_num: int) -> str:
    return f"{pdf_url}#page={page_num}"


def dicom_module_url(module_name: str) -> str:
    query = quote_plus(module_name)
    return f"https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_{query}.html"


def dicom_template_url(template_id: str) -> str:
    tid = normalize_tid(template_id)
    if tid.isdigit():
        return f"https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_TID_{tid}.html"
    return "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_A.html"


def dicom_concept_url(concept_name: str) -> str:
    query = quote_plus(concept_name)
    return f"https://dicom.nema.org/medical/dicom/current/output/chtml/part16/search.html?q={query}"


def is_url_reachable(url: str, timeout: int = 10) -> bool:
    if not url:
        return False
    if Request is None:
        return True
    try:
        req = Request(url, method="HEAD")
        with urlopen(req, timeout=timeout):
            return True
    except Exception:
        try:
            with urlopen(url, timeout=timeout):
                return True
        except Exception:
            return False


def is_template_row(row: Dict[str, str]) -> bool:
    """
    Determine if a row represents a template (vs. module).

    Templates typically have TID numbers. Modules do not.

    Args:
        row: Parsed row dictionary

    Returns:
        True if row represents a template
    """
    # Check for TID pattern
    tid_pattern = r'TID\s*\d+'
    for key, value in row.items():
        # Skip metadata fields added by the parser
        if key.startswith('_'):
            continue
        if isinstance(value, str) and re.search(tid_pattern, value):
            return True
        if isinstance(value, str) and "HAS ACQ CONTEXT" in value:
            return True
        if isinstance(value, str) and "|" in value and any(tok in value for tok in ["R+", "RC+", "CODE", "TEXT", "NUM", "UIDREF", "DATE", "TIME", "INCLUDE"]):
            return True
    return False


def header_join(header: List[str]) -> str:
    return " | ".join(h.lower() for h in header if h)


def classify_table(header: List[str]) -> str:
    joined = header_join(header)
    if all(k in joined for k in ["ie", "module", "reference"]) and "attribute" not in joined:
        return "module-summary"
    if any(k in joined for k in ["rel with parent", "vt", "concept name", "template", "tid"]):
        return "template"
    if any(k in joined for k in ["module", "attribute", "tag", "type"]):
        return "module"
    return "unknown"


def extract_tid(text: str) -> Optional[str]:
    """
    Extract TID (Template ID) number from text.

    Args:
        text: Text potentially containing TID

    Returns:
        TID number like "1602" or "16XX" (MADO wildcard) or None if not found
    """
    match = re.search(r'TID\s*(16XX|\d+)', text, re.IGNORECASE)
    if not match:
        return None
    # Normalise the 16XX wildcard to uppercase regardless of source casing
    val = match.group(1)
    return val.upper() if val.upper() == "16XX" else val


def extract_page_template_tid_mapping(page_text: str) -> List[Tuple[str, str]]:
    """Extract ordered (tid, template_name) pairs from table caption text on a page.

    Matches captions like: 'Table 6.X.2.9-1: TID 1600 Template for ...'
    Returns unique list (deduplicates consecutive identical TIDs from repeated captions).
    """
    caption_re = re.compile(
        r'Table\s+[\d.X]+-\d+:\s+TID\s+(16XX|\d+)\b([^\n]*)',
        re.IGNORECASE
    )
    matches = caption_re.findall(page_text)
    result: List[Tuple[str, str]] = []
    prev_tid: Optional[str] = None
    for tid, rest in matches:
        # Normalise 16XX to uppercase
        tid_norm = tid.upper() if tid.upper() == "16XX" else tid
        if tid_norm == prev_tid:
            continue  # skip duplicate caption (same table referenced twice on page)
        prev_tid = tid_norm
        full_name = normalize_text(f"TID {tid_norm} {rest}").strip()
        result.append((tid_norm, full_name or f"TID {tid_norm}"))
    return result


def parse_pdf_tables(pdf_path: str, pdf_url: str, verbose: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Extract DICOM modules and templates from PDF tables.

    Args:
        pdf_path: Path to IHE MADO PDF
        verbose: If True, log detailed extraction progress

    Returns:
        Tuple of (modules_list, templates_list) where each is a list of dicts
    """
    try:
        import pdfplumber
    except ImportError:
        logger.error("pdfplumber not installed. Run: pip install pdfplumber")
        return [], []

    modules: List[Dict[str, Any]] = []
    templates: List[Dict[str, Any]] = []
    rows_processed = 0

    # Cross-page template TID context (persists across page boundaries for continuation tables)
    cross_page_template_id: str = ""
    cross_page_template_name: str = ""

    if verbose:
        logger.info(f"Opening PDF: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"PDF has {total_pages} pages; scanning for DICOM tables...")

            for page_num, page in enumerate(pdf.pages, 1):
                if page_num < MADO_VOLUME3_PAGE_MIN or page_num > MADO_VOLUME3_PAGE_MAX:
                    continue
                # Look for tables on this page
                page_tables = page.extract_tables()
                if not page_tables:
                    if verbose:
                        logger.debug(f"Page {page_num}: no tables found")
                    continue

                # Extract TID captions from page text for template table assignment
                page_text = page.extract_text() or ""
                page_tid_mapping = extract_page_template_tid_mapping(page_text)
                # Counts only template-type tables on this page (used to index page_tid_mapping)
                template_table_local_idx = 0
                # F1: pre-scan to count template tables so continuation tables can be
                # distinguished from new-TID tables (n_continuation first tables on the
                # page continue from a previous page; remaining tables map to page captions)
                n_template_tables_on_page = 0
                for _t in page_tables:
                    if _t and len(_t) >= 2:
                        _hdr, _, _ = resolve_table_header(_t)
                        if classify_table(_hdr) == "template":
                            n_template_tables_on_page += 1
                unique_page_tids_list = [entry[0] for entry in page_tid_mapping]
                n_continuation = max(0, n_template_tables_on_page - len(unique_page_tids_list))

                if verbose and page_tid_mapping:
                    logger.debug(f"Page {page_num}: caption TID mapping: {page_tid_mapping}")

                # context_module_name persists across tables within a page
                context_module_name = ""

                if verbose:
                    logger.debug(f"Page {page_num}: found {len(page_tables)} table(s)")

                for table_idx, table in enumerate(page_tables):
                    if not table or len(table) < 2:
                        continue

                    # Resolve the effective column headers, data start row, and
                    # any module name embedded in a row-0 "Attributes from Table…" header.
                    effective_header, data_start_idx, detected_module = resolve_table_header(table)
                    header = effective_header
                    table_type = classify_table(header)

                    # Initialise per-table template context (overridden below for template tables)
                    context_template_name = ""
                    context_template_id = ""

                    # Assign TID from page caption mapping for template tables.
                    # Must happen before should_skip_table so the local index counter
                    # is only incremented for genuinely classified template tables.
                    #
                    # F1: use n_continuation to correctly identify continuation tables.
                    # The first n_continuation template tables on the page continue from
                    # the previous page; subsequent tables map to page caption TIDs.
                    if table_type == "template":
                        if template_table_local_idx < n_continuation:
                            # Continuation from previous page — carry forward previous TID
                            context_template_id = cross_page_template_id
                            context_template_name = cross_page_template_name
                        else:
                            tid_idx = template_table_local_idx - n_continuation
                            if tid_idx < len(page_tid_mapping):
                                tid_entry = page_tid_mapping[tid_idx]
                                context_template_id = tid_entry[0]
                                context_template_name = tid_entry[1]
                                # Persist for continuation tables on subsequent pages
                                cross_page_template_id = context_template_id
                                cross_page_template_name = context_template_name
                            elif cross_page_template_id:
                                context_template_id = cross_page_template_id
                                context_template_name = cross_page_template_name
                        template_table_local_idx += 1
                    elif table_type == "unknown":
                        # Possible fragmented template table from page break;
                        # row-level injection of cross_page TID happens below.
                        pass

                    # Skip tables that are not attribute/template tables
                    if should_skip_table(header):
                        if verbose:
                            logger.debug(f"  Table {table_idx}: skipped (legend/format table) header={header}")
                        continue

                    header_text = normalize_text(" ".join(h for h in header if h and h.lower() != "none"))

                    if detected_module:
                        context_module_name = detected_module
                    elif "attributes from table" not in " ".join(
                        normalize_text(str(c)) for c in table[0]
                    ).lower():
                        # Non-module-named table: preserve existing context
                        pass

                    if verbose:
                        logger.debug(f"  Table {table_idx} type={table_type} "
                                     f"data_start={data_start_idx} "
                                     f"header: {header}")

                    if table_type == "module-summary":
                        # This table lists modules used by MADO; it is not an attribute table.
                        continue

                    # Parse table rows (start from resolved data row index)
                    for row_idx, row_data in enumerate(table[data_start_idx:], data_start_idx + 1):
                        try:
                            row_dict = parse_table_row(header, row_data)
                            if not row_dict:
                                continue

                            non_empty_cells = [normalize_text(str(c)) for c in row_data if c is not None and normalize_text(str(c))]
                            if len(non_empty_cells) == 1:
                                candidate = non_empty_cells[0]
                                if "module" in candidate.lower():
                                    context_module_name = candidate
                                # F7: only update TID context when the cell IS a TID label
                                # (starts with "TID "); do NOT match "DTID" in concept names
                                if re.match(r'^TID\s+', candidate, re.IGNORECASE):
                                    tid_candidate = extract_tid(candidate)
                                    if tid_candidate:
                                        context_template_id = tid_candidate
                                        context_template_name = candidate

                            row_dict["_source_page"] = page_num
                            row_dict["_source_mado_url"] = mado_page_url(pdf_url, page_num)
                            row_dict["_source_snippet"] = normalize_text(" | ".join(str(c) for c in row_data if c is not None))
                            row_dict["_row_index"] = str(row_idx)
                            row_dict["_context_module_name"] = context_module_name
                            row_dict["_context_template_name"] = context_template_name
                            row_dict["_context_template_id"] = context_template_id

                            # Classify row as module or template
                            if table_type == "template" or is_template_row(row_dict):
                                # For fragmented/unknown-type tables whose rows look like
                                # template data, inject the cross-page TID context so that
                                # standardize_templates can assign Template ID correctly.
                                if table_type == "unknown" and cross_page_template_id:
                                    row_dict["_context_template_id"] = cross_page_template_id
                                    row_dict["_context_template_name"] = cross_page_template_name
                                templates.append(row_dict)
                                if verbose:
                                    logger.debug(f"    Row {row_idx}: TEMPLATE")
                            else:
                                modules.append(row_dict)
                                if verbose:
                                    logger.debug(f"    Row {row_idx}: MODULE")

                            rows_processed += 1
                        except Exception as e:
                            if verbose:
                                logger.warning(f"    Row {row_idx} parse error: {e}")
                            continue

    except Exception as e:
        logger.error(f"✗ Error reading PDF: {e}")
        return [], []

    logger.info(f"✓ Extracted {rows_processed} rows: "
                f"{len(modules)} modules, {len(templates)} templates")
    return modules, templates


def parse_table_row(header: List[str], row_data: List) -> Optional[Dict[str, str]]:
    """
    Parse a single table row into a dictionary.

    Args:
        header: List of column headers
        row_data: List of cell values for this row

    Returns:
        Dictionary mapping header to normalized cell values, or None if invalid
    """
    if not row_data or not any(str(cell).strip() for cell in row_data):
        return None

    row_dict = {}
    for idx, header_name in enumerate(header):
        if idx < len(row_data):
            cell = row_data[idx]
            row_dict[header_name] = normalize_text("" if cell is None else str(cell))
        else:
            row_dict[header_name] = ""

    # Discard rows that are all empty
    if not any(row_dict.values()):
        return None

    return row_dict


def value_from_keys(raw: Dict[str, Any], keys: List[str]) -> str:
    for k, v in raw.items():
        # Skip internal metadata fields added by the parser
        if k.startswith('_'):
            continue
        lk = k.lower()
        if any(key in lk for key in keys):
            return normalize_text(str(v))
    return ""


def standardize_modules(raw_modules: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    standardized: List[Dict[str, str]] = []
    last_attribute_row: Optional[Dict[str, str]] = None
    for raw in raw_modules:
        row = {col: "" for col in MODULE_COLUMNS}
        context_module = parse_module_name_from_context(str(raw.get("_context_module_name", "")))
        # Prefer explicit "Module Name" key, then the "Attributes from Table…" key, then context
        row["Module Name"] = (
            value_from_keys(raw, ["module name", "iod module"])
            or context_module
        )
        # With proper two-row headers, "Attribute Name" key is now available directly
        row["Attribute Name"] = value_from_keys(raw, ["attribute name", "attribute", "name", "element"])
        source_text = " ".join(str(v) for v in raw.values())
        snippet = normalize_text(str(raw.get("_source_snippet", "")))
        tokens = [normalize_text(t) for t in snippet.split("|") if normalize_text(t)]
        if not row["Attribute Name"] and tokens:
            first = tokens[0]
            if first not in ["R", "RC", "Usage"] and "module" not in first.lower():
                row["Attribute Name"] = first
        if row["Attribute Name"].startswith(">"):
            row["Attribute Name"] = row["Attribute Name"].lstrip(">").strip()
        # Tag: prefer explicit column, then regex fallback
        raw_tag = value_from_keys(raw, ["tag"]) or (extract_dicom_tag(source_text) or "")
        # Normalize tag: remove spaces introduced by PDF line-wrap
        # e.g. '(004 0,0032)' → '(0040,0032)'
        if raw_tag:
            cleaned_tag = re.sub(r'\s+', '', raw_tag)
            normalized = extract_dicom_tag(cleaned_tag)
            row["Tag"] = normalized if normalized else raw_tag
        else:
            row["Tag"] = ""
        row["Optionality/Cardinality"] = value_from_keys(raw, ["vm", "cardinality", "optionality"])
        # IHE Usage: prefer explicit column key, then token scan
        row["IHE Usage"] = value_from_keys(raw, ["ihe usage", "ihe", "usage"])
        if not row["IHE Usage"]:
            for t in tokens:
                if t in ["R", "RC", "R+", "RC+", "O", "O+", "Usage"]:
                    row["IHE Usage"] = t
                    break
        # Type: prefer explicit column, then derive from IHE Usage mapping (most
        # reliable for MADO tables which have no explicit Type column), then fall
        # back to regex on row text only.  Do NOT run extract_dicom_type on the
        # full source_text because that includes _row_index numbers (3, 4, …) that
        # the regex `\b(1C|2C|1|2|3)\b` would incorrectly match as DICOM types.
        row["Type"] = value_from_keys(raw, ["type"])
        if not row["Type"] and row["IHE Usage"]:
            usage_map = {
                "R": "1",
                "R+": "1",
                "RC": "1C",
                "RC+": "1C",
                "O": "3",
                "O+": "3",
            }
            row["Type"] = usage_map.get(row["IHE Usage"], "")
        # Last resort: extract type code from row snippet tokens or text
        if not row["Type"]:
            for t in tokens:
                if t in ["1", "1C", "2", "2C", "3"]:
                    row["Type"] = t
                    break
        if not row["Type"]:
            row["Type"] = extract_dicom_type(snippet)
        row["Attribute Description"] = value_from_keys(raw, ["attribute description", "description", "meaning", "definition", "purpose"])
        if not row["Attribute Description"] and len(tokens) >= 2:
            row["Attribute Description"] = tokens[-1]
        row["DICOM Section URL"] = value_from_keys(raw, ["dicom", "url", "section"]) or dicom_module_url(row["Module Name"])
        row["MADO Page URL"] = normalize_text(str(raw.get("_source_mado_url", "")))
        row["DICOM Difference Note"] = ""

        if not row["Attribute Name"] and row["Module Name"]:
            row["Attribute Name"] = value_from_keys(raw, ["keyword", "field", "data element"])

        # Skip obvious table headers and narrative marker rows.
        attr_lower = row["Attribute Name"].lower()
        if (
            attr_lower in {"attribute name", "ihe", "usage", "ihe usage", "keyword:", "fhir keyword:", "context group id:"}
            or attr_lower.startswith("attributes from table")
            or attr_lower.startswith("table 6.x")
            or attr_lower.startswith("include table")
        ):
            continue

        # Skip rows that look like format-code table content (no DICOM tag)
        if not row["Tag"] and re.match(r'^[\d.]+(\s*\(|\|)', row["Attribute Name"]):
            continue

        # Skip description fragments and non-attribute rows that pdfplumber
        # places in the Attribute Name column due to layout overflow.
        # These include: lowercase-starting prose, section references, vocabulary
        # entries like 'UID:' / 'Version:', and URN patterns.
        is_fragment = bool(
            (row["Attribute Name"] and row["Attribute Name"][0].islower())
            or attr_lower.startswith("see ")
            or attr_lower.startswith("one or more items")
            or attr_lower.endswith(":")
            or attr_lower.startswith("[")
        )
        if is_fragment and not row["Tag"]:
            if last_attribute_row is not None:
                desc_text = row["Attribute Name"]
                prev_desc = normalize_text(last_attribute_row.get("Attribute Description", ""))
                last_attribute_row["Attribute Description"] = f"{prev_desc} {desc_text}".strip()
            continue

        # Continuation lines: rows with empty attribute name, tag, AND type.
        # These are description overflow rows from the previous data row.
        if (
            not row["Attribute Name"]
            and not row["Tag"]
            and not row["Type"]
            and last_attribute_row is not None
            and last_attribute_row.get("MADO Page URL") == row["MADO Page URL"]
        ):
            # Collect any description text available in this continuation row
            desc_candidate = row["Attribute Description"]
            if not desc_candidate:
                # Also scan tokens for description fragments
                for t in tokens:
                    if (t and t not in {row["IHE Usage"], "R", "R+", "RC", "RC+", "O", "O+"}
                            and len(t) > 2):
                        desc_candidate = t
                        break
            if desc_candidate:
                prev_desc = normalize_text(last_attribute_row.get("Attribute Description", ""))
                last_attribute_row["Attribute Description"] = f"{prev_desc} {desc_candidate}".strip()
            continue

        standardized.append(row)
        if row["Attribute Name"]:
            last_attribute_row = row
    return standardized


def standardize_templates(raw_templates: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    standardized: List[Dict[str, str]] = []
    for raw in raw_templates:
        row = {col: "" for col in TEMPLATE_COLUMNS}
        source_text = " ".join(str(v) for v in raw.values())
        row["Template Name"] = value_from_keys(raw, ["template name", "template", "document title"]) or normalize_text(str(raw.get("_context_template_name", "")))
        row["Template ID"] = normalize_tid(value_from_keys(raw, ["template id", "tid"]) or (extract_tid(source_text) or normalize_text(str(raw.get("_context_template_id", "")))) )
        row["No"] = value_from_keys(raw, ["no", "item no"])
        row["NL"] = value_from_keys(raw, ["nl", "nesting"])
        row["REL with Parent"] = value_from_keys(raw, ["rel with parent", "relationship"])
        row["VT"] = value_from_keys(raw, ["vt", "value type"])
        row["Concept Name"] = value_from_keys(raw, ["concept name", "name", "code meaning"])
        row["Concept URL"] = value_from_keys(raw, ["concept url", "code url", "link"]) or dicom_concept_url(row["Concept Name"])
        row["VM"] = value_from_keys(raw, ["vm", "multiplicity"]) or extract_vm(source_text)
        row["Req Type (DICOM)"] = value_from_keys(raw, ["req type (dicom)", "dicom req", "type"])
        row["Req Type (IHE)"] = value_from_keys(raw, ["req type (ihe)", "ihe req", "ihe usage"])
        row["Condition"] = value_from_keys(raw, ["condition", "if"])
        row["ValueSet Constraint"] = value_from_keys(raw, ["valueset", "value set", "constraint", "code"]) 
        row["DICOM Section URL"] = value_from_keys(raw, ["dicom", "url", "section"]) or dicom_template_url(row["Template ID"])
        row["MADO Page URL"] = normalize_text(str(raw.get("_source_mado_url", "")))
        row["DICOM Difference Note"] = ""
        # 16XX is a MADO-specific wildcard covering the entire TID 1600 series;
        # it does not map directly to a single DICOM standard template.
        if row["Template ID"] == "16XX":
            row["DICOM Difference Note"] = "16XX is a MADO wildcard covering TID 1600-1699"

        snippet = normalize_text(str(raw.get("_source_snippet", "")))
        tokens = [normalize_text(t) for t in snippet.split("|") if normalize_text(t)]

        if len(tokens) >= 1 and not row["REL with Parent"]:
            if tokens[0] in ["HAS ACQ CONTEXT", "CONTAINS", "HAS PROPERTIES", "INFERRED FROM", "SELECTED FROM", "INCLUDE"]:
                row["REL with Parent"] = tokens[0]
        if len(tokens) >= 2 and not row["VT"]:
            if tokens[1] in ["CODE", "TEXT", "NUM", "UIDREF", "DATE", "TIME", "INCLUDE"]:
                row["VT"] = tokens[1]
        if len(tokens) >= 3 and not row["Concept Name"]:
            row["Concept Name"] = tokens[2]
        if len(tokens) >= 4 and not row["VM"]:
            row["VM"] = tokens[3]
        if len(tokens) >= 5 and not row["Req Type (IHE)"]:
            row["Req Type (IHE)"] = tokens[4]
        if len(tokens) >= 6 and not row["Condition"]:
            row["Condition"] = tokens[5]
        if len(tokens) >= 7 and not row["ValueSet Constraint"]:
            row["ValueSet Constraint"] = tokens[6]

        if not row["No"]:
            row["No"] = normalize_text(str(raw.get("_row_index", "")))
        if not row["Template Name"] and row["Template ID"]:
            row["Template Name"] = f"TID {row['Template ID']}"
        if not row["Template Name"]:
            row["Template Name"] = value_from_keys(raw, ["title", "row", "concept"])
        if not row["Concept Name"]:
            row["Concept Name"] = row["Template Name"]

        # F6: repair truncated Concept Name values at PDF page boundaries
        if row["Concept Name"].endswith(","):
            repair_key = (row["Template ID"], row["Concept Name"])
            if repair_key in CONCEPT_NAME_REPAIRS:
                row["Concept Name"] = CONCEPT_NAME_REPAIRS[repair_key]

        # F2: flag provisional DCM codes in the CP-2595 range (131xxx)
        if re.search(r'\b(131[0-9]{3})\b', row["Concept Name"]):
            flag = ("PDF uses provisional DCM code (CP-2595); "
                    "MADO spec may use 99IHE MADOTEMP interim code")
            note = row["DICOM Difference Note"]
            row["DICOM Difference Note"] = f"{note}; {flag}".strip("; ") if note else flag

        # F4: move DCID/CID value-set references out of Condition into ValueSet Constraint
        if (
            (row["Condition"].startswith("DCID ") or row["Condition"].startswith("CID "))
            and not row["ValueSet Constraint"]
        ):
            row["ValueSet Constraint"] = row["Condition"]
            row["Condition"] = ""

        # F5: reject VM values that look like 6-digit concept code artifacts
        if row["VM"] and not re.match(r'^\d{1,3}(-\d{1,3})?$|^\d+-n$|^1-n$', row["VM"]):
            row["VM"] = "1"

        standardized.append(row)

    # F8: merge ValueSet-only continuation rows into the preceding row.
    # A row is a continuation when its two structural anchor fields (REL with Parent and VT)
    # are both empty AND Concept Name is absent or only set via the Template Name fallback.
    # This handles PDF rows like "| | | | | | 6.X.6.4.1 Value Set ..." where extract_vm()
    # may have grabbed a digit from the section number; we do not require VM to be empty.
    merged: List[Dict[str, str]] = []
    for row in standardized:
        cn = normalize_text(row.get("Concept Name", ""))
        cn_is_fallback = cn and (cn == normalize_text(row.get("Template Name", "")))
        is_continuation = (
            not normalize_text(row.get("REL with Parent", ""))
            and not normalize_text(row.get("VT", ""))
            and (not cn or cn_is_fallback)
            and bool(normalize_text(row.get("ValueSet Constraint", "")))
        )
        if is_continuation and merged:
            prev = merged[-1]
            existing = normalize_text(prev.get("ValueSet Constraint", ""))
            addition = normalize_text(row.get("ValueSet Constraint", ""))
            prev["ValueSet Constraint"] = f"{existing} {addition}".strip()
        else:
            merged.append(row)
    standardized = merged

    # F3: renumber No sequentially within each TID group
    tid_counters: Dict[str, int] = defaultdict(int)
    for row in standardized:
        tid = row.get("Template ID", "")
        tid_counters[tid] += 1
        row["No"] = str(tid_counters[tid])

    return standardized


def split_review_rows(
    rows: List[Dict[str, str]],
    required_columns: List[str],
    source_key: str,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    accepted: List[Dict[str, str]] = []
    review: List[Dict[str, str]] = []
    for row in rows:
        missing = [c for c in required_columns if not normalize_text(row.get(c, ""))]
        if missing:
            review_row = dict(row)
            review_row["Missing Fields"] = "; ".join(missing)
            review_row["Parse Notes"] = "Missing required fields"
            review_row["Source Snippet"] = row.get(source_key, "")
            review_row["Source Page"] = row.get("MADO Page URL", "")
            review.append(review_row)
        else:
            accepted.append(row)
    return accepted, review


def validate_urls(rows: List[Dict[str, str]], url_columns: List[str]) -> Dict[str, int]:
    failures = 0
    checks = 0
    for row in rows:
        failed_cols = []
        for col in url_columns:
            url = normalize_text(row.get(col, ""))
            if not url:
                continue
            checks += 1
            if not is_url_reachable(url):
                failures += 1
                failed_cols.append(col)
        if failed_cols:
            note = row.get("DICOM Difference Note", "")
            suffix = f"URL check failed: {', '.join(failed_cols)}"
            row["DICOM Difference Note"] = f"{note}; {suffix}".strip("; ")
    return {"checks": checks, "failures": failures}


def dedupe_rows(rows: List[Dict[str, str]], key_columns: List[str]) -> Tuple[List[Dict[str, str]], int]:
    seen = set()
    deduped: List[Dict[str, str]] = []
    dupes = 0
    for row in rows:
        key = tuple(normalize_text(row.get(c, "")) for c in key_columns)
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        deduped.append(row)
    return deduped, dupes


def write_summary(path: str, data: Dict[str, Any]) -> bool:
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"✓ Wrote summary to {path}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to write summary: {e}")
        return False


def write_csv(filepath: str, data: List[Dict], fieldnames: List[str]) -> bool:
    """
    Write data to CSV file.

    Args:
        filepath: Output CSV file path
        data: List of dictionaries to write
        fieldnames: CSV column headers

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"✓ Wrote {len(data)} rows to {filepath}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to write CSV: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract DICOM modules and templates from IHE MADO PDF Volume 3"
    )
    parser.add_argument(
        "--pdf-url", default=DEFAULT_PDF_URL,
        help="Custom PDF URL"
    )
    parser.add_argument(
        "--output-dir", default=DEFAULT_OUTPUT_DIR,
        help="Output directory for CSV files"
    )
    parser.add_argument(
        "--modules-file", default=DEFAULT_MODULES_FILE,
        help="Modules CSV filename"
    )
    parser.add_argument(
        "--templates-file", default=DEFAULT_TEMPLATES_FILE,
        help="Templates CSV filename"
    )
    parser.add_argument(
        "--pdf-path", default=None,
        help="Use a local PDF file directly (skips download and cache lookup)"
    )
    parser.add_argument(
        "--no-download", action="store_true",
        help="Use cached PDF only"
    )
    parser.add_argument("--modules-review-file", default=DEFAULT_MODULES_REVIEW_FILE, help="Modules manual-review CSV filename")
    parser.add_argument("--templates-review-file", default=DEFAULT_TEMPLATES_REVIEW_FILE, help="Templates manual-review CSV filename")
    parser.add_argument("--summary-file", default=DEFAULT_SUMMARY_FILE, help="Run summary JSON filename")
    parser.add_argument("--skip-url-check", action="store_true", help="Skip online URL reachability checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("=== DICOM Tables Extraction ===")
    logger.info(f"Output directory: {args.output_dir}")

    # Check dependencies
    if not ensure_dependencies():
        return 1

    # Resolve PDF path
    if args.pdf_path:
        if not os.path.exists(args.pdf_path):
            logger.error(f"✗ Specified PDF not found: {args.pdf_path}")
            return 1
        pdf_path = args.pdf_path
        size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        logger.info(f"✓ Using local PDF: {pdf_path} ({size_mb:.1f} MB)")
    else:
        # Download PDF
        if args.no_download and not os.path.exists(PDF_CACHE_FILE):
            logger.error("✗ Cached PDF not found and --no-download specified")
            return 1
        force_dl = not args.no_download
        if not download_pdf(args.pdf_url, PDF_CACHE_FILE, force_redownload=force_dl):
            logger.error("✗ Could not obtain PDF")
            return 1
        pdf_path = PDF_CACHE_FILE

    # Extract tables
    modules, templates = parse_pdf_tables(pdf_path, args.pdf_url, verbose=args.verbose)

    if not modules and not templates:
        logger.warning("⚠ No tables extracted from PDF")
        logger.info("Hint: PDF table structure may differ from expected format")
        logger.info("     Create CSVs manually or inspect PDF with: pdfplumber .cache/IHE_RAD_Suppl_MADO.pdf")
        # Still create empty CSVs with headers to avoid downstream errors
        modules = []
        templates = []

    # Standardize to target schema
    std_modules = standardize_modules(modules)
    std_templates = standardize_templates(templates)

    # Attach source snippets for manual-review queues
    for i, raw in enumerate(modules[: len(std_modules)]):
        std_modules[i]["_source_snippet"] = normalize_text(str(raw.get("_source_snippet", "")))
    for i, raw in enumerate(templates[: len(std_templates)]):
        std_templates[i]["_source_snippet"] = normalize_text(str(raw.get("_source_snippet", "")))

    accepted_modules, review_modules = split_review_rows(std_modules, MODULE_REQUIRED, "_source_snippet")
    accepted_templates, review_templates = split_review_rows(std_templates, TEMPLATE_REQUIRED, "_source_snippet")

    accepted_modules, module_dupes = dedupe_rows(
        accepted_modules,
        ["Module Name", "Attribute Name", "Tag", "MADO Page URL"],
    )
    accepted_templates, template_dupes = dedupe_rows(
        accepted_templates,
        ["Template ID", "No", "Concept Name", "MADO Page URL"],
    )

    url_stats = {"modules": {"checks": 0, "failures": 0}, "templates": {"checks": 0, "failures": 0}}
    if not args.skip_url_check:
        url_stats["modules"] = validate_urls(accepted_modules, ["DICOM Section URL", "MADO Page URL"])
        url_stats["templates"] = validate_urls(accepted_templates, ["DICOM Section URL", "Concept URL", "MADO Page URL"])

    # Sort output
    accepted_modules.sort(key=lambda x: (x["Module Name"], x["Attribute Name"], x["Tag"], x["MADO Page URL"]))
    accepted_templates.sort(key=lambda x: (x["Template ID"], x["No"], x["Concept Name"], x["MADO Page URL"]))
    review_modules.sort(key=lambda x: (x.get("Module Name", ""), x.get("Attribute Name", "")))
    review_templates.sort(key=lambda x: (x.get("Template ID", ""), x.get("No", "")))

    # Write CSVs
    modules_path = os.path.join(args.output_dir, args.modules_file)
    templates_path = os.path.join(args.output_dir, args.templates_file)
    modules_review_path = os.path.join(args.output_dir, args.modules_review_file)
    templates_review_path = os.path.join(args.output_dir, args.templates_review_file)
    summary_path = os.path.join(args.output_dir, args.summary_file)

    success = True
    success &= write_csv(
        modules_path,
        accepted_modules,
        MODULE_COLUMNS,
    )
    success &= write_csv(
        templates_path,
        accepted_templates,
        TEMPLATE_COLUMNS,
    )
    success &= write_csv(
        modules_review_path,
        review_modules,
        MODULE_COLUMNS + REVIEW_EXTRA_COLUMNS,
    )
    success &= write_csv(
        templates_review_path,
        review_templates,
        TEMPLATE_COLUMNS + REVIEW_EXTRA_COLUMNS,
    )
    success &= write_summary(
        summary_path,
        {
            "modules": {
                "accepted": len(accepted_modules),
                "review": len(review_modules),
                "duplicates_removed": module_dupes,
                "url_checks": url_stats["modules"],
            },
            "templates": {
                "accepted": len(accepted_templates),
                "review": len(review_templates),
                "duplicates_removed": template_dupes,
                "url_checks": url_stats["templates"],
            },
            "skip_url_check": args.skip_url_check,
            "source": {
                "pdf_url": args.pdf_url,
                "volume3_page_range": [MADO_VOLUME3_PAGE_MIN, MADO_VOLUME3_PAGE_MAX],
            },
        },
    )

    if success:
        logger.info("✓ Extraction complete")
        logger.info(f"  Modules accepted: {len(accepted_modules)}; review: {len(review_modules)}")
        logger.info(f"  Templates accepted: {len(accepted_templates)}; review: {len(review_templates)}")
        return 0
    else:
        logger.error("✗ Extraction incomplete due to errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
