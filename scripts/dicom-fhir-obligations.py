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

ADDED = ["EU-MADO Profile", "EU-MADO Field", "Consumer Obligation", "Producer Obligation", "DICOM-KOS Match"]

TAG_RE = re.compile(r"\(\s*([0-9A-Fa-f]{4})\s*,\s*([0-9A-Fa-f]{4})\s*\)")
CODE_RE = re.compile(r"\b(\d{5,6})\b")


def load_bridge():
    """Index step9 rows that carry a DICOM-KOS link, by tag and by SR concept code."""
    by_tag, by_code = {}, {}
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
    return by_tag, by_code


def merge(entries):
    if not entries:
        return {k: "" for k in ADDED}
    j = lambda key: " ; ".join(dict.fromkeys(e[key] for e in entries if e[key]))
    return {
        "EU-MADO Profile": j("profile"), "EU-MADO Field": j("field"),
        "Consumer Obligation": j("consumer"), "Producer Obligation": j("producer"),
        "DICOM-KOS Match": j("kos"),
    }


def enrich_modules(by_tag):
    rows = list(csv.DictReader(MODULE_IN.open(encoding="utf-8")))
    cols = list(rows[0].keys()) + ADDED if rows else ADDED
    out = []
    hits = 0
    for r in rows:
        tag = (r.get("Tag") or "").strip().upper().replace(" ", "")
        e = by_tag.get(tag, [])
        if e:
            hits += 1
        out.append({**r, **merge(e)})
    write(MODULE_OUT, cols, out)
    return len(out), hits


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
    by_tag, by_code = load_bridge()
    m_total, m_hit = enrich_modules(by_tag)
    t_total, t_hit = enrich_templates(by_code)
    print(f"modules:   {m_total} rows, {m_hit} matched -> {MODULE_OUT}")
    print(f"templates: {t_total} rows, {t_hit} matched -> {TEMPLATE_OUT}")


if __name__ == "__main__":
    main()
