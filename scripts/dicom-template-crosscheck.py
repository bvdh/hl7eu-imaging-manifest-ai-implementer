#!/usr/bin/env python3
"""
dicom-template-crosscheck.py

For each DICOM SR template (TID) addressed by IHE-MADO Volume 3:
  1. Fetch the authoritative DICOM PS3.16 template node rows from
     dicom.nema.org (with local caching in .cache/dicom-ps16/).
  2. Load IHE-MADO-specified template rows from the already-extracted
     ai-result/step10-dicom-templates.csv.
  3. Cross-check and write one line per unique template node:
       ai-result/step10-dicom-template-cross-check.csv

Output columns:
  Template ID, DICOM TID Name, Row No, NL, REL with Parent, VT,
  Concept Name, VM, Req Type (DICOM), Req Type (IHE),
  Condition (DICOM), Condition (IHE), ValueSet (DICOM), ValueSet (IHE),
  in_dicom, in_ihe_mado, difference_type,
    DICOM Section URL, MADO Page URL, DICOM Difference Note, TID 1602 Context

difference_type values:
  both          – node present in both PS3.16 and IHE-MADO, same requirement
  dicom_only    – in PS3.16, not addressed by IHE-MADO
  mado_only     – addressed by IHE-MADO, no PS3.16 counterpart (e.g. TID 16XX)
  mado_override – in both, but IHE-MADO changes requirement level vs PS3.16

EU-MADO is not a separate source: IHE-MADO is the EU profile here.
"""

import csv
import html.parser
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import urlopen

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── paths ──────────────────────────────────────────────────────────────────────
TEMPLATES_CSV = Path("ai-result/step10-dicom-templates.csv")
OUTPUT = Path("ai-result/step10-dicom-template-cross-check.csv")
DICOM_CACHE = Path(".cache/dicom-ps16")
P16_BASE = "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/"

# ── TID catalogue ────────────────────────────────────────────────────────────
# page:    PS3.16 HTML file holding the TID table.
# anchor:  the table anchor id within that page (table_TID_NNNN).
# mado_id: Template ID value(s) in step10-dicom-templates.csv mapping to this TID.
TID_CATALOGUE: List[Dict] = [
    {"tid": "2010", "name": "Key Object Selection", "page": "sect_TID_2010.html", "anchor": "table_TID_2010", "mado_ids": []},
    {"tid": "1600", "name": "Image Library", "page": "chapter_A.html", "anchor": "table_TID_1600", "mado_ids": ["1600"]},
    {"tid": "1601", "name": "Image Library Entry", "page": "chapter_A.html", "anchor": "table_TID_1601", "mado_ids": []},
    {"tid": "1602", "name": "Image Library Entry Descriptors", "page": "chapter_A.html", "anchor": "table_TID_1602", "mado_ids": ["1602"]},
    {"tid": "1609", "name": "Image Library Entry Descriptors for Key Object Selection", "page": "chapter_A.html", "anchor": "table_TID_1609", "mado_ids": ["16XX"]},
]

OUTPUT_COLS = [
    "Template ID", "DICOM TID Name", "Row No", "NL", "REL with Parent", "VT",
    "Concept Name", "VM", "Req Type (DICOM)", "Req Type (IHE)",
    "Condition (DICOM)", "Condition (IHE)", "ValueSet (DICOM)", "ValueSet (IHE)",
    "in_dicom", "in_ihe_mado", "difference_type",
    "DICOM Section URL", "MADO Page URL", "DICOM Difference Note", "TID 1602 Context", "Field State",
]


# ── DICOM PS3.16 HTML fetcher and parser ────────────────────────────────────────

def _fetch_page(page: str) -> Optional[str]:
    """Download and cache a PS3.16 HTML page."""
    DICOM_CACHE.mkdir(parents=True, exist_ok=True)
    path = DICOM_CACHE / page
    if path.exists():
        log.info(f"  cache: {page}")
        return path.read_text(encoding="utf-8", errors="replace")
    url = P16_BASE + page
    log.info(f"  GET {url}")
    try:
        with urlopen(url, timeout=30) as r:
            body = r.read().decode("utf-8", errors="replace")
        path.write_text(body, encoding="utf-8")
        log.info(f"  saved {page} ({len(body) // 1024} KB)")
        return body
    except Exception as exc:
        log.warning(f"  {page}: {exc}")
        return None


class _AnchoredTableParser(html.parser.HTMLParser):
    """Extract the first <table> that follows a given anchor id."""

    def __init__(self, anchor: str) -> None:
        super().__init__()
        self._anchor = anchor
        self._armed = False
        self._in_table = False
        self._done = False
        self._rows: List[List[str]] = []
        self._in_cell = False
        self._cur_row: List[str] = []
        self._cur_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if self._done:
            return
        d = dict(attrs)
        if not self._in_table:
            if d.get("id") == self._anchor:
                self._armed = True
            if self._armed and tag == "table":
                self._in_table = True
            return
        if tag == "tr":
            self._cur_row = []
        if tag in ("td", "th"):
            self._in_cell = True
            self._cur_parts = []

    def handle_endtag(self, tag: str) -> None:
        if self._done or not self._in_table:
            return
        if self._in_cell and tag in ("td", "th"):
            self._in_cell = False
            self._cur_row.append(re.sub(r"\s+", " ", "".join(self._cur_parts)).strip())
        if tag == "tr":
            if any(self._cur_row):
                self._rows.append(self._cur_row)
        if tag == "table":
            self._done = True

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cur_parts.append(data)

    @property
    def rows(self) -> List[List[str]]:
        return self._rows


def get_dicom_template_rows(tid: Dict) -> List[Dict]:
    """Return PS3.16 node rows for a TID: {no, nl, rel, vt, concept, vm, req, condition, valueset}."""
    if not tid["page"]:
        return []
    html_text = _fetch_page(tid["page"])
    if not html_text:
        return []
    parser = _AnchoredTableParser(tid["anchor"])
    parser.feed(html_text)
    raw = parser.rows
    # First row(s) are header; data rows have a leading row-number cell.
    out: List[Dict] = []
    for row in raw:
        if len(row) < 8:
            continue
        no = row[0].strip()
        # header / param rows lack a numeric-ish leading cell
        if not re.match(r"^\d+[a-z]?$", no):
            continue
        out.append({
            "no": no, "nl": row[1], "rel": row[2], "vt": row[3],
            "concept": row[4], "vm": row[5], "req": row[6],
            "condition": row[7], "valueset": row[8] if len(row) > 8 else "",
        })
    log.info(f"  TID {tid['tid']}: {len(out)} DICOM rows")
    return out


# ── IHE-MADO row loader ─────────────────────────────────────────────────────────

def load_mado_rows() -> Dict[str, List[Dict]]:
    """Group step10-dicom-templates.csv rows by Template ID."""
    by_id: Dict[str, List[Dict]] = {}
    if not TEMPLATES_CSV.exists():
        log.warning(f"  {TEMPLATES_CSV} not found")
        return by_id
    with TEMPLATES_CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            by_id.setdefault(r.get("Template ID", "").strip(), []).append(r)
    return by_id


def _norm_concept(s: str) -> str:
    """Normalise concept name for fuzzy matching (codes/quotes/punct stripped)."""
    s = re.sub(r"\(\s*\d+\s*,\s*\w+\s*,", "", s)  # drop (code, scheme,
    return re.sub(r"[^a-z0-9]", "", s.lower())


# ── requirement-level comparison ────────────────────────────────────────────────
# DICOM: M/MC/U/UC; IHE-MADO: R+/RC+/O+ etc. Required-ish vs optional-ish.
_REQUIRED_DICOM = {"M", "MC"}
_REQUIRED_MADO = {"R", "R+", "RC", "RC+"}

TID_1602_SERIES_ROWS = {"1", "2", "2b", "3", "4", "5", "5a", "5b", "5c", "5d", "5e", "5f", "5g", "18"}
TID_1602_INSTANCE_ROWS = {"2b", "12a", "12b"}


def _diff_type(df: Optional[Dict], mf: Optional[Dict]) -> str:
    in_d, in_m = bool(df), bool(mf)
    if in_d and in_m:
        d_req = (df.get("req", "") or "").strip().rstrip("+") in {x.rstrip("+") for x in _REQUIRED_DICOM}
        m_req = (mf.get("Req Type (IHE)", "") or "").strip() in _REQUIRED_MADO
        return "mado_override" if d_req != m_req else "both"
    return "dicom_only" if in_d else "mado_only"


def crosscheck(tid: Dict, dicom_rows: List[Dict], mado_rows: List[Dict]) -> List[Dict]:
    section_url = (P16_BASE + tid["page"] + "#" + tid["anchor"]) if tid["page"] else ""

    def state(row: Dict) -> str:
        if tid["tid"] == "16XX":
            return "ignore"
        return "lean" if (row.get("Req Type (IHE)") or "").strip() else "full"
    mado_by_no = {r.get("No", "").strip(): r for r in mado_rows if r.get("No", "").strip()}
    mado_by_concept = {_norm_concept(r.get("Concept Name", "")): r for r in mado_rows}
    consumed = set()
    out: List[Dict] = []

    for d in dicom_rows:
        m = mado_by_no.get(d["no"]) or mado_by_concept.get(_norm_concept(d["concept"]))
        if m:
            consumed.add(m.get("No", "").strip())
        context = tid_1602_context(tid["tid"], d["no"], bool(m))
        out.append({
            "Template ID": tid["tid"], "DICOM TID Name": tid["name"], "Row No": d["no"],
            "NL": d["nl"], "REL with Parent": d["rel"], "VT": d["vt"],
            "Concept Name": d["concept"] or (m or {}).get("Concept Name", ""),
            "VM": d["vm"], "Req Type (DICOM)": d["req"],
            "Req Type (IHE)": (m or {}).get("Req Type (IHE)", ""),
            "Condition (DICOM)": d["condition"], "Condition (IHE)": (m or {}).get("Condition", ""),
            "ValueSet (DICOM)": d["valueset"], "ValueSet (IHE)": (m or {}).get("ValueSet Constraint", ""),
            "in_dicom": "Y", "in_ihe_mado": "Y" if m else "",
            "difference_type": _diff_type(d, m), "DICOM Section URL": section_url,
            "MADO Page URL": (m or {}).get("MADO Page URL", ""),
            "DICOM Difference Note": (m or {}).get("DICOM Difference Note", ""),
            "TID 1602 Context": context,
            "Field State": state({"Req Type (IHE)": (m or {}).get("Req Type (IHE)", "")}),
        })

    for m in mado_rows:
        if m.get("No", "").strip() in consumed:
            continue
        context = tid_1602_context(tid["tid"], m.get("No", "").strip(), True)
        out.append({
            "Template ID": tid["tid"], "DICOM TID Name": tid["name"], "Row No": m.get("No", ""),
            "NL": m.get("NL", ""), "REL with Parent": m.get("REL with Parent", ""), "VT": m.get("VT", ""),
            "Concept Name": m.get("Concept Name", ""), "VM": m.get("VM", ""),
            "Req Type (DICOM)": m.get("Req Type (DICOM)", ""), "Req Type (IHE)": m.get("Req Type (IHE)", ""),
            "Condition (DICOM)": "", "Condition (IHE)": m.get("Condition", ""),
            "ValueSet (DICOM)": "", "ValueSet (IHE)": m.get("ValueSet Constraint", ""),
            "in_dicom": "", "in_ihe_mado": "Y", "difference_type": "mado_only",
            "DICOM Section URL": section_url, "MADO Page URL": m.get("MADO Page URL", ""),
            "DICOM Difference Note": m.get("DICOM Difference Note", ""),
            "TID 1602 Context": context,
            "Field State": state(m),
        })
    return out


def tid_1602_context(tid: str, row_no: str, has_mado_usage: bool) -> str:
    if tid != "1602" or not has_mado_usage:
        return ""
    contexts = []
    if row_no in TID_1602_SERIES_ROWS:
        contexts.append("1602-s")
    if row_no in TID_1602_INSTANCE_ROWS:
        contexts.append("1602-i")
    return ";".join(contexts)


def main() -> None:
    mado = load_mado_rows()
    rows: List[Dict] = []
    for tid in TID_CATALOGUE:
        d_rows = get_dicom_template_rows(tid)
        m_rows: List[Dict] = []
        for mid in tid["mado_ids"]:
            m_rows.extend(mado.get(mid, []))
        rows.extend(crosscheck(tid, d_rows, m_rows))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUTPUT_COLS)
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    diff = Counter(r["difference_type"] for r in rows)
    log.info(f"Wrote {len(rows)} rows to {OUTPUT}")
    log.info(f"  diff types: {dict(diff)}")


if __name__ == "__main__":
    main()
