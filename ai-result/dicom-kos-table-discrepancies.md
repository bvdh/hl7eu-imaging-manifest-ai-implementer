# DICOM-KOS Table Discrepancies

The following table lists every allowed change. Any change outside `DICOM Type` fails the check.

| Source table | Row identity | Field | Before | After | Result |
|---|---|---|---|---|---|
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Study Description + (0008,1030) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + >Retrieve Location UID + (0040,E011) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Study Time + (0008,0030) | DICOM Type |  | 2 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Series Number + (0020,0011) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Issuer of Accession Number Sequence + (0008,0051) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Series Instance UID + (0020,000E) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + >Referenced Series Sequence + (0008,1115) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Patient + An identifier for the Patient + (0010,0020) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Physician(s) of Record + (0008,1048) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Study Date + (0008,0020) | DICOM Type |  | 2 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + >Retrieve URL + (0008,1190) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Consulting Physician Identification Sequence + (0008,009D) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Patient + Universal Entity ID + (004 0,0032) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Accession Number + (0008,0050) | DICOM Type |  | 2 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Referring Physician's Name + (0008,0090) | DICOM Type |  | 2 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Consulting Physician's Name + (0008,009C) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Physician(s) of Record Identification Sequence + (0008,1049) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Requesting Service Code Sequence + (0032,1034) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Requesting Service + (0032,1033) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Universal Entity ID Type + (0010,0033) | DICOM Type |  | 1C | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Study ID + (0020,0010) | DICOM Type |  | 2 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Protocol Name + (0018,1030) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Patient + Issuer of Patient ID Qualifiers Sequence + (0010,0024) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Display URI + (0040,E021) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Patient + Universal Entity ID Type + (004 0,0033) | DICOM Type |  | 1C | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Study Instance UID + (0020,000D) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Referring Physician Identification Sequence + (0008,0096) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Reason For Performed Procedure Code Sequence + (0040,1012) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Physician(s) Reading Study Identification Sequence + (0008,1062) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Universal Entity ID + (0010,0032) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Referenced Study Sequence + (0008,1110) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Name of Physician(s) Reading Study + (0008,1060) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Modality + (0008,0060) | DICOM Type |  | 1 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Patient + Issuer of Patient ID + (0010,0021) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Series Description + (0008,103E) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | General Study + Procedure Code Sequence + (0008,1032) | DICOM Type |  | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Series Time + (0008,0031) | DICOM Type |  | 3 | APPROVED |
| module/template source CSVs | all rows | non-Type fields | unchanged | unchanged | PASS |
