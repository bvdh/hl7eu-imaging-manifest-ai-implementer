#!/usr/bin/env python3
"""
Step 11: Add EU-MADO FHIR profile/field + Consumer/Producer obligations to the
DICOM module and template cross-check files.

Inputs:
  ai-result/step10-dicom-module-field-crosscheck.csv  (one row per module attribute)
  ai-result/step10-dicom-template-cross-check.csv      (one row per TID node)
  ai-result/step9-all.csv                              (bridge: EU-MADO field ->
                                                        Consumer/Producer + DICOM-KOS)

Outputs:
  ai-result/step11-dicom-module-fhir-obligations.csv
  ai-result/step11-dicom-template-fhir-obligations.csv

Each output appends: EU-MADO Profile, EU-MADO Field, Consumer Obligation,
Producer Obligation, DICOM-KOS Match. Module rows match by DICOM tag; template
rows match by SR concept code. Multiple matches are joined with " ; ".
"""

import csv
import re
from pathlib import Path

MODULE_IN = Path("ai-result/step10-dicom-module-field-crosscheck.csv")
TEMPLATE_IN = Path("ai-result/step10-dicom-template-cross-check.csv")
BRIDGE = Path("ai-result/step9-all.csv")
MODULE_OUT = Path("ai-result/step11-dicom-module-fhir-obligations.csv")
TEMPLATE_OUT = Path("ai-result/step11-dicom-template-fhir-obligations.csv")

# Human-curated overlay: a reviewed copy of the module output whose curated
# columns (manual FHIR mappings, MADO instructions, obligations, comments) take
# precedence over the auto-derived bridge values. Matched per attribute row.
MODULE_OVERLAY = Path("ai-result/step11-dicom-module-fhir-obligations-review.csv")

ADDED = ["EU-MADO Profile", "EU-MADO Field", "Consumer Obligation", "Producer Obligation", "DICOM-KOS Match"]

# Extra columns introduced by manual review that the bridge cannot derive.
MADO_INSTRUCTION_COL = "MADO instruction"
REVIEW_COMMENT_COL = "Review comment"

# Columns the overlay may override. For these, a non-empty overlay value wins
# over the auto-derived value; an empty overlay value leaves the auto value
# untouched. MADO instruction and Review comment are taken verbatim from the
# overlay (they have no auto-derived counterpart).
OVERLAY_FILL_COLS = [
    "MADO IHE Usage", "MADO Description", "EU-MADO Profile", "EU-MADO Field",
    "Consumer Obligation", "Producer Obligation", "DICOM-KOS Match",
]
OVERLAY_VERBATIM_COLS = [MADO_INSTRUCTION_COL, REVIEW_COMMENT_COL]

TAG_RE = re.compile(r"\(\s*([0-9A-Fa-f]{4})\s*,\s*([0-9A-Fa-f]{4})\s*\)")
CODE_RE = re.compile(r"\b(\d{5,6})\b")

# Module attribute tags whose FHIR target is not derivable from the step9 KOS tag
# (the KOS references *Referenced* SOP UIDs, not the document's own SOP Common tags).
TAG_OVERRIDE = {}


def load_bridge():
    """Index step9 rows that carry a DICOM-KOS link, by tag and by SR concept code."""
    by_tag, by_code, by_field = {}, {}, {}
    for r in csv.DictReader(BRIDGE.open(encoding="utf-8")):
        kos = (r.get("DICOM-KOS") or "").strip()
        if not kos:
            continue
        eu = (r.get("EU-MADO") or "").strip()
        prof, _, fld = eu.partition(".")
        entry = {
            "profile": prof, "field": fld,
            "consumer": (r.get("Consumer") or "").strip(),
            "producer": (r.get("Producer") or "").strip(),
            "kos": kos,
        }
        for g1, g2 in TAG_RE.findall(kos):
            by_tag.setdefault(f"({g1.upper()},{g2.upper()})", []).append(entry)
        for code in CODE_RE.findall(kos):
            by_code.setdefault(code, []).append(entry)
        if fld:
            by_field.setdefault(fld, []).append(entry)
    return by_tag, by_code, by_field


def merge(entries):
    if not entries:
        return {k: "" for k in ADDED}
    j = lambda key: " ; ".join(dict.fromkeys(e[key] for e in entries if e[key]))
    return {
        "EU-MADO Profile": j("profile"), "EU-MADO Field": j("field"),
        "Consumer Obligation": j("consumer"), "Producer Obligation": j("producer"),
        "DICOM-KOS Match": j("kos"),
    }


def overlay_key(row):
    """Stable per-attribute key shared by the auto output and the curated overlay."""
    return (
        (row.get("Module") or "").strip(),
        (row.get("Attribute Name") or "").strip(),
        (row.get("Tag") or "").strip(),
    )


def load_overlay():
    """Index the human-curated overlay rows by attribute key.

    Returns an empty dict if the overlay file is absent, so the pipeline still
    runs in environments where the review file has not been produced yet.
    """
    if not MODULE_OVERLAY.exists():
        return {}
    overlay = {}
    for r in csv.DictReader(MODULE_OVERLAY.open(encoding="utf-8")):
        overlay[overlay_key(r)] = r
    return overlay


def apply_overlay(row, ov):
    """Overlay curated columns onto an auto-enriched row.

    Fill columns: a non-empty overlay value replaces the auto value.
    Verbatim columns: taken directly from the overlay (may be empty).
    """
    for col in OVERLAY_FILL_COLS:
        val = (ov.get(col) or "").strip()
        if val:
            row[col] = val
    for col in OVERLAY_VERBATIM_COLS:
        row[col] = (ov.get(col) or "").strip()
    return row


def enrich_modules(by_tag, by_field, overlay):
    rows = list(csv.DictReader(MODULE_IN.open(encoding="utf-8")))
    # Output column order: base columns with "MADO instruction" inserted after
    # "MADO Description", then the auto-derived ADDED columns, then "Review comment".
    base_cols = list(rows[0].keys()) if rows else []
    cols = []
    for c in base_cols:
        cols.append(c)
        if c == "MADO Description":
            cols.append(MADO_INSTRUCTION_COL)
    if MADO_INSTRUCTION_COL not in cols:
        cols.append(MADO_INSTRUCTION_COL)
    cols += ADDED + [REVIEW_COMMENT_COL]

    out = []
    hits = 0
    overlaid = 0
    for r in rows:
        tag = (r.get("Tag") or "").strip().upper().replace(" ", "")
        e = by_tag.get(tag, [])
        if not e and tag in TAG_OVERRIDE:
            e = by_field.get(TAG_OVERRIDE[tag], [])
        if e:
            hits += 1
        row = {**r, **merge(e), MADO_INSTRUCTION_COL: "", REVIEW_COMMENT_COL: ""}
        ov = overlay.get(overlay_key(r))
        if ov:
            apply_overlay(row, ov)
            overlaid += 1
        out.append(row)
    write(MODULE_OUT, cols, out)
    return len(out), hits, overlaid


def enrich_templates(by_code):
    rows = list(csv.DictReader(TEMPLATE_IN.open(encoding="utf-8")))
    cols = list(rows[0].keys()) + ADDED if rows else ADDED
    out = []
    hits = 0
    for r in rows:
        codes = CODE_RE.findall(r.get("Concept Name") or "")
        e = [x for c in codes for x in by_code.get(c, [])]
        if e:
            hits += 1
        out.append({**r, **merge(e)})
    write(TEMPLATE_OUT, cols, out)
    return len(out), hits


def write(path, cols, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def main():
    by_tag, by_code, by_field = load_bridge()
    overlay = load_overlay()
    m_total, m_hit, m_overlaid = enrich_modules(by_tag, by_field, overlay)
    t_total, t_hit = enrich_templates(by_code)
    print(f"modules:   {m_total} rows, {m_hit} matched, {m_overlaid} overlaid -> {MODULE_OUT}")
    if not overlay:
        print(f"           (no overlay found at {MODULE_OVERLAY}; auto values only)")
    print(f"templates: {t_total} rows, {t_hit} matched -> {TEMPLATE_OUT}")


if __name__ == "__main__":
    main()
