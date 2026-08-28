# DICOM-KOS Table Discrepancies

The following table lists every allowed DICOM Type or obligation change. Any other field change fails the check.

| Source table | Row identity | Field | Before | After | Result |
|---|---|---|---|---|---|
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document + Referenced Request Sequence + (0040,A370) | Producer Obligation | SHALL:able-to-populate | SHALL:populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 2 + EV (126200, DCM, "Image Library Group") | Producer Obligation | SHALL:able-to-populate ; SHALL:populate | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 1 + EV (111028, DCM, "Image Library") | Producer Obligation | SHALL:able-to-populate ; SHALL:populate | SHALL:able-to-populate | APPROVED |
| module/template source CSVs | all rows | non-approved fields | unchanged | unchanged | PASS |
