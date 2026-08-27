#!/usr/bin/env python3
"""
dicom-module-crosscheck.py

For each DICOM module referenced in IHE MADO Table 6.X.2.4-1:
  1. Fetch the authoritative DICOM attribute list from dicom.nema.org PS3.3
     (with local caching in .cache/dicom-ps3/).
  2. Extract MADO-specified fields from the cached IHE MADO PDF.
  3. Cross-check and write:
       ai-result/step10-dicom-module-field-crosscheck.csv

Output columns:
  Module, DICOM Reference, Attribute Name, Tag,
  DICOM Type, MADO IHE Usage,
  in_dicom, in_mado, difference_type,
  DICOM Description, MADO Description

difference_type values:
  both          – attribute present in both DICOM spec and MADO
  dicom_only    – in DICOM, not mentioned in MADO
  mado_only     – mentioned in MADO as IHE extension, not in base DICOM module
  mado_override – in both, but MADO changes requirement level vs DICOM
"""

import csv
import html.parser
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import urlopen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ── paths ──────────────────────────────────────────────────────────────────────
PDF_PATH = Path(".cache/IHE_RAD_Suppl_MADO.pdf")
DICOM_CACHE = Path(".cache/dicom-ps3")
OUTPUT = Path("ai-result/step10-dicom-module-field-crosscheck.csv")
DICOM_BASE = "https://dicom.nema.org/medical/dicom/current/output/chtml/part03/"

# ── MADO module catalogue ──────────────────────────────────────────────────────
# mado_pages: 1-based PDF page numbers that contain MADO attribute tables for
#             this module (including any macro sub-tables referenced inline).
# Page mapping derived from Table 6.X.2.4-1 and PDF text scan.
# table_patterns: regex patterns (case-insensitive) matched against the
# 'Attributes from Table …' title row of each PDF attribute table.  Only tables
# whose title matches at least one pattern are included for that module.  This
# prevents tables from an adjacent module on the same page from leaking in.
MADO_MODULES: List[Dict] = [
    {
        "name": "Patient",
        "dicom_ref": "C.7.1.1",
        "mado_pages": list(range(43, 46)),
        "table_patterns": [
            r"patient module",
            r"issuer of patient id macro",
        ],
    },
    {
        "name": "General Study",
        "dicom_ref": "C.7.2.1",
        "mado_pages": list(range(45, 47)),
        "table_patterns": [
            r"general study module",
            r"hl7v2 hierarchic designator macro",
        ],
    },
    {
        "name": "Key Object Document Series",
        "dicom_ref": "C.17.6.1",
        "mado_pages": [],
        "table_patterns": [
            r"key object document series",
        ],
    },
    {
        "name": "General Equipment",
        "dicom_ref": "C.7.5.1",
        "mado_pages": list(range(46, 48)),
        "table_patterns": [
            r"general equipment module",
        ],
    },
    {
        "name": "Key Object Document",
        "dicom_ref": "C.17.6.2",
        "mado_pages": list(range(47, 50)),
        "table_patterns": [
            r"key object document module",
            r"referenced request macro",
        ],
    },
    {
        "name": "SR Document Content",
        "dicom_ref": "C.17.3",
        "mado_pages": [],
        "table_patterns": [],
    },
    {
        "name": "SOP Common",
        "dicom_ref": "C.12.1",
        "mado_pages": list(range(54, 57)),
        "table_patterns": [
            r"sop common module",
            r"hl7v2 hierarchic designator macro",
            r"hierarchical series reference macro",
            r"hierarchical sop instance reference macro",
        ],
    },
]

OUTPUT_COLS = [
    "Module",
    "DICOM Reference",
    "Attribute Name",
    "Tag",
    "DICOM Type",
    "MADO IHE Usage",
    "in_dicom",
    "in_mado",
    "difference_type",
    "DICOM Description",
    "MADO Description",
]

# MADO includes macro attributes that are not returned by the module section
# lookup. Keep their normative DICOM types explicit so the generated KOS table
# does not lose them during the DICOM/MADO merge.
MADO_ONLY_DICOM_TYPES = {
    ("Patient", "An identifier for the Patient", "(0010,0020)"): "1",
    ("Patient", "Issuer of Patient ID", "(0010,0021)"): "3",
    ("Patient", "Issuer of Patient ID Qualifiers Sequence", "(0010,0024)"): "1",
    ("Patient", "Universal Entity ID", "(0040,0032)"): "1",
    ("Patient", "Universal Entity ID Type", "(0040,0033)"): "1C",
    ("SOP Common", "Universal Entity ID", "(0010,0032)"): "1",
    ("SOP Common", "Universal Entity ID Type", "(0010,0033)"): "1C",
}

# ── DICOM PS3.3 HTML fetcher and parser ────────────────────────────────────────

class _SectionTableParser(html.parser.HTMLParser):
    """Extract the first attribute table that follows a target section heading."""

    _ATTR_HEADER_WORDS = {"attribute name", "attribute", "tag", "type"}

    def __init__(self, section_id: str) -> None:
        super().__init__()
        self._target = section_id       # e.g. "sect_C.7.1.1"
        self._in_section = False
        self._in_table = False
        self._done = False
        self._header: List[str] = []
        self._rows: List[List[str]] = []
        self._in_row = False
        self._in_cell = False
        self._cur_row: List[str] = []
        self._cur_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if self._done:
            return
        d = dict(attrs)
        # Detect the target section by its id attribute
        if not self._in_table:
            if d.get("id") == self._target:
                self._in_section = True
            elif (
                self._in_section
                and d.get("id", "").startswith("sect_")
                and d.get("id") != self._target
            ):
                # Another section started → stop looking
                self._in_section = False
            if self._in_section and tag == "table":
                self._in_table = True
        if self._in_table:
            if tag == "tr":
                self._in_row = True
                self._cur_row = []
            if tag in ("td", "th"):
                self._in_cell = True
                self._cur_parts = []

    def handle_endtag(self, tag: str) -> None:
        if self._done:
            return
        if self._in_table:
            if self._in_cell and tag in ("td", "th"):
                self._in_cell = False
                self._cur_row.append(
                    re.sub(r"\s+", " ", "".join(self._cur_parts)).strip()
                )
            if self._in_row and tag == "tr":
                self._in_row = False
                row = self._cur_row
                if not self._header:
                    joined = " ".join(row).lower()
                    if any(w in joined for w in self._ATTR_HEADER_WORDS):
                        self._header = row
                elif self._header and any(row):
                    self._rows.append(row)
            if tag == "table":
                self._done = True

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cur_parts.append(data)

    @property
    def result(self) -> Tuple[List[str], List[List[str]]]:
        return self._header, self._rows


def _fetch_section_html(ref: str) -> Optional[str]:
    """Download and cache DICOM PS3.3 HTML for a section reference.

    Tries candidate filenames from most-specific to least-specific, e.g.
    for ref="C.7.1.1": sect_C.7.1.1.html → sect_C.7.1.html → sect_C.7.html
    """
    DICOM_CACHE.mkdir(parents=True, exist_ok=True)
    parts = ref.split(".")
    for n in range(len(parts), 1, -1):
        fname = "sect_" + ".".join(parts[:n]) + ".html"
        path = DICOM_CACHE / fname
        if path.exists():
            log.info(f"  cache: {fname}")
            return path.read_text(encoding="utf-8", errors="replace")
        url = DICOM_BASE + fname
        log.info(f"  GET {url}")
        try:
            with urlopen(url, timeout=20) as r:
                body = r.read().decode("utf-8", errors="replace")
            path.write_text(body, encoding="utf-8")
            log.info(f"  saved {fname} ({len(body) // 1024} KB)")
            return body
        except Exception as exc:
            log.debug(f"  {fname}: {exc}")
    return None


def _normalize_tag(tag: str) -> str:
    m = re.search(r"\(\s*([0-9A-Fa-f]{2,4})\s*,\s*([0-9A-Fa-f]{2,4})\s*\)", tag)
    if m:
        return f"({m.group(1).upper().zfill(4)},{m.group(2).upper().zfill(4)})"
    return tag.strip()


def get_dicom_fields(ref: str) -> List[Dict]:
    """Return list of {attr, tag, type, description} from DICOM PS3.3 HTML."""
    html_text = _fetch_section_html(ref)
    if not html_text:
        log.warning(f"  No HTML found for {ref}")
        return []

    parser = _SectionTableParser("sect_" + ref)
    parser.feed(html_text)
    header, rows = parser.result

    if not rows:
        log.warning(f"  No table parsed for {ref} (header={header})")
        return []

    hl = [h.lower() for h in header]

    def col_idx(keywords: List[str]) -> Optional[int]:
        for i, h in enumerate(hl):
            if any(k in h for k in keywords):
                return i
        return None

    attr_i = col_idx(["attribute name", "name"]) or 0
    tag_i = col_idx(["tag"])
    type_i = col_idx(["type"])
    desc_i = col_idx(["description"])

    def cell(row: List[str], idx: Optional[int]) -> str:
        if idx is None or idx >= len(row):
            return ""
        return re.sub(r"\s+", " ", row[idx]).strip()

    fields = []
    for row in rows:
        attr = cell(row, attr_i)
        tag = _normalize_tag(cell(row, tag_i) if tag_i is not None else "")
        typ = cell(row, type_i) if type_i is not None else ""
        desc = cell(row, desc_i) if desc_i is not None else ""

        if not attr and not tag:
            continue
        # Skip macro-include rows — they are handled when we process the macro's own section
        if re.match(r"^\s*>?\s*include\b", attr, re.IGNORECASE):
            continue

        fields.append({"attr": attr, "tag": tag, "type": typ, "description": desc})

    log.info(f"  {ref}: {len(fields)} DICOM fields from PS3.3")
    return fields


# ── MADO PDF field extractor ───────────────────────────────────────────────────

_NOISE_ROW = re.compile(
    r"^(>?\s*include\b|attributes from\b|attribute name$|ihe usage$|ihe$|usage$"
    r"|keyword:\s*$|fhir keyword:\s*$|context group id:\s*$|table 6\.x)",
    re.IGNORECASE,
)

_IHE_USAGE_TOKENS = {"R", "R+", "RC", "RC+", "O", "O+", "RO"}


def get_mado_fields(
    module_name: str,
    pages: List[int],
    table_patterns: Optional[List[str]] = None,
) -> List[Dict]:
    """Extract MADO-listed attribute rows for a module from the IHE MADO PDF.

    table_patterns: if provided, only process tables whose 'Attributes from
    Table …' title row matches at least one pattern (case-insensitive).  This
    prevents tables from an adjacent module on the same page from being
    included under the wrong module.
    """
    if not pages:
        return []
    try:
        import pdfplumber
    except ImportError:
        log.error("pdfplumber not installed")
        return []

    raw: List[Dict] = []

    with pdfplumber.open(str(PDF_PATH)) as pdf:
        for pg in pages:
            if pg < 1 or pg > len(pdf.pages):
                continue
            for tbl in pdf.pages[pg - 1].extract_tables() or []:
                if not tbl or len(tbl) < 2:
                    continue

                # MADO attribute tables have a two-row header structure:
                #   row 0: table title  e.g. "Attributes from Table C.7-1 Patient Module"
                #   row 1: column header e.g. "Attribute Name | Tag | IHE Usage | ..."
                # Detect a title row: only 1 non-None/non-empty cell, OR first
                # cell matches the "Attributes from Table" pattern.
                def _nonempty_cells(row: list) -> List[str]:
                    return [
                        str(c).strip()
                        for c in row
                        if c is not None and str(c).strip() not in ("", "NULL", "None")
                    ]

                first_nonempty = _nonempty_cells(tbl[0])
                is_title_row = (
                    len(first_nonempty) == 1
                    or (
                        first_nonempty
                        and re.match(
                            r"attributes\s+from\s+table",
                            first_nonempty[0],
                            re.IGNORECASE,
                        )
                    )
                )

                # Filter by table title when patterns are specified
                if is_title_row and table_patterns:
                    title = first_nonempty[0].lower() if first_nonempty else ""
                    if not any(
                        re.search(pat, title, re.IGNORECASE)
                        for pat in table_patterns
                    ):
                        continue  # table belongs to a different module

                header_row_idx = 1 if (is_title_row and len(tbl) >= 3) else 0
                data_start = header_row_idx + 1

                header = [
                    re.sub(r"\s+", " ", (str(c) if c is not None else "")).strip()
                    for c in tbl[header_row_idx]
                ]
                hl = [h.lower() for h in header]

                def col(kws: List[str]) -> Optional[int]:
                    for i, h in enumerate(hl):
                        if any(k in h for k in kws):
                            return i
                    return None

                # Skip tables that have no attribute name column
                attr_i = col(["attribute name", "attribute"])
                if attr_i is None:
                    continue

                # Skip module-summary tables (IE/Module/Reference/Usage shape)
                if col(["ie"]) is not None and col(["reference"]) is not None:
                    continue

                # Skip TID/SR template tables
                if col(["rel with", "vt", "concept name"]) is not None:
                    continue

                tag_i = col(["tag"])
                ihe_i = col(["ihe", "usage"])
                desc_i = col(["description"])

                # The PDF sometimes places the description text one column to the
                # right of the "Attribute Description" header due to cell merging.
                # Build a set of candidate description column indices.
                desc_candidates: List[int] = []
                if desc_i is not None:
                    desc_candidates.append(desc_i)
                    if desc_i + 1 < len(tbl[header_row_idx]):
                        desc_candidates.append(desc_i + 1)
                else:
                    # Fall back: use last two non-tag/ihe columns
                    used = {i for i in [attr_i, tag_i, ihe_i] if i is not None}
                    desc_candidates = [
                        i for i in range(len(tbl[header_row_idx])) if i not in used
                    ][-2:]

                def _desc_from_row(row: list) -> str:
                    parts = []
                    for ci in desc_candidates:
                        if ci < len(row):
                            v = row[ci]
                            s = re.sub(r"\s+", " ", (str(v) if v is not None else "")).strip()
                            if s and s not in ("NULL", "None"):
                                parts.append(s)
                    return " ".join(parts).strip()

                for row in tbl[data_start:]:
                    def cv(idx: Optional[int]) -> str:
                        if idx is None or idx >= len(row):
                            return ""
                        v = row[idx]
                        return re.sub(r"\s+", " ", (str(v) if v is not None else "")).strip()

                    attr = cv(attr_i).lstrip(">").strip()
                    tag = _normalize_tag(cv(tag_i) if tag_i is not None else "")
                    ihe = cv(ihe_i) if ihe_i is not None else ""
                    desc = _desc_from_row(row)

                    # Skip noise rows
                    if _NOISE_ROW.match(attr):
                        continue

                    # Continuation line: only description text, fold into previous
                    if not attr and not tag and desc and raw:
                        raw[-1]["description"] = (
                            raw[-1]["description"] + " " + desc
                        ).strip()
                        continue

                    if not attr and not tag:
                        continue

                    raw.append(
                        {
                            "attr": attr,
                            "tag": tag,
                            "ihe_usage": ihe,
                            "description": desc,
                            "source_page": pg,
                        }
                    )

    # Deduplicate by (normalised attr, tag)
    seen: set = set()
    deduped: List[Dict] = []
    for f in raw:
        key = (f["attr"].lower().strip(), f["tag"])
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    log.info(
        f"  {module_name}: {len(deduped)} MADO fields "
        f"(pages {pages[0]}–{pages[-1]})"
    )
    return deduped


# ── Cross-check logic ──────────────────────────────────────────────────────────

def _norm_attr(s: str) -> str:
    """Normalise attribute name for fuzzy comparison (strip punctuation, lowercase)."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def crosscheck(
    module: Dict,
    dicom_fields: List[Dict],
    mado_fields: List[Dict],
) -> List[Dict]:
    """Produce one output row per unique attribute, merged from both sources."""

    # Index DICOM and MADO fields by tag and by normalised attribute name
    dicom_by_tag: Dict[str, Dict] = {f["tag"]: f for f in dicom_fields if f["tag"]}
    dicom_by_attr: Dict[str, Dict] = {
        _norm_attr(f["attr"]): f for f in dicom_fields if f["attr"]
    }
    mado_by_tag: Dict[str, Dict] = {f["tag"]: f for f in mado_fields if f["tag"]}
    mado_by_attr: Dict[str, Dict] = {
        _norm_attr(f["attr"]): f for f in mado_fields if f["attr"]
    }

    # Determine if requirement levels differ
    _REQUIRED_DICOM = {"1", "1C", "2", "2C"}
    _REQUIRED_MADO = {"R", "R+", "RC", "RC+"}

    def _diff_type(df: Optional[Dict], mf: Optional[Dict]) -> str:
        in_d = bool(df)
        in_m = bool(mf)
        if in_d and in_m:
            dicom_req = (df.get("type", "") or "") in _REQUIRED_DICOM
            mado_req = (mf.get("ihe_usage", "") or "") in _REQUIRED_MADO
            if dicom_req != mado_req:
                return "mado_override"
            return "both"
        if in_d:
            return "dicom_only"
        if in_m:
            return "mado_only"
        return "unknown"

    def _make_row(attr: str, tag: str, df: Optional[Dict], mf: Optional[Dict]) -> Dict:
        type_key = (module["name"], attr, tag)
        dicom_type = (df or {}).get("type", "")
        if not dicom_type:
            dicom_type = MADO_ONLY_DICOM_TYPES.get(type_key, "")
        return {
            "Module": module["name"],
            "DICOM Reference": module["dicom_ref"],
            "Attribute Name": attr or (mf or {}).get("attr") or (df or {}).get("attr", ""),
            "Tag": tag or "",
            "DICOM Type": dicom_type,
            "MADO IHE Usage": (mf or {}).get("ihe_usage", ""),
            "in_dicom": "Y" if df else "",
            "in_mado": "Y" if mf else "",
            "difference_type": _diff_type(df, mf),
            "DICOM Description": (df or {}).get("description", ""),
            "MADO Description": (mf or {}).get("description", ""),
        }

    out_rows: List[Dict] = []
    consumed_mado_tags: set = set()
    consumed_mado_attrs: set = set()

    # Process all DICOM fields first, try to find matching MADO entry
    for df in dicom_fields:
        tag = df["tag"]
        an = _norm_attr(df["attr"])
        mf = mado_by_tag.get(tag) or mado_by_attr.get(an)
        if mf:
            consumed_mado_tags.add(mf.get("tag", ""))
            consumed_mado_attrs.add(_norm_attr(mf.get("attr", "")))
        out_rows.append(_make_row(df["attr"], tag, df, mf))

    # Add MADO-only rows (no match found in DICOM)
    for mf in mado_fields:
        tag = mf["tag"]
        an = _norm_attr(mf["attr"])
        if tag and tag in consumed_mado_tags:
            continue
        if an and an in consumed_mado_attrs:
            continue
        out_rows.append(_make_row(mf["attr"], tag, None, mf))

    return out_rows


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    if not PDF_PATH.exists():
        log.error(f"PDF not found: {PDF_PATH}. Run extraction first.")
        return 1

    all_rows: List[Dict] = []
    stats: Dict[str, Dict] = {}

    for mod in MADO_MODULES:
        name = mod["name"]
        ref = mod["dicom_ref"]
        log.info(f"── {name} ({ref}) ──")

        dicom_f = get_dicom_fields(ref)
        mado_f = get_mado_fields(name, mod["mado_pages"], mod.get("table_patterns"))
        rows = crosscheck(mod, dicom_f, mado_f)
        all_rows.extend(rows)

        counts = {dt: sum(1 for r in rows if r["difference_type"] == dt)
                  for dt in ("both", "dicom_only", "mado_only", "mado_override")}
        stats[name] = {
            "dicom_fields": len(dicom_f),
            "mado_fields": len(mado_f),
            "total_rows": len(rows),
            **counts,
        }
        log.info(
            f"  rows={len(rows)}: "
            f"both={counts['both']}  "
            f"dicom_only={counts['dicom_only']}  "
            f"mado_only={counts['mado_only']}  "
            f"mado_override={counts['mado_override']}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=OUTPUT_COLS)
        w.writeheader()
        w.writerows(all_rows)

    log.info(f"Wrote {len(all_rows)} rows → {OUTPUT}")

    # Print summary table
    print("\n── Cross-Check Summary ───────────────────────────────────────────")
    print(f"{'Module':<30} {'DICOM':>5} {'MADO':>5} {'both':>5} {'D-only':>6} {'M-only':>6} {'overr.':>6}")
    print("─" * 72)
    for name, s in stats.items():
        print(
            f"{name:<30} {s['dicom_fields']:>5} {s['mado_fields']:>5} "
            f"{s['both']:>5} {s['dicom_only']:>6} {s['mado_only']:>6} "
            f"{s['mado_override']:>6}"
        )
    print("─" * 72)
    total_d = sum(s["dicom_fields"] for s in stats.values())
    total_m = sum(s["mado_fields"] for s in stats.values())
    total_b = sum(s["both"] for s in stats.values())
    total_do = sum(s["dicom_only"] for s in stats.values())
    total_mo = sum(s["mado_only"] for s in stats.values())
    total_ov = sum(s["mado_override"] for s in stats.values())
    print(
        f"{'TOTAL':<30} {total_d:>5} {total_m:>5} "
        f"{total_b:>5} {total_do:>6} {total_mo:>6} {total_ov:>6}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
