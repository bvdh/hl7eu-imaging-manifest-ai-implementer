#!/usr/bin/env python3
"""Fill empty DICOM-KOS module types without changing any other CSV fields."""

import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "ai-result/step10-dicom-module-field-crosscheck.csv"
ENRICHED = ROOT / "ai-result/step11-dicom-module-fhir-obligations.csv"
SOURCE = ROOT / "scripts/dicom-module-crosscheck.py"

OVERRIDES = {
    ("Patient", "An identifier for the Patient", "(0010,0020)"): "1",
    ("Patient", "Issuer of Patient ID", "(0010,0021)"): "3",
    ("Patient", "Issuer of Patient ID Qualifiers Sequence", "(0010,0024)"): "1",
    ("Patient", "Universal Entity ID", "(0040,0032)"): "1",
    ("Patient", "Universal Entity ID Type", "(0040,0033)"): "1C",
    ("SOP Common", "Universal Entity ID", "(0010,0032)"): "1",
    ("SOP Common", "Universal Entity ID Type", "(0010,0033)"): "1C",
    ("General Study", "Referenced Series Sequence", "(0008,1115)"): "1",
    ("General Study", "Retrieve Location UID", "(0040,E011)"): "1",
    ("General Study", "Retrieve URL", "(0008,1190)"): "3",
    ("SOP Common", "Study Instance UID", "(0020,000D)"): "1",
    ("SOP Common", "Display URI", "(0040,E021)"): "3",
}

MODULE_REFS = {
    "Patient": "C.7.1.1",
    "General Study": "C.7.2.1",
    "Key Object Document Series": "C.17.6.1",
    "General Equipment": "C.7.5.1",
    "Key Object Document": "C.17.6.2",
    "SOP Common": "C.12.1",
}


def load_crosscheck():
    spec = importlib.util.spec_from_file_location("dicom_module_crosscheck", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    types = dict(OVERRIDES)
    for module_name, reference in MODULE_REFS.items():
        for row in module.get_dicom_fields(reference):
            if row["type"]:
                types[(module_name, row["attr"].lstrip(">"), row["tag"])] = row["type"]
    return types


def update(path: Path, types: dict) -> int:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        columns = list(rows[0].keys())
    changed = 0
    for row in rows:
        key = (row.get("Module", ""), row.get("Attribute Name", "").lstrip(">"), row.get("Tag", "").replace(" ", ""))
        value = types.get(key)
        if value and not row.get("DICOM Type", "").strip():
            row["DICOM Type"] = value
            changed += 1
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return changed


def main() -> None:
    types = load_crosscheck()
    print(f"step10: {update(MODULES, types)} DICOM Type cells filled")
    print(f"step11: {update(ENRICHED, types)} DICOM Type cells filled")


if __name__ == "__main__":
    main()