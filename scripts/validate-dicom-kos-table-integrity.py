#!/usr/bin/env python3
"""Check that DICOM-KOS source tables changed only in approved fields."""

import csv
import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = Path("ai-result/step11-dicom-module-fhir-obligations.csv")
TEMPLATE_PATH = Path("ai-result/step11-dicom-template-fhir-obligations.csv")
REPORT = ROOT / "ai-result/dicom-kos-table-discrepancies.md"
ALLOWED_CHANGED_FIELDS = {"DICOM Type", "Consumer Obligation", "Producer Obligation"}
DISCREPANCIES: list[tuple[str, tuple[str, ...], str, str, str]] = []


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def baseline(path: Path) -> list[dict[str, str]]:
    content = subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT, text=True)
    return list(csv.DictReader(io.StringIO(content)))


def compare(path: Path, key_columns: tuple[str, ...]) -> list[str]:
    before = baseline(path)
    after = read_csv(ROOT / path)
    key = lambda row: tuple(row.get(column, "") for column in key_columns)
    errors = []
    before_by_key = {key(row): row for row in before}
    after_by_key = {key(row): row for row in after}
    for missing in before_by_key.keys() - after_by_key.keys():
        errors.append(f"{path}: removed row {missing}")
    for added in after_by_key.keys() - before_by_key.keys():
        errors.append(f"{path}: added row {added}")
    for row_key in before_by_key.keys() & after_by_key.keys():
        old, new = before_by_key[row_key], after_by_key[row_key]
        row_key = key(new)
        changed = [column for column in old if old.get(column, "") != new.get(column, "")]
        if any(column not in ALLOWED_CHANGED_FIELDS for column in changed):
            errors.append(f"{path}: {row_key}: changed {changed}")
        else:
            for field in changed:
                DISCREPANCIES.append((str(path), row_key, field, old.get(field, ""), new.get(field, "")))
    return errors


def main() -> int:
    errors = compare(MODULE_PATH, ("Module", "Attribute Name", "Tag"))
    errors.extend(compare(TEMPLATE_PATH, ("Template ID", "Row No", "Concept Name")))
    lines = ["# DICOM-KOS Table Discrepancies", "", "The following table lists every allowed DICOM Type or obligation change. Any other field change fails the check.", "", "| Source table | Row identity | Field | Before | After | Result |", "|---|---|---|---|---|---|"]
    for source, row_key, field, before, after in DISCREPANCIES:
        identity = " + ".join(row_key).replace("|", "\\|")
        lines.append(f"| {source} | {identity} | {field} | {before} | {after} | APPROVED |")
    for error in errors:
        lines.append(f"| source CSV | n/a | integrity | n/a | n/a | FAIL: {error.replace('|', '\\|')} |")
    if not errors:
        lines.append("| module/template source CSVs | all rows | non-approved fields | unchanged | unchanged | PASS |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT)
    if errors:
        print("DICOM-KOS table integrity check FAILED")
        print("\n".join(errors))
        return 1
    print("DICOM-KOS table integrity check PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())