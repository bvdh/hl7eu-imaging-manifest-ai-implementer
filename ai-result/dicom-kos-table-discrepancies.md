# DICOM-KOS Table Discrepancies

The following table lists every allowed DICOM Type or obligation change. Any other field change fails the check.

| Source table | Row identity | Field | Before | After | Result |
|---|---|---|---|---|---|
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Series Instance UID + (0020,000E) | Producer Obligation | SHALL:able-to-populate |  | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Patient + Other Patient IDs Sequence + (0010,1002) | Consumer Obligation |  | SHOULD:process | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Patient + Other Patient IDs Sequence + (0010,1002) | Producer Obligation |  | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + SOP Instance UID + (0008,0018) | Producer Obligation | SHALL:populate |  | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Universal Entity ID + (0010,0032) | Consumer Obligation |  | SHOULD:process | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Universal Entity ID + (0010,0032) | Producer Obligation |  | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Series Number + (0020,0011) | Producer Obligation | SHALL:able-to-populate |  | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document Series + Series Description Code Sequence + (0008,103F) | DICOM Type | 2001-02-28 | 3 | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | Key Object Document + Referenced Request Sequence + (0040,A370) | Producer Obligation | SHALL:populate | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Universal Entity ID Type + (0010,0033) | Consumer Obligation |  | SHOULD:process | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Universal Entity ID Type + (0010,0033) | Producer Obligation |  | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-module-fhir-obligations.csv | SOP Common + Specific Character Set + (0008,0005) | Producer Obligation | SHALL:populate |  | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 1d + EV (123014, DCM, "Target Region") | Producer Obligation | SHALL:populate | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 1e + EV (123014, DCM, "Target Region") | Consumer Obligation |  | SHOULD:process | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 1e + EV (123014, DCM, "Target Region") | Producer Obligation |  | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 1b + EV (121139, DCM, "Modality") | Producer Obligation | SHALL:populate | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 2010 + 4b + EV (121023, DCM, "Procedure Code") | Producer Obligation | SHALL:able-to-populate | SHALL-populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 2010 + 7 + EV (113012, DCM, "Key Object Description") | Producer Obligation | SHALL:populate | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 2 + EV (126200, DCM, "Image Library Group") | Producer Obligation | SHALL:populate | SHALL:able-to-populate ; SHALL:populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 16XX + 1 + DTID 16XX Image Library Entry Descriptors for Key Object Selection | Consumer Obligation |  | SHOULD:process | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 16XX + 1 + DTID 16XX Image Library Entry Descriptors for Key Object Selection | Producer Obligation |  | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 1 + EV (111028, DCM, "Image Library") | Producer Obligation | SHALL:populate | SHALL:able-to-populate ; SHALL:populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 3 + DTID 1602 “Image Library Entry Descriptors” | Consumer Obligation |  | SHOULD:process | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 3 + DTID 1602 “Image Library Entry Descriptors” | Producer Obligation | SHALL:populate | SHALL:able-to-populate | APPROVED |
| ai-result/step11-dicom-template-fhir-obligations.csv | 1600 + 1f + EV (131565, DCM, "Number of Study Related Series") | Producer Obligation | SHALL:populate | SHALL:able-to-populate | APPROVED |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: removed row ('General Study', '>Referenced Series Sequence', '(0008,1115)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: removed row ('General Study', '>Retrieve Location UID', '(0040,E011)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: removed row ('Key Object Document Series', 'Reference Request Sequence', '(0040,A370)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: removed row ('Patient', 'An identifier for the Patient', '(0010,0020)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: removed row ('SOP Common', 'Display URI', '(0040,E021)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: removed row ('General Study', '>Retrieve URL', '(0008,1190)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: removed row ('Patient', 'Patient Birth Date', '(0010,0030)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: added row ('Patient', 'Patient ID', '(0010,0020)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: added row ('Patient', 'Type of Patient ID', '(0010,0022)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: added row ('SOP Common', 'Retrieve URL', '(0008,1190)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: added row ('SOP Common', 'Retrieve Location UID', '(0040,E011)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: added row ('SOP Common', 'Display URI', '(gggg.eeee) (See Note for temporary TI private tag)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: added row ('SOP Common', 'Referenced Series Sequence', '(0008,1115)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: added row ('Patient', "Patient's Birth Date", '(0010,0030)') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('SOP Common', '>Institution Name', '(0008,0080)'): changed ['EU-MADO Profile', 'EU-MADO Field', 'Producer Obligation', 'DICOM-KOS Match'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('General Study', 'Accession Number', '(0008,0050)'): changed ['MADO Description'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('General Study', 'Study Description', '(0008,1030)'): changed ['MADO IHE Usage'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('SOP Common', 'Instance Creation Time', '(0008,0013)'): changed ['Review comment'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('SOP Common', '>Manufacturer', '(0008,0070)'): changed ['EU-MADO Profile', 'EU-MADO Field', 'Producer Obligation', 'DICOM-KOS Match'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('Key Object Document Series', 'Series Date', '(0008,0021)'): changed ['DICOM Type', 'Consumer Obligation', 'Review comment'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('Key Object Document Series', 'Modality', '(0008,0060)'): changed ['Producer Obligation', 'Review comment'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('SOP Common', 'Instance Creation Date', '(0008,0012)'): changed ['Review comment'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('SOP Common', 'SOP Class UID', '(0008,0016)'): changed ['Review comment'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('SOP Common', 'Timezone Offset From UTC', '(0008,0201)'): changed ['MADO IHE Usage', 'Producer Obligation'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('Key Object Document', 'Current Requested Procedure Evidence Sequence', '(0040,A375)'): changed ['MADO IHE Usage', 'EU-MADO Profile', 'EU-MADO Field'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('Key Object Document Series', 'Series Time', '(0008,0031)'): changed ['Review comment'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('General Equipment', 'Manufacturer', '(0008,0070)'): changed ['MADO IHE Usage', 'MADO Description'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('Patient', '>Type of Patient ID', '(0010,0022)'): changed ['Producer Obligation', 'DICOM-KOS Match'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('General Study', 'Study Time', '(0008,0030)'): changed ['MADO Description'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-module-fhir-obligations.csv: ('General Equipment', 'Institution Name', '(0008,0080)'): changed ['MADO IHE Usage', 'MADO Description', 'Review comment'] |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '15', 'DTID 1605 “Image Library Entry Descriptors for CT”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '18', 'DTID 1609 “Image Library Entry Descriptors for Key Object Selection”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '12b', 'EV (121140, DCM, "Number of Frames")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '4', 'EV (111060, DCM, "Study Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '5e', 'EV (131561, DCM, "Series Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '10', 'EV (112227, DCM, "Frame of Reference UID")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '5g', 'EV (131564, DCM, "Number of Series Related Instances")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1609', '2', 'EV (113012, DCM, "Key Object Description")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '7', 'EV (111019, DCM, "Content Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '8', 'EV (126201, DCM, "Acquisition Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '2b', 'EV (123014, DCM, "Target Region")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '1', 'EV (121139, DCM, "Modality")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '17', 'DTID 1607 “Image Library Entry Descriptors for PET”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '5f', 'EV (131562, DCM, "Series Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '9', 'EV (126202, DCM, "Acquisition Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '12a', 'EV (113609, DCM, "Instance Number")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '5d', 'EV (131563, DCM, "Series Description")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '12', 'EV (110911, DCM, "Pixel Data Columns")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '4', 'EV (111060, DCM, "Study Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '3', 'EV (111027, DCM, "Image Laterality")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '2b', 'EV (123014, DCM, "Target Region")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '5e', 'EV (131561, DCM, "Series Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '5c', 'EV (131563, DCM, "Series Description")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '12a', 'EV (113609, DCM, "Instance Number")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '13', 'DTID 1603 “Image Library Entry Descriptors for Projection Radiography”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '17', 'DTID 1607 “Image Library Entry Descriptors for PET”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '5', 'EV (111061, DCM, "Study Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '11', 'EV (110910, DCM, "Pixel Data Rows")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '5f', 'EV (131562, DCM, "Series Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '9', 'EV (126202, DCM, "Acquisition Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '5d', 'EV (131563, DCM, "Series Description")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '14', 'DTID 1604 “Image Library Entry Descriptors for Cross-Sectional Modalities”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '6', 'EV (111018, DCM, "Content Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '5b', 'EV (113607, DCM, "Series Number")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '2', 'EV (123014, DCM, "Target Region")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '12', 'EV (110911, DCM, "Pixel Data Columns")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '3', 'EV (111027, DCM, "Image Laterality")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '5', 'EV (111061, DCM, "Study Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '5c', 'EV (131563, DCM, "Series Description")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1609', '1', 'EV (121144, DCM, "Document Title")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '5a', 'EV (112002, DCM, "Series Instance UID")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '15', 'DTID 1605 “Image Library Entry Descriptors for CT”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '18', 'DTID 1609 “Image Library Entry Descriptors for Key Object Selection”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '14', 'DTID 1604 “Image Library Entry Descriptors for Cross-Sectional Modalities”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '6', 'EV (111018, DCM, "Content Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '16', 'DTID 1606 “Image Library Entry Descriptors for MR”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '5b', 'EV (113607, DCM, "Series Number")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '2', 'EV (123014, DCM, "Target Region")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '13', 'DTID 1603 “Image Library Entry Descriptors for Projection Radiography”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '10', 'EV (112227, DCM, "Frame of Reference UID")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '11', 'EV (110910, DCM, "Pixel Data Rows")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '1', 'EV (121139, DCM, "Modality")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '5g', 'EV (131564, DCM, "Number of Series Related Instances")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '5a', 'EV (112002, DCM, "Series Instance UID")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '7', 'EV (111019, DCM, "Content Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '8', 'EV (126201, DCM, "Acquisition Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-i', '12b', 'EV (121140, DCM, "Number of Frames")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: removed row ('1602-s', '16', 'DTID 1606 “Image Library Entry Descriptors for MR”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '16', 'DTID 1606 “Image Library Entry Descriptors for MR”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '15', 'DTID 1605 “Image Library Entry Descriptors for CT”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '12b', 'EV (121140, DCM, "Number of Frames")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '14', 'DTID 1604 “Image Library Entry Descriptors for Cross-Sectional Modalities”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '18', 'DTID 1609 “Image Library Entry Descriptors for Key Object Selection”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '13', 'DTID 1603 “Image Library Entry Descriptors for Projection Radiography”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '17', 'DTID 1607 “Image Library Entry Descriptors for PET”') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '6', 'EV (111018, DCM, "Content Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '11', 'EV (110910, DCM, "Pixel Data Rows")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '5f', 'EV (131562, DCM, "Series Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '9', 'EV (126202, DCM, "Acquisition Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '7', 'EV (111019, DCM, "Content Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '8', 'EV (126201, DCM, "Acquisition Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '4', 'EV (111060, DCM, "Study Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '3', 'EV (111027, DCM, "Image Laterality")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '12', 'EV (110911, DCM, "Pixel Data Columns")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '10', 'EV (112227, DCM, "Frame of Reference UID")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '5c', 'EV (131563, DCM, "Series Description")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '5a', 'EV (112002, DCM, "Series Instance UID")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '5e', 'EV (131561, DCM, "Series Date")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '5', 'EV (111061, DCM, "Study Time")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '5b', 'EV (113607, DCM, "Series Number")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '2', 'EV (123014, DCM, "Target Region")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '5d', 'EV (131563, DCM, "Series Description")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '5g', 'EV (131564, DCM, "Number of Series Related Instances")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '1', 'EV (121139, DCM, "Modality")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '12a', 'EV (113609, DCM, "Instance Number")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: added row ('1602', '2b', 'EV (123014, DCM, "Target Region")') |
| source CSV | n/a | integrity | n/a | n/a | FAIL: ai-result/step11-dicom-template-fhir-obligations.csv: ('2010', '1', 'DCID 7010 “Key Object Selection Document Title”'): changed ['Producer Obligation', 'Comment'] |
