# IHE RAD MADO – Volume 3 – Content Modules

<!-- Source: .cache/IHE_RAD_Suppl_MADO.pdf pages 39–65 -->


<!-- page 39 -->

______________________________________________________________________________


<a id="volume-3-content-modules"></a>
# Volume 3 – Content Modules

975


<!-- page 40 -->

______________________________________________________________________________


<a id="4-ihe-namespaces-concept-domains-and-vocabularies"></a>
## 4 IHE Namespaces, Concept Domains and Vocabularies

Add to Section 4 IHE Namespaces, Concept Domains and Vocabularies, Section 4.3.1, the following two lines.in Table 4.3.1-1 Format Codes for IHE Radiology Profiles,


<a id="43-format-codes-and-vocabularies"></a>
## 4.3 Format Codes and Vocabularies

980 4.3.1 IHE Format Codes


**Table 4.3.1-1: Format Codes for IHE Radiology Profiles**

Add to Volume 3 Section 6, Section 6.X MADO Imaging Study Manifest 985


<a id="6x-mado-imaging-study-manifest"></a>
## 6.X MADO Imaging Study Manifest

6.X.1 Scope An imaging study manifest is a document listing the key information about the content of a single imaging study. It includes location pointers to its instances’ content and organizes this 990 information according to the well-established model of an imaging study containing one or more series with each series containing one or more instances (e.g., images). MADO defines two content formats (and corresponding encodings) for the imaging study manifest: 1. DICOM KOS-Based (see TF-3: 6.X.2) 995 2. HL7 FHIR-Based (see TF-3: 6.X.3) A bi-directional mapping between the two formats for transformation purposes is also specified (see TF-3: 6.X.5). An MHD Envelope Content to be used along with the IHE MHD Profile is specified (see TF-3: 6.X.4) when Document Consumer Actors and Document Source Actors of the document sharing 1000 infrastructure are grouped with MADO (see TF-1:X.6).

<a id="table-431-1-format-codes-for-ihe-radiology-profiles"></a>
<table>
  <caption>Table 4.3.1-1: Format Codes for IHE Radiology Profiles</caption>
  <thead>
    <tr><th></th><th>Profile</th><th></th><th></th><th>Format Code</th><th></th><th></th><th>Coding Scheme</th><th></th><th></th><th>Description</th><th></th><th></th><th>Reference</th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Manifest
Based
Access to
DICOM
Objects
(MADO)</td><td></td><td></td><td>1.2.840.10008.5.1.4.1.1.88.59
(same as XDS-I assigned Format
Code)</td><td></td><td></td><td>1.2.840.10008.2.6.1</td><td></td><td></td><td>MADO DICOM
KOS-Based
Imaging Study
Manifest</td><td></td><td></td><td>6.X.2</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>urn:ihe:rad:MADO:fhir-manifest:2026</td><td></td><td></td><td>1.3.6.1.4.1.19376.1.2.7.1</td><td></td><td></td><td>MADO FHIR-based
Imaging Study
Manifest</td><td></td><td></td><td>6.X.3</td><td></td><td></td></tr>
  </tbody>
</table>


<!-- page 41 -->

______________________________________________________________________________ Finally, a set of search parameters associated to imaging study manifests, is specified and expected to be supported by Document Consumer Actors of the document sharing infrastructure grouped with MADO (see TF-1: X.6). 6.X.2 DICOM KOS-Based Imaging Study Content Definition 1005 This section specifies the structure and format of an Imaging Study Manifest for the MADO Profile using the DICOM standards. It is based on the DICOM Key Object Selection (KOS) Document Information Object Definition (IOD) as specified in DICOM PS3.3 Section A.35.4 Key Object Selection Document IOD. 6.X.2.1 Conventions 1010 IHE Profiles may constrain the use of instances of specific DICOM IODs (also referred to as DICOM objects). This typically means placing requirements on the creators of those instances, although requirements may also be placed on the receivers and users. These profiling conventions on DICOM IOD are defined in Appendix E Section E.2 of the IHE Technical Frameworks General Introduction. These conventions are copied in this section (as extracted 1015 from section E.2 of CP-RAD-562 which is not yet approved at the time of issuing this Trial Implementation). • The IHE Technical Framework uses the following legend to specify requirements for DICOM IOD module encoding:


**Table 6.X.2.1-1: Usage of DICOM Modules in IHE**

1020 • The IHE Technical Framework uses the following legend to specify requirements for DICOM attribute encoding:


**Table 6.X.2.1-2: Usage of DICOM Attributes in IHE**

<a id="table-6x21-1-usage-of-dicom-modules-in-ihe"></a>
<table>
  <caption>Table 6.X.2.1-1: Usage of DICOM Modules in IHE</caption>
  <thead>
    <tr><th>M / C / U</th><th>As defined in DICOM PS 3.3</th></tr>
  </thead>
  <tbody>
    <tr><td>R</td><td>The Module is defined as Conditional (C) or User Option (U) in DICOM. The Requirement is an
IHE extension of the DICOM requirements, and the module shall be present.</td></tr>
    <tr><td>RC</td><td>The Module is defined as Conditional (C) or User Option (U) in DICOM. The Requirement is an
IHE extension of the DICOM requirements, and the module shall be present when the specified
conditions apply.</td></tr>
  </tbody>
</table>

<a id="table-6x21-2-usage-of-dicom-attributes-in-ihe"></a>
<table>
  <caption>Table 6.X.2.1-2: Usage of DICOM Attributes in IHE</caption>
  <thead>
    <tr><th>O</th><th>The attribute or its value is optional, i.e., in DICOM it is Type 2 or 3.</th></tr>
  </thead>
  <tbody>
    <tr><td>O+*</td><td>The attribute is optional, but additional constraints have been added. Note: The specification
approach does not force a Type 2 or Type 3 value to become a Type 1 by stating O+.</td></tr>
  </tbody>
</table>


<!-- page 42 -->

______________________________________________________________________________ 1025 Specifications for constraining instances of DICOM Structured Reports follow the conventions in the tables above. In many cases, requiring the use of a specific DICOM SR Template may be sufficient. 6.X.2.2 General Definitions Study Instance UID (0020,000D) in the Imaging Study Manifest shall use the same value as the 1030 referenced instances. Since the Imaging study manifest instance is not considered to be “shared” with the MADO specified mechanisms, it will not include itself in the list of shared instances. When shared with MHD, MHDS, XDS.b, XDS-I.b document sharing profiles, the Imaging Study Manifest, shall be encoded as a DICOM Part 10 File format having a MIME type of “application/dicom”. 1035


**Table 6.X.2.2: Imaging Study Manifest Format Code**

6.X.2.3 Referenced Standards • DICOM PS 3.3: A.35.4 Key Object Selection Document IOD 6.X.2.4 IOD Definition 1040 This section builds upon the DICOM IOD specification of a Key Object Selection SOP Class

<a id="table-page-42-table-1"></a>
<table>
  <caption>Table (page 42, table 1)</caption>
  <thead>
    <tr><th>R</th><th>The attribute shall be present with a value, and is not an IHE extension of the DICOM
requirements, i.e., it is already Type 1 in DICOM, but additional constraints are placed by IHE,
for example on the value set that may be used for the attribute.</th></tr>
  </thead>
  <tbody>
    <tr><td>R+</td><td>The Requirement is an IHE extension of the DICOM requirements, and the attribute shall be
present with a value, i.e., is Type 1, whereas the DICOM requirement may be Type 2 or 3.</td></tr>
    <tr><td>RC+</td><td>The Requirement is an IHE extension of the DICOM requirements, and the attribute shall be
present when the condition is satisfied, i.e., is Type 1C, whereas the DICOM requirement may be
Type 2 or 3. If the condition is not fulfilled, the DICOM definitions apply. Note, that this means
that the attribute may be present / have a value also in case the condition does not apply.</td></tr>
    <tr><td>D</td><td>The requirements of DICOM apply unchanged, but the attribute needs to be displayed.</td></tr>
    <tr><td>-</td><td>No IHE extension of the DICOM requirements is defined. The attribute is listed for better
readability or similar purpose.</td></tr>
    <tr><td>X+</td><td>The attribute information is required to be absent. DICOM Type 2 attributes shall be present with
no value. DICOM Type 3 attributes shall be absent.</td></tr>
  </tbody>
</table>

<a id="table-6x22-imaging-study-manifest-format-code"></a>
<table>
  <caption>Table 6.X.2.2: Imaging Study Manifest Format Code</caption>
  <thead>
    <tr><th></th><th>Format Code</th><th></th><th></th><th>Coding Scheme</th><th></th><th></th><th>Description</th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>1.2.840.10008.5.1.4.1.1.88.59
(same as XDS-I assigned Format Code)</td><td></td><td></td><td>1.2.840.10008.2.6.1</td><td></td><td></td><td>MADO DICOM
KOS-Based Imaging
Study Manifest</td><td></td><td></td></tr>
  </tbody>
</table>


<!-- page 43 -->

______________________________________________________________________________ (1.2.840.10008.5.1.4.1.1.88.59) as specified by the DICOM Standard. It focusses on constraints and additions specific to the KOS-Based MADO Imaging Study Manifest.


**Table 6.X.2.4-1: Usage of DICOM Modules in MADO Imaging Study Manifest**

1045 In the modules specified below only the DICOM attributes profiled by MADO are listed. The DICOM standard applies for all other attributes. 6.X.2.5 Patient Module 6.X.2.5.1 Module Definition


**Table 6.X.2.5.1-1: Usage of DICOM Attributes in Patient Module**

<a id="table-6x24-1-usage-of-dicom-modules-in-mado-imaging-study-manifest"></a>
<table>
  <caption>Table 6.X.2.4-1: Usage of DICOM Modules in MADO Imaging Study Manifest</caption>
  <thead>
    <tr><th></th><th>IE</th><th></th><th></th><th>Module</th><th></th><th></th><th>Reference</th><th></th><th></th><th>Usage</th><th></th><th></th><th>IHE Usage</th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Patient</td><td></td><td></td><td>Patient</td><td></td><td></td><td>C.7.1.1</td><td></td><td></td><td>M</td><td></td><td></td><td>M
See Section 6.X.2.5</td><td></td><td></td></tr>
    <tr><td>Study</td><td></td><td></td><td>General Study</td><td></td><td></td><td>C.7.2.1</td><td></td><td></td><td>M</td><td></td><td></td><td>M
See Section 6.X.2.6</td><td></td><td></td></tr>
    <tr><td>Series</td><td></td><td></td><td>Key Object Document
Series</td><td></td><td></td><td>C.17.6.1</td><td></td><td></td><td>M</td><td></td><td></td><td>M</td><td></td><td></td></tr>
    <tr><td>Equipment</td><td></td><td></td><td>General Equipment</td><td></td><td></td><td>C.7.5.1</td><td></td><td></td><td>M</td><td></td><td></td><td>M
See Section 6.X.2.7</td><td></td><td></td></tr>
    <tr><td>SR Document</td><td></td><td></td><td>Key Object Document</td><td></td><td></td><td>C.17.6.2</td><td></td><td></td><td>M</td><td></td><td></td><td>M
See Section 6.X.2.8</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>SR Document Content</td><td></td><td></td><td>C.17.3</td><td></td><td></td><td>M</td><td></td><td></td><td>M
See Section 6.X.2.9</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>SOP Common</td><td></td><td></td><td>C.12.1</td><td></td><td></td><td>M</td><td></td><td></td><td>M
See Section 6.X.2.10</td><td></td><td></td></tr>
  </tbody>
</table>

<a id="table-6x251-1-usage-of-dicom-attributes-in-patient-module"></a>
<table>
  <caption>Table 6.X.2.5.1-1: Usage of DICOM Attributes in Patient Module</caption>
  <thead>
    <tr><th>Attributes from Table C.7-1 Patient Module</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE
Usage</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td>Patient ID</td><td>(0010,0020)</td><td>R+</td><td></td><td>Primary identifier for the patient.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>See Section 6.X.2.5.2.1.1.</td><td></td></tr>
    <tr><td>Include Table 6.X.2.5.2.1.3-1 “Issuer of Patient ID Macro Attributes” - see section 6.X.2.5.2.1.3 Issuer of Patient ID Macro</td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Other Patient IDs Sequence</td><td>(0010,1002)</td><td>R+</td><td></td><td>A Sequence of identification numbers or codes used to</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>identify the Patient, which may or may not be human</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>readable, and may or may not have been obtained from</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>an implanted or attached device such as an RFID or</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>barcode.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>One or more Items shall be included in this Sequence.</td><td></td></tr>
  </tbody>
</table>

<a id="table-6x251-1-usage-of-dicom-attributes-in-patient-module-2"></a>
<table>
  <caption>Table 6.X.2.5.1-1: Usage of DICOM Attributes in Patient Module</caption>
  <thead>
    <tr><th>IHE</th></tr>
  </thead>
  <tbody>
    <tr><td>Usage</td></tr>
  </tbody>
</table>


<!-- page 44 -->

______________________________________________________________________________ 1050 6.X.2.5.1.1 Patient Identification Attributes Descriptions 6.X.2.5.1.1.1 Patient ID (0010,0020) The Patient ID (0010,0020), whether used as the primary patient identifier or one of the other patient ids, shall be combined with the Issuer of Patient ID Qualifiers Sequence (0010,0024) to 1055 provide a globally unique patient identifier in all cases. 6.X.2.5.1.1.2 Other Patient IDs Sequence (0010,1002) The Other Patient IDs Sequence (0010,1002) shall also contain the patient identifier present in the Patient ID attribute (0010,0020) of the imaging study manifest. In addition, it may contain other known patient identifiers such as national, regional and local ones. 1060 This will allow an importing system to select from the Other Patient IDs sequence a value that is more locally useful and place it in the Patient ID attribute (0010,0020) without making any changes to the Other Patient IDs Sequence identifiers. 6.X.2.5.1.1.3 Issuer of Patient ID Macro


**Table 6.X.2.5.1.1.3-1: Usage of DICOM Attributes in Issuer of Patient ID Macro**

<a id="table-page-44-table-1"></a>
<table>
  <caption>Table (page 44, table 1)</caption>
  <thead>
    <tr><th>Attributes from Table C.7-1 Patient Module</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE
Usage</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>See Section 6.X.2.5.2.1.2.</td><td></td></tr>
    <tr><td>&gt;Patient ID</td><td>(0010,0020)</td><td>R+</td><td>An identifier for the Patient.</td><td></td><td></td></tr>
    <tr><td>&gt;Include Table 6.X.2.5.2.1.3-1 “Issuer of Patient ID Macro Attributes” - see section 6.X.2.5.2.1.3 Issuer of Patient ID
Macro</td><td></td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>

<a id="table-page-44-table-2"></a>
<table>
  <caption>Table (page 44, table 2)</caption>
  <thead>
    <tr><th>IHE</th></tr>
  </thead>
  <tbody>
    <tr><td>Usage</td></tr>
  </tbody>
</table>

<a id="table-6x25113-1-usage-of-dicom-attributes-in-issuer-of-patient-id-macro"></a>
<table>
  <caption>Table 6.X.2.5.1.1.3-1: Usage of DICOM Attributes in Issuer of Patient ID Macro</caption>
  <thead>
    <tr><th>Attributes from Table 10-18 Issuer of Patient ID Macro Attributes</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE
Usage</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td>Issuer of Patient ID</td><td>(0010,0021)</td><td>O+</td><td></td><td>Identifier of the Assigning Authority (system,</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>organization, agency, or department) that issued the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Patient ID.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>If present should contain a label that corresponds to the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>authority identified by the Universal Entity ID</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>(0010,0032) in the Issuer of Patient ID Qualifiers</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Sequence (0010,0024).</td><td></td></tr>
    <tr><td>Issuer of Patient ID Qualifiers
Sequence</td><td>(0010,0024)</td><td>R+</td><td></td><td>Attributes specifying or qualifying the identity of the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Issuer of the Patient ID (0010,0021) or scoping the</td><td></td></tr>
  </tbody>
</table>

<a id="table-6x25113-1-usage-of-dicom-attributes-in-issuer-of-patient-id-macro-2"></a>
<table>
  <caption>Table 6.X.2.5.1.1.3-1: Usage of DICOM Attributes in Issuer of Patient ID Macro</caption>
  <thead>
    <tr><th>IHE</th></tr>
  </thead>
  <tbody>
    <tr><td>Usage</td></tr>
  </tbody>
</table>


<!-- page 45 -->

______________________________________________________________________________ 1065 6.X.2.6 General Study Module


**Table 6.X.2.6-1: Usage of DICOM Attributes in General Study Module**

6.X.2.6.1 Accession Number Attribute Descriptions 1070 Three workflow cases shall be supported by all actors of the MADO Profile:

<a id="table-page-45-table-1"></a>
<table>
  <caption>Table (page 45, table 1)</caption>
  <thead>
    <tr><th>Attributes from Table 10-18 Issuer of Patient ID Macro Attributes</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE
Usage</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Patient ID (0010,0020).</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Only a single Item shall be included in this Sequence.</td><td></td></tr>
    <tr><td>&gt;Universal Entity ID</td><td>(004
0,0032)</td><td>R+</td><td></td><td>Globally unique identifier for the Patient ID Assigning</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Authority.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>The authority identified by this attribute shall be the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>same as that labelled by the Issuer of Patient ID</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>(0010,0021).</td><td></td></tr>
    <tr><td>&gt;Universal Entity ID Type</td><td>(004
0,0033)</td><td>R+</td><td></td><td>Standard defining the format of the Universal Entity</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>ID.</td><td></td></tr>
  </tbody>
</table>

<a id="table-page-45-table-2"></a>
<table>
  <caption>Table (page 45, table 2)</caption>
  <thead>
    <tr><th>IHE</th></tr>
  </thead>
  <tbody>
    <tr><td>Usage</td></tr>
  </tbody>
</table>

<a id="table-6x26-1-usage-of-dicom-attributes-in-general-study-module"></a>
<table>
  <caption>Table 6.X.2.6-1: Usage of DICOM Attributes in General Study Module</caption>
  <thead>
    <tr><th>Attributes from Table C.7-3 General Study Module</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE
Usage</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td>Study Date</td><td>(0008,0020)</td><td>R+</td><td></td><td>Date the Study started.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>See Section 6.X.2.6.2.</td><td></td></tr>
    <tr><td>Study Time</td><td>(0008,0030)</td><td>R+</td><td></td><td>Time the Study started.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>See Section 6.X..2.6.2.</td><td></td></tr>
    <tr><td>Accession Number</td><td>(0008,0050)</td><td>O+</td><td></td><td>Identifier of the imaging (scheduled) procedure request. Present</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>when a single value is assigned to the imaging study. When an</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>imaging study has multiple accession numbers assigned, the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Accession Number (0008,0050) shall be empty, and the originally</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>assigned accession numbers shall be present in the Referenced</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Request Sequence 6.X.2.8.1. See Section 6.X.2.8.1 Accession</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Number Attribute Descriptions.</td><td></td></tr>
    <tr><td>Issuer of Accession
Number Sequence</td><td>(0008,0051)</td><td>RC+</td><td></td><td>Identifier of the Assigning Authority that issued the Accession</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Number (0008,0050). Required if Accession Number</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>(0008,0050) is not empty.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Only a single Item shall be included in this Sequence.</td><td></td></tr>
    <tr><td>&gt; Include Table 6.X.2.12-1 “HL7v2 Hierarchic Designator Macro Attributes” – see section 6.X.2.12 HL7v2 Hierarchic
Designator Macro</td><td></td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>

<a id="table-6x26-1-usage-of-dicom-attributes-in-general-study-module-2"></a>
<table>
  <caption>Table 6.X.2.6-1: Usage of DICOM Attributes in General Study Module</caption>
  <thead>
    <tr><th>IHE</th></tr>
  </thead>
  <tbody>
    <tr><td>Usage</td></tr>
  </tbody>
</table>


<!-- page 46 -->

______________________________________________________________________________ 1. Simple Case: An imaging study is related to a single Accession Number (IHE Scheduled Workflow Profile, see RAD TF2: 4.6.4.1.2.3.1 Simple Case). The General Study Module conveys the accession number. 2. Group Case: An Imaging Study is related to more than one Accession Number (IHE 1075 Scheduled Workflow Profile, see RAD TF2: 4.6.4.1.2.3.4 Group Case). The Referenced Request Sequence 6.X.2.8.1 conveys these multiple Accession Numbers. 3. Absent Case: An imaging study is not locally stored with an Accession Number. One or more unique Accession Number(s) shall be generated by the Content Creator and placed in the Manifest. If a single accession number is generated, it is conveyed in the General 1080 Study Module, otherwise the Referenced Request Sequence is used. If Imaging Reports exist and are associated to the shared imaging study they shall also contain the appropriate generated Accession Number. 6.X.2.6.2 Date/Time Attribute Descriptions 6.X.2.6.2.1 Manifest Study Date and Time 1085 The Study Date Date (0008,0020) and Study Time (0008,0030) in the imaging study manifest are required by the MADO Profile. They are Type 2 attributes in DICOM and are widely present in imaging studies. These attributes are among the critical search parameters (RAD TF-3: 6.X.5 Imaging Study Manifest Search Metadata) and need to be present in the imaging study manifest. 6.X.2.6.2.2 Dates and Times Timezone Offset 1090 In a document sharing context, all date, time and datetime attribute values in the referenced imaging study should be specified in a time zone, for which it is strongly recommended to convey the Timezone Offset From UTC (0008,0201) in the retrieved referenced instances of the imaging study. This is described by the IHE CT Profile Timezone Offset Option introduced by IHE CP-ITI- 1095 1329 and CP-RAD-565. 6.X.2.7 General Equipment Module


**Table 6.X.2.7-1: Usage of DICOM Attributes in General Equipment**

<a id="table-6x27-1-usage-of-dicom-attributes-in-general-equipment"></a>
<table>
  <caption>Table 6.X.2.7-1: Usage of DICOM Attributes in General Equipment</caption>
  <thead>
    <tr><th>Attributes from Table C.7-8 General Equipment Module</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td></td><td>IHE</td><td></td><td>Attribute Description</td></tr>
    <tr><td></td><td></td><td></td><td>Usage</td><td></td><td></td></tr>
    <tr><td>Manufacturer</td><td>(0008,0070)</td><td>R+</td><td></td><td></td><td>Manufacturer of the equipment that produced the KOS manifest.
This attribute is required to facilitate the discovery of errors’
sources in the creation of KOS Manifests.</td></tr>
    <tr><td>Institution Name</td><td>(0008,0080)</td><td>R+</td><td></td><td></td><td>Defines the institution that created the KOS manifest. This
information is important to trace back any content error in a KOS
Manifest.</td></tr>
  </tbody>
</table>


<!-- page 47 -->

______________________________________________________________________________ 6.X.2.8 Key Object Document Module 1100 Table 6.X.2.8-1: Usage of DICOM Attributes in Key Object Document Module 6.X.2.8.1 Referenced Request Macro Description Identifies Requested Procedures that are being fulfilled (completely or partially) in the imaging study referenced by the manifest. 1105 Figure 6.X.2.2.8.1-1 shows the many to many relationships between the workflow entities Clinical Order and Imaging Procedure Request (called Scheduled Procedure Request by DICOM) and the Imaging Study. The MADO Profile is designed to handle all of these relationships to ensure interoperability even between the broadest number of existing and future Imaging Document Consumers and Sources.

<a id="table-page-47-table-1"></a>
<table>
  <caption>Table (page 47, table 1)</caption>
  <thead>
    <tr><th>Attributes from Table C.7-8 General Equipment Module</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td></td><td>IHE</td><td></td><td>Attribute Description</td></tr>
    <tr><td></td><td></td><td></td><td>Usage</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td>Fixed value configured onsite at install time of the software that
created the KOS Manifests.
Note: It is recommended to format this attribute according to the
HL7 V2.5 XON data type so that it contains, in addition to the
institution name, its globally unique identifier. This format is
identical to the format of the authorInstitution Attribute of the
MHD, XDS and XCA metadata.</td></tr>
  </tbody>
</table>

<a id="1100-table-6x28-1-usage-of-dicom-attributes-in-key-object-document-module"></a>
<table>
  <caption>1100 Table 6.X.2.8-1: Usage of DICOM Attributes in Key Object Document Module</caption>
  <thead>
    <tr><th>Attributes from Table C.17.6-2 Key Object Document Module</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td></td><td>Tag</td><td></td><td>IHE</td><td></td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Usage</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Referenced Request
Sequence</td><td></td><td>(0040,A370)</td><td>R+</td><td>R+</td><td></td><td></td><td>Identifies Requested Procedures to which this Document</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>pertains.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>One or more Items shall be included in this Sequence.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>See Section 6.X.2.8.1.</td><td></td></tr>
    <tr><td>&gt;Include Table 6.X.2.8.1-1 “Referenced Request Macro Attributes” – see section 6.X.2.8.1 Referenced Request Macro</td><td>&gt;Include Table 6.X.2.8.1-1 “Referenced Request Macro Attributes” – see section 6.X.2.8.1 Referenced Request Macro</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Current Requested
Procedure Evidence
Sequence</td><td></td><td>(0040,A375)</td><td>R</td><td></td><td></td><td>List of all Composite SOP Instances references in Content
Sequence (0040,A730), including all presentation states, real
world value maps and other accompanying composite instances
that are referenced from the content items.</td><td></td><td></td></tr>
    <tr><td></td><td>&gt; Include Table 6.X.2.12-1 “HL7v2 Hierarchic Designator Macro Attributes” – see section 6.X.2.12 HL7v2 Hierarchic</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td></td><td>Designator Macro</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>

<a id="1100-table-6x28-1-usage-of-dicom-attributes-in-key-object-document-module-2"></a>
<table>
  <caption>1100 Table 6.X.2.8-1: Usage of DICOM Attributes in Key Object Document Module</caption>
  <thead>
    <tr><th>Referenced Request</th></tr>
  </thead>
  <tbody>
    <tr><td>Sequence</td></tr>
  </tbody>
</table>

<a id="1100-table-6x28-1-usage-of-dicom-attributes-in-key-object-document-module-3"></a>
<table>
  <caption>1100 Table 6.X.2.8-1: Usage of DICOM Attributes in Key Object Document Module</caption>
  <thead>
    <tr><th>Current Requested</th></tr>
  </thead>
  <tbody>
    <tr><td>Procedure Evidence</td></tr>
    <tr><td>Sequence</td></tr>
  </tbody>
</table>

<a id="1100-table-6x28-1-usage-of-dicom-attributes-in-key-object-document-module-4"></a>
<table>
  <caption>1100 Table 6.X.2.8-1: Usage of DICOM Attributes in Key Object Document Module</caption>
  <thead>
    <tr><th>(0040,A375)</th></tr>
  </thead>
  <tbody>
  </tbody>
</table>

<a id="1100-table-6x28-1-usage-of-dicom-attributes-in-key-object-document-module-5"></a>
<table>
  <caption>1100 Table 6.X.2.8-1: Usage of DICOM Attributes in Key Object Document Module</caption>
  <thead>
    <tr><th>List of all Composite SOP Instances references in Content</th></tr>
  </thead>
  <tbody>
    <tr><td>Sequence (0040,A730), including all presentation states, real</td></tr>
    <tr><td>world value maps and other accompanying composite instances</td></tr>
    <tr><td>that are referenced from the content items.</td></tr>
  </tbody>
</table>


<!-- page 48 -->

______________________________________________________________________________ 1-n Clinical Order Imaging Procedure Request (Placer Order Number) (Accession Number) 1-n 1-n 1-n Imaging Study (Study Instance UID) 1-n 1-n 1110


**Figure: 6.X.2.2.8.1-1: Entities Identifiers and their linkages**

The Referenced Request Sequence (0040,A370) contains the same number of items as the number of unique combinations of Accession Numbers and Placer Order Numbers associated with the Imaging Study. 1115 The following examples illustrate some possible combinations: 1. An intensive care physician orders a series of six portable chest x-rays for a patient, every 12 hours over 72 hours. o 1 Clinical Order o 6 Imaging Procedure Requests o 1120 6 Imaging Studies When the imaging manifest is created for each one of these 6 Imaging Studies, the Accession Number in the Study Module contains the Accession Number (corresponding to one of the Imaging Procedure Requests). In addition, if the Placer Order Number is known, the Referenced Request Sequence (0040,A370) contains one item for the unique 1125 combination of the Accession Number (corresponding to one of the Imaging Procedure Requests) and the Placer Order Number (corresponding to the clinical order). 2. An ED physician orders a chest CT and an abdominal CT for a patient in a tertiary care center. A single combined chest/abdominal CT is carried out and read by a single radiologist. o 1130 2 Clinical Orders o 1 Imaging Procedure Request o 1 Imaging Study


<!-- page 49 -->

______________________________________________________________________________ When the imaging manifest is created for the grouped imaging study, the Referenced Request Sequence (0040,A370) contains two items, one for the first Placer Order Number 1135 with the Accession Number and the second item for the second Placer Order Number with the same Accession Number. 3. An angiography procedure is ordered by a vascular surgeon. During the course of this radiology intervention, an ultrasound exam is performed in the Angio room. o 1 Clinical Order o 1140 1 Imaging Procedure Request o 2 Imaging Studies When the two imaging manifests are created, each manifest contains the same Accession Number in the Study Module. In addition, if the Placer Order Number is known, the Referenced Request Sequence (0040,A370) contains a single Item (Accession Number 1145 and Order Placer Number). 6.X.2.9 SR Document Content Module Implementers Note: DICOM CP 2595 is introducing a set of codes used by this profile. Since this IHE Radiology 1150 MADO Profile Trial Implementation text will be released before the DICOM CP becomes final text, IHE has issued temporary code values under the private coding scheme “99IHE”. These temporary codes will be replaced with the finalized DICOM codes upon approval of the DICOM CP-2595. 1155 The SR Document Content Module shall be constructed from TID 2010 “Key Object Selection” invoked at the root node. The TID 2010 “Key Object Selection” Template may include one or more Content Item of Value Type CODE and identified by EV (121023, DCM “Procedure Code”).

<a id="table-page-49-table-1"></a>
<table>
  <caption>Table (page 49, table 1)</caption>
  <thead>
    <tr><th>Placeholder Code
Value</th><th>Code Meaning</th><th>Temporary Code Value for IHE Trial
Implementation (99IHE)</th></tr>
  </thead>
  <tbody>
    <tr><td>ddd001</td><td>Manifest with Description</td><td>MADOTEMP001</td></tr>
    <tr><td>ddd003</td><td>Series Date</td><td>MADOTEMP003</td></tr>
    <tr><td>ddd004</td><td>Series Time</td><td>MADOTEMP004</td></tr>
    <tr><td>ddd002</td><td>Series Description</td><td>MADOTEMP002</td></tr>
    <tr><td>ddd007</td><td>Number of Series Related Instances</td><td>MADOTEMP007</td></tr>
    <tr><td>ddd009</td><td>Number of Study Related Series</td><td>MADOTEMP009</td></tr>
  </tbody>
</table>


<!-- page 50 -->

______________________________________________________________________________ 1160 The TID 2010 “Key Object Selection” Template shall include the TID 1600 “Image Library” Template. CID 7010 “Key Object Selection Document Title shall be set to: (MADOTEMP001, 99IHE, "Manifest with Description"). The MADO Profile relies on the DICOM Change Proposal CP-2595 that specifies the extension to the TID 2010 and the introduction of TID 1600. 1165 Reviewers Note: Until the above DICOM CP-2595 issued for March 2026 Voting Packet is approved by DICOM, IHE Radiology relies on this Voting Packet version of CP2595 for this Trial Implementation document. When approved by DICOM, the MADO TI version will be updated by removing this note. 1170 The TID 1600 “Image Library” Content Items shall be present as specified in Table 6.X.2.9-1: TID 1600 Template for SR Document Content Module of Manifest.


**Table 6.X.2.9-1: TID 1600 Template for SR Document Content Module of Manifest**

*Note: The High-level anatomic regions and systems value set defined in Section 6.X.6.4.1 High-Level Anatomic Regions and*

1175

*Systems Value Set is intended to be used for the metadata search parameter (See section 6.X.6.2 Imaging-Specific*

*Search Request Parameters) used to support filtering queries.*

<a id="table-6x29-1-tid-1600-template-for-sr-document-content-module-of-manifest"></a>
<table>
  <caption>Table 6.X.2.9-1: TID 1600 Template for SR Document Content Module of Manifest</caption>
  <thead>
    <tr><th>Rel with</th><th>VT</th><th>Concept Name</th><th>VM</th><th>Req</th><th>Condition</th><th>Value Set</th></tr>
  </thead>
  <tbody>
    <tr><td>Parent</td><td></td><td></td><td></td><td>Type</td><td></td><td>Constraint</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>CODE</td><td>EV (121139, DCM,
&quot;Modality&quot;)</td><td>1-n</td><td>R+</td><td></td><td>DCID 29 “Acquisition
Modality”
Non-acquisition
Modality from DCID 32
“Non-Acquisition
Modality” may be
included.</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>CODE</td><td>EV (123014, DCM,
&quot;Target Region&quot;)</td><td>1-n</td><td>R+</td><td></td><td>Code value for target
region selected. See
6.X.6.4.1 High-Level
Anatomic Regions and
Systems Value Set (See
Note below).</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>NUM</td><td>EV (MADOTEMP009,
99IHE, “Number of Study
Related Series”)</td><td>1</td><td>R+</td><td></td><td>UNITS = EV ({series},
UCUM, &quot;series&quot;)
This value shall reflect
the number of series in
the study as referenced
by the Current
Requested Procedure
Evidence Sequence
(0040,A375).</td></tr>
  </tbody>
</table>


<!-- page 51 -->

______________________________________________________________________________ Within the TID 1600 Image Library, each shared Series in the Manifest shall be represented by a distinct Image Library Group container. Within this container, the TID1602 “Image Library 1180 Entry Descriptors” Content Items shall be present as specified in Table 6.X.2.9-2: TID Template for SR Document Content Module of Manifest


**Table 6.X.2.9-2: TID 1602 Template for SR Document Content Module of Manifest**

<a id="table-6x29-2-tid-1602-template-for-sr-document-content-module-of-manifest"></a>
<table>
  <caption>Table 6.X.2.9-2: TID 1602 Template for SR Document Content Module of Manifest</caption>
  <thead>
    <tr><th>Rel with</th><th>VT</th><th>Concept Name</th><th>VM</th><th>Req</th><th>Condition</th><th>Value Set</th></tr>
  </thead>
  <tbody>
    <tr><td>Parent</td><td></td><td></td><td></td><td>Type</td><td></td><td>Constraint</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>CODE</td><td>EV (121139, DCM,
&quot;Modality&quot;)</td><td>1</td><td>R+</td><td></td><td>DCID 33
“Modality”</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>DATE</td><td>EV (MADOTEMP003,
99IHE, &quot;Series Date&quot;)</td><td>1</td><td>RC+</td><td>Shall be
populated if the
corresponding
attribute is
populated in the
relevant
instance(s).</td><td></td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>TIME</td><td>EV (MADOTEMP004,
99IHE, &quot;Series Time&quot;)</td><td>1</td><td>RC+</td><td>Shall be
populated if the
corresponding
attribute is
populated in the
relevant
instance(s).</td><td></td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>TEXT</td><td>EV (MADOTEMP002,
99IHE, “Series
Description”)</td><td>1</td><td>RC+</td><td>Shall be
populated if the
corresponding
attribute is
populated in the
relevant
instance(s).</td><td></td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>TEXT</td><td>EV (113607, DCM,
“Series Number”)</td><td>1</td><td>RC+</td><td>Shall be
populated if the
corresponding
attribute is
populated in the
relevant
instance(s).</td><td>The text string
shall be consistent
with the value of
Series Number
(0020,0011) of the
referenced series.</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>UIDREF</td><td>EV (112002, DCM,
“Series Instance UID”)</td><td>1</td><td>R+</td><td></td><td></td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>CODE</td><td>EV (123014, DCM,
&quot;Target Region&quot;)</td><td>1</td><td>RC+</td><td></td><td>This is a fine-
grained series level
anatomical region
recommended to
use DCID 4031 or
CID4</td></tr>
  </tbody>
</table>


<!-- page 52 -->

______________________________________________________________________________ Within the Image Library Group container, each shared Instance shall be represented by a 1185 distinct invocation of the TID 1601 Image Library Entry Template. Within each TID invocation, the Template TID 1602 is included. The TID 1602 “Image Library Entry Descriptors” Content Items shall be present as specified in Table 6.X.2.9-3: TID 1602 Template for SR Document Content Module of Manifest.


**Table 6.X.2.9-3: TID 1602 Template for SR Document Content Module of Manifest**

1190

*Note: It is important to note that no instance ordering semantics may be assumed from:*

*• The ordering of Sequence Items in Referenced SOP Sequence (0008,1199),*

*• The ordering of SOP Instances in Content Items of the SR Document Module under template TID 2010,*

<a id="table-page-52-table-1"></a>
<table>
  <caption>Table (page 52, table 1)</caption>
  <thead>
    <tr><th>Rel with</th><th>VT</th><th>Concept Name</th><th>VM</th><th>Req</th><th>Condition</th><th>Value Set</th></tr>
  </thead>
  <tbody>
    <tr><td>Parent</td><td></td><td></td><td></td><td>Type</td><td></td><td>Constraint</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>TEXT</td><td>EV (123014, DCM,
&quot;Target Region&quot;)</td><td>1</td><td>RC+</td><td></td><td>This is a fine-
grained series level
anatomical region</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>TEXT</td><td>EV (MADOTEMP007,
99IHE, “Number of Series
Related instances”)</td><td>1</td><td>R+</td><td></td><td>UNITS = EV
({instances},
UCUM,
&quot;instances&quot;)
This value shall
reflect the number
of instances in the
series of the study
as referenced in the
Current Requested
Procedure
Evidence Sequence
(0040,A375).</td></tr>
  </tbody>
</table>

<a id="table-6x29-3-tid-1602-template-for-sr-document-content-module-of-manifest"></a>
<table>
  <caption>Table 6.X.2.9-3: TID 1602 Template for SR Document Content Module of Manifest</caption>
  <thead>
    <tr><th>Rel with</th><th>VT</th><th>Concept Name</th><th>VM</th><th>Req
Type</th><th>Condition</th><th>Addtl Value Set</th></tr>
  </thead>
  <tbody>
    <tr><td>Parent</td><td></td><td></td><td></td><td></td><td></td><td>Constraint</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>NUM</td><td>EV (121140, DCM,
“Number of Frames”)</td><td>1</td><td>RC+</td><td>Required when
the SOP Class is
multiframe</td><td></td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>TEXT</td><td>EV (113609, DCM,
“Instance Number”)</td><td>1</td><td>RC+</td><td>Required when
present in the
referenced SOP
Instance</td><td>The text string shall
be consistent with the
value of Instance
Number (0020,0013)
of the referenced
instance (See Note).</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>INCLUDE</td><td>DTID 16XX Image
Library Entry
Descriptors for Key
Object Selection</td><td>1</td><td>RC+</td><td>Present if this
instance is a KOS
Object</td><td></td></tr>
  </tbody>
</table>


<!-- page 53 -->

______________________________________________________________________________

*• The ordering of SOP Instances in Content Items of the SR Document Module under template TID*

*• The order in which DICOM instances are received by the Imaging Document Consumer.*

1195

*Instance number(s), when present in the referenced SOP Instance of the imaging study manifest, offer a basic way to*

*order images when displayed without actually having retrieved all instances to gain access to image orientation and*

*image position attributes in the image headers.*

When a Key Object Selection instance is referenced, the TID 16XX “Image Library Entry Descriptors for Key Object Selection” Content Items shall be present as specified in Table 1200 6.X.2.9-4: TID 16XX Template for SR Document Content Module of Manifest. The Content Items contain information from the referenced KOS instance that allows the user of any Imaging Document Consumer to determine: • The presence of flagged significant images by a KOS instance (in a series of modality KO). 1205 • If a KOS flagging significant images, is relevant using the KOS Title code and if present, an associated description For each KOS selected as relevant, retrieve the KOS instance to identify the flagged images and retrieve them.


**Table 6.X.2.9-4: TID 16XX Template for SR Document Content Module of Manifest**

1210 The information allows retrieval of key images flagged as significant without first having to retrieve the list of KOS instances within the imaging study.

<a id="table-6x29-4-tid-16xx-template-for-sr-document-content-module-of-manifest"></a>
<table>
  <caption>Table 6.X.2.9-4: TID 16XX Template for SR Document Content Module of Manifest</caption>
  <thead>
    <tr><th>Rel with</th><th>VT</th><th>Concept Name</th><th>VM</th><th>Req</th><th>Condition</th><th>Addtl Value Set</th></tr>
  </thead>
  <tbody>
    <tr><td>Parent</td><td></td><td></td><td></td><td>Type</td><td></td><td>Constraint</td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>CODE</td><td>EV (121144, DCM,
&quot;Document Title&quot;)</td><td>1</td><td>R+</td><td></td><td></td></tr>
    <tr><td>HAS ACQ
CONTEXT</td><td>TEXT</td><td>EV (113012, DCM, “ Key
Object Description</td><td>1</td><td>RC+</td><td>Required
when
present in
the
referenced
KOS
instance</td><td></td></tr>
  </tbody>
</table>


<!-- page 54 -->

______________________________________________________________________________ 6.X.2.10 SOP Common Module


**Table 6.X.2.10-1: Usage of DICOM Attributes in SOP Common Module**

1215 6.X.2.11 Referenced Request Macro


**Table 6.X.2.11-1: Usage of DICOM Attributes in Referenced Request Macro**

<a id="table-6x210-1-usage-of-dicom-attributes-in-sop-common-module"></a>
<table>
  <caption>Table 6.X.2.10-1: Usage of DICOM Attributes in SOP Common Module</caption>
  <thead>
    <tr><th></th><th>Attributes from Table C.12-1 SOP Common Module</th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Attribute Name</td><td>Tag</td><td></td><td>IHE</td><td>Attribute Description</td><td>Attribute Description</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Usag</td><td></td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>e</td><td></td><td></td><td></td></tr>
    <tr><td>Timezone Offset
From UTC</td><td></td><td>(0008,0201)</td><td>R+</td><td></td><td></td><td>Contains the offset from UTC for the timezone in which the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td><td>manifest was created. It applies to all DA and TM Attributes of the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td><td>Manifest.</td><td></td></tr>
  </tbody>
</table>

<a id="table-6x211-1-usage-of-dicom-attributes-in-referenced-request-macro"></a>
<table>
  <caption>Table 6.X.2.11-1: Usage of DICOM Attributes in Referenced Request Macro</caption>
  <thead>
    <tr><th>Attributes from Table C.17-3c Referenced Request Macro Attributes</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td></td><td></td><td>Usage</td><td></td><td></td><td></td></tr>
    <tr><td>Study Instance UID</td><td>(0020,000D)</td><td>R+</td><td></td><td>Unique Identifier for the Study.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Copy of the referenced study’s Study Instance UID</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>(0020,000D).</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Note: There is a 1 to 1 relationship between this KOS</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>manifest and the study that this KOS manifest</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>references.</td><td></td></tr>
    <tr><td>Accession Number</td><td>(0008,0050)</td><td>R+</td><td></td><td>A departmental IS generated number that identifies the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>imaging order for the Study. Shall contain a value</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>associated with the Placer Order Number (0040,2016)</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>in the sequence item.</td><td></td></tr>
    <tr><td>Issuer of Accession Number
Sequence</td><td>(0008,0051)</td><td>R+</td><td></td><td>Identifier of the Assigning Authority that issued the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Accession Number (0008,0050). A value shall be</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>present.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Only a single Item shall be included in this Sequence.</td><td></td></tr>
    <tr><td>&gt;Include Table 6.X.2.12-1 “HL7v2 Hierarchic Designator Macro Attributes” – see section 6.X.2.12 HL7v2 Hierarchic
Designator Macro</td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Placer Order Number /
Imaging Service Request</td><td>(0040,2016)</td><td>R+</td><td></td><td>The order number assigned to the Imaging Service</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Request by the party placing the order.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Shall contain a value associated with the Accession</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Number (0008,0050) in the sequence item.</td><td></td></tr>
    <tr><td>Order Placer Identifier
Sequence</td><td>(0040,0026)</td><td>RC+</td><td></td><td>Identifier of the Assigning Authority that issued the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Placer Order Number (0040,2016).</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Required if Placer Order Number / Imaging Service</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Request (0040,2016) is not empty.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Only a single Item shall be included in this Sequence.</td><td></td></tr>
    <tr><td>&gt;Include Table 6.X.2.12-1 “HL7v2 Hierarchic Designator Macro Attributes” – see section 6.X.2.12 HL7v2 Hierarchic
Designator Macro</td><td></td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>


<!-- page 55 -->

______________________________________________________________________________ 6.X.2.12 HL7v2 Hierarchic Designator Macro


**Table 6.X.2.12-1: Usage of DICOM Attributes in HL7v2 Hierarchic Designator Macro**

6.X.2.13 Hierarchical SOP Instance Reference Macro


**Table 6.X.2.13-1: Usage of DICOM Attributes in Hierarchical SOP Instance Reference**


**Macro**

1225

*Note: Since the IHE Radiology MADO Profile Trial Implementation has been released prior to the CP 2595 reaching approval*

*in DICOM WG 6, a temporary DICOM Private Tag will be used in lieu of “DICOM Display URI Tag (gggg,eeee)”.*

<a id="table-6x212-1-usage-of-dicom-attributes-in-hl7v2-hierarchic-designator-macro"></a>
<table>
  <caption>Table 6.X.2.12-1: Usage of DICOM Attributes in HL7v2 Hierarchic Designator Macro</caption>
  <thead>
    <tr><th>Attributes from Table 10-17 HL7v2 Hierarchic Designator Macro Attributes</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE
Usage</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td>Universal Entity ID</td><td>(0010,0032)</td><td>R+</td><td>Globally unique identifier for the Assigning Authority.</td><td></td><td></td></tr>
    <tr><td>Universal Entity ID Type</td><td>(0010,0033)</td><td>RC+</td><td></td><td>Standard defining the format of the Universal Entity</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>ID.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>(e.g. value: “ISO” for an OID format)</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Required if Universal Entity ID (0010,0032) is present.</td><td></td></tr>
  </tbody>
</table>

<a id="table-6x212-1-usage-of-dicom-attributes-in-hl7v2-hierarchic-designator-macro-2"></a>
<table>
  <caption>Table 6.X.2.12-1: Usage of DICOM Attributes in HL7v2 Hierarchic Designator Macro</caption>
  <thead>
    <tr><th>IHE</th></tr>
  </thead>
  <tbody>
    <tr><td>Usage</td></tr>
  </tbody>
</table>

<a id="table-6x213-1-usage-of-dicom-attributes-in-hierarchical-sop-instance-reference"></a>
<table>
  <caption>Table 6.X.2.13-1: Usage of DICOM Attributes in Hierarchical SOP Instance Reference</caption>
  <thead>
    <tr><th>Attributes from Table C.17-3 Hierarchical SOP Instance Reference Macro Attributes</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE
Usage</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td>Study Instance UID</td><td>(0020,000D)</td><td>R</td><td></td><td>Unique identifier for the Study.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Copy of the referenced study’s Study Instance UID</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>(0020,000D).</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Note: There is a 1 to 1 relationship between this KOS</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>manifest and the study that this KOS manifest</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>references.</td><td></td></tr>
    <tr><td>Display URI</td><td>(gggg.eeee)
(See Note for
temporary TI
private tag)</td><td>O</td><td></td><td>The value of this attribute is an opaque URI that results</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>in launching a remote viewing application for the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>imaging study summarized by the imaging study</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>manifest (See the concepts described in section X.4.1.7</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Launching a Remote Image Display).</td><td></td></tr>
    <tr><td>Referenced Series Sequence</td><td>(0008,1115)</td><td>R</td><td></td><td>Sequence of Items where each item includes the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Attributes of a Series containing referenced Composite</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Object(s)</td><td></td></tr>
    <tr><td>&gt; Include Table 6.X.2.12-1 “HL7v2 Hierarchic Designator Macro Attributes” – see section 6.X.2.12 HL7v2 Hierarchic
Designator Macro</td><td></td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>

<a id="table-6x213-1-usage-of-dicom-attributes-in-hierarchical-sop-instance-reference-2"></a>
<table>
  <caption>Table 6.X.2.13-1: Usage of DICOM Attributes in Hierarchical SOP Instance Reference</caption>
  <thead>
    <tr><th>IHE</th></tr>
  </thead>
  <tbody>
    <tr><td>Usage</td></tr>
  </tbody>
</table>

<a id="table-6x213-1-usage-of-dicom-attributes-in-hierarchical-sop-instance-reference-3"></a>
<table>
  <caption>Table 6.X.2.13-1: Usage of DICOM Attributes in Hierarchical SOP Instance Reference</caption>
  <thead>
    <tr><th>Display URI</th></tr>
  </thead>
  <tbody>
  </tbody>
</table>

<a id="table-6x213-1-usage-of-dicom-attributes-in-hierarchical-sop-instance-reference-4"></a>
<table>
  <caption>Table 6.X.2.13-1: Usage of DICOM Attributes in Hierarchical SOP Instance Reference</caption>
  <thead>
    <tr><th>(gggg.eeee)</th></tr>
  </thead>
  <tbody>
    <tr><td>(See Note for</td></tr>
    <tr><td>temporary TI</td></tr>
    <tr><td>private tag)</td></tr>
  </tbody>
</table>


<!-- page 56 -->

______________________________________________________________________________

*This IHE Private tag is a temporary tag value to be replaced with the DICOM assigned Tag for Display URI upon*

*approval of the CP 2595 by DICOM.*

6.X.2.14 Hierarchical Series Reference Macro 1230


**Table 6.X.2.14-1: Usage of DICOM Attributes in Hierarchical Series Reference Macro**

6.X.3 HL7 FHIR Based Imaging Study Manifest Content Definitions This section specifies the structure and format of an Imaging Study Manifest for the MADO

<a id="table-page-56-table-1"></a>
<table>
  <caption>Table (page 56, table 1)</caption>
  <thead>
    <tr><th></th><th>Tag</th><th></th><th></th><th>Private Creator</th><th></th><th></th><th>VR</th><th></th><th></th><th>VM</th><th></th><th></th><th>Attribute Name</th><th></th><th></th><th>Attribute Description</th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>(000D,00xx)</td><td></td><td></td><td>IHE_MADO_PRIVATE</td><td></td><td></td><td>LO</td><td></td><td></td><td>1</td><td></td><td></td><td>IHE MADO
Private Creator ID</td><td></td><td></td><td>Private Creator ID</td><td></td><td></td></tr>
    <tr><td>(000D,xx01)</td><td></td><td></td><td>IHE_MADO_PRIVATE</td><td></td><td></td><td>UR</td><td></td><td></td><td>1</td><td></td><td></td><td>Display URI</td><td></td><td></td><td>URI specifying the
access path to a remote
image display service
for the Study.
Temporary until
DICOM CP2595 is
approved (June 2026).</td><td></td><td></td></tr>
  </tbody>
</table>

<a id="table-6x214-1-usage-of-dicom-attributes-in-hierarchical-series-reference-macro"></a>
<table>
  <caption>Table 6.X.2.14-1: Usage of DICOM Attributes in Hierarchical Series Reference Macro</caption>
  <thead>
    <tr><th>Attributes from Table C.17-3a Hierarchical Series Reference Macro Attributes</th><th></th><th></th><th></th><th></th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>Attribute Name</td><td>Tag</td><td>IHE
Usage</td><td>Attribute Description</td><td></td><td></td></tr>
    <tr><td>Retrieve Location UID</td><td>(0040,E011)</td><td>R+</td><td></td><td>Unique identifier of the system where the Composite</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Object(s) may be retrieved on the network.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>The value of this attribute is an OID that may be used</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>as a reference to obtain the endpoint of the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>corresponding WADO-RS service returned as a Base</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>URI (See concept section X.4.1.2 Intra-community</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>sharing infrastructure).</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>WADO-RS retrieval URLs can be composed by the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>consumer using this Base URI and the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>study/series/instance UIDs from this manifest.</td><td></td></tr>
    <tr><td>Retrieve URL</td><td>(0008,1190)</td><td>O</td><td></td><td>URL specifying the location of the referenced</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Instance(s).</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>The value of this attribute is a Base URI representing</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>the endpoint for the corresponding WADO-RS service</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>(See concept section X.4.1.2 Intra-community sharing</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>infrastructure).</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>WADO-RS retrieval URL can be composed by the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>consumer using this Base URI and the</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>study/series/instance UIDs from this manifest.</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>Note: The definition of this Retrieve URL being a Base</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>URI aligns with its use in the IHE XDS-I.b profile</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>(DICOM Retrieve by WADO-RS option) and the IHE</td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td>XC-WADO profile.</td><td></td></tr>
  </tbody>
</table>

<a id="table-6x214-1-usage-of-dicom-attributes-in-hierarchical-series-reference-macro-2"></a>
<table>
  <caption>Table 6.X.2.14-1: Usage of DICOM Attributes in Hierarchical Series Reference Macro</caption>
  <thead>
    <tr><th>IHE</th></tr>
  </thead>
  <tbody>
    <tr><td>Usage</td></tr>
  </tbody>
</table>


<!-- page 57 -->

______________________________________________________________________________ Profile using the HL7 FHIR standard. It is based on the FHIR Imaging Study resource as 1235 specified by the FHIR Release 4 and other related FHIR Release 4 resources in the form of a FHIR Implementation Guide, which is an integral part of the MADO Profile. The MADO HL7 FHIR Imaging Study Manifest specification is under finalization and the development version may be accessed at: https://build.fhir.org/ig/IHE/RAD.MADO/branches/master/fhir-imaging-manifest.html 1240

*Note: To focus on the imaging manifest go to the “Artifacts tab” in the top bar. Then, when accessing the different resource*

*profiles, it automatically selects the "Key Elements" tab which does not show all elements in the resource.*

When shared with MHD, MHDS, or XDS.b document sharing profiles, the Imaging Study Manifest, shall use the following Format Code. 1245 6.X.4 MHD Envelope Content Definitions This section specifies the structure and content of an envelope based on a FHIR Document Reference resource as specified by the FHIR Release 4 in the form of a FHIR Implementation Guide, which is an integral part of the MADO Profile. This MADO HL7 FHIR Envelope 1250 specification shall be used in conjunction with the IHE MHD or MHDS Profiles when the imaging study manifest is shared in a FHIR-Based Format or a DICOM KOS-Based Format (See X.6.1 and X.6.2). This envelope specification is under finalization and the development version may be accessed at: https://build.fhir.org/ig/IHE/RAD.MADO/branches/master/manifest-envelope.html. 1255 6.X.5 DICOM – FHIR Manifest Format Mapping Specification This section specifies the mapping between the two imaging study manifest formats specified in section 6.X.2 and 6.X.3. It enhances the ability to bridge between infrastructures that may have chosen to deploy different imaging study manifest formats. This mapping is under finalization and the development version may be accessed at: 1260 https://build.fhir.org/ig/IHE/RAD.MADO/branches/master/mapping.html. Such mapping is not currently required by the MADO Profile. 6.X.6 Imaging Study Manifest Search Metadata A set of search parameters is defined in this section for the search of imaging study manifests. 1265 These functional requirements ensure a uniform access to imaging study manifest irrespective of the document sharing infrastructure used.

<a id="table-page-57-table-1"></a>
<table>
  <caption>Table (page 57, table 1)</caption>
  <thead>
    <tr><th></th><th>Format Code</th><th></th><th></th><th>Coding Scheme</th><th></th><th></th><th>Description</th><th></th></tr>
  </thead>
  <tbody>
    <tr><td>urn:ihe:rad:MADO:fhir-manifest:2026</td><td></td><td></td><td>1.3.6.1.4.1.19376.1.2.7.1</td><td></td><td></td><td>MADO FHIR-based
Imaging Study Manifest</td><td></td><td></td></tr>
  </tbody>
</table>


<!-- page 58 -->

______________________________________________________________________________ It is expected that the search Document Consumer Actors of the document sharing infrastructure grouped with MADO, will support these search parameters. These parameters have been selected based on the experience with deployments of XDS-I.b and 1270 MHD (Comprehensive Metadata option). They are directly supported by the XDS.b, XDS-I.b, XCA, XCA-I, MHD and MHDS profiles. Any given query might use only a subset of these search parameters. 6.X.6.1 Generic Search Request Parameters The following search request parameters are generic (not specific to imaging): 1275 • Patient Business Identifier – patient id • Period – the time of service. As a search parameter, it matches when the requested interval overlaps with the period or time of service. Note: The time of service for an Imaging Manifest Doc is the Study Date and Time. • Document Creation Date/Time - date/time the imaging study manifest was created. . This 1280 is intended to facilitate finding manifest published or revised after a certain date and time. • Category – class of document (e.g., images or reports) • Practice Setting – specialty where care was performed/provided (e.g., radiology, cardiology, surgery, endoscopy for imaging study manifest) 6.X.6.2 Imaging-Specific Search Request Parameters 1285 The following search request parameters are specific to imaging: • Modality • Anatomical Region - body part • Study Instance UID • Accession Number (include Issuer of Accession Number to ensure uniqueness) 1290 • Placer Order Number 6.X.6.3 Return Response Parameters For each matching entry, a response will be returned to the consumer. It is expected that this response contains not only the values of the search parameters conveyed by the query request, but the complete list of values for all supported search parameters, plus some additional 1295 parameters that are returned. These returned parameter values may be used by the Health Professional or an application to select any relevant imaging study manifest of interest which can then be retrieved through the document sharing infrastructure. The list of returned parameters are:


<!-- page 59 -->

______________________________________________________________________________ • Repository Location Unique Identifier - The document repository from which the 1300 document can be retrieved. • Document Identifier • Document Creation Date/Time • Document Type • Document Format 1305 • Document Mime Type • Document Author(s) • Document Organization Name and ID • Document Category (high-level type) • Practice Setting (high-level specialty) 1310 • Order identifier(s) • Procedure code(s) • Modality type(s) • Anatomical Regions (high-level value set) • Study Instance UID 1315 • Accession Number(s) (include Issuer of Accession Number to ensure uniqueness) • Placer Order Number(s) 6.X.6.4 Anatomical Region Value Set The Anatomical Region Value Set is defined as a short set of anatomical region values optimized for use as a search parameter, to facilitate a coarse grain filtering among large numbers of 1320 imaging studies, performed across a wide range of treatment specialties and imaging modalities. Coarse grain filtering on anatomical regions needs to rely on a short classification set, meaning: • Typically, only one or two values, rarely more, are needed to identify, at a high-level, the anatomies associated with most imaging procedures, thus making the mapping of imaging procedure to such high-level anatomy easy and simple to check for correctness 1325 when deployed across many sites. • When expressing a query filter, one should avoid a long pull-down menu of 20, 30 or more values to be presented to the Health Professional to scroll through, to set the filter in a query.


<!-- page 60 -->

______________________________________________________________________________ • Deploying such a shared short set is simple even with large numbers of local imaging 1330 procedures (point 1 above) and it lends itself to a robust selection process (point 2 above) by the requester, resulting in avoiding false negative query matches Example of mapping process: A possible way to select the right value(s) of anatomical regions is to automate the mapping at the time the imaging order is processed by the imaging department: 1. Today, it is typical that when processing incoming clinical orders, one or more imaging 1335 procedure request(s) are created with a corresponding imaging procedure code selected. Such an imaging procedure code comes from a value set (typically around a thousand values) that may be locally defined or nationally standardized, based on ad-hoc or international terminologies. 2. This variety of terminologies used for imaging procedure codes is not a barrier to define a 1340 mapping for each imaging procedure codes used locally to one or more anatomical region(s) from the high-level Anatomical Regions and Systems value set defined in Table 6.X.6.4-1: CID IHE-MADO1 High-Level Anatomic Regions and Systems. 3. This process could be automated by the order processing application at the departmental level. The imaging modalities may continue to manage anatomical codes as they do 1345 today.


**Table 6.X.6.4-1: CID IHE-MADO1 High-Level Anatomic Regions and Systems**

<a id="table-6x64-1-cid-ihe-mado1-high-level-anatomic-regions-and-systems"></a>
<table>
  <caption>Table 6.X.6.4-1: CID IHE-MADO1 High-Level Anatomic Regions and Systems</caption>
  <thead>
    <tr><th></th><th>Type:</th><th></th><th>Extensible</th></tr>
  </thead>
  <tbody>
    <tr><td>FHIR Keyword:</td><td></td><td></td><td>IHE-MADO1-
HighLevelAnatomicRegionsAndSystems</td></tr>
    <tr><td></td><td>Keyword:</td><td></td><td>HighLevelAnatomicRegionsAndSystems</td></tr>
    <tr><td></td><td>Version:</td><td></td><td>20260227</td></tr>
    <tr><td></td><td>UID:</td><td></td><td>1.3.6.1.4.1.19376.1.1.86.1</td></tr>
    <tr><td></td><td>Context Group ID:</td><td></td><td>CID IHE-MADO1</td></tr>
  </tbody>
</table>

<a id="table-6x64-1-cid-ihe-mado1-high-level-anatomic-regions-and-systems-2"></a>
<table>
  <caption>Table 6.X.6.4-1: CID IHE-MADO1 High-Level Anatomic Regions and Systems</caption>
  <thead>
    <tr><th>Coding Scheme</th><th></th><th></th><th>Corresponding</th></tr>
  </thead>
  <tbody>
    <tr><td>Designator</td><td>Code Value</td><td>Code Meaning</td><td>DICOM Body Part Examined</td></tr>
    <tr><td>SCT</td><td>63337009</td><td>Lower trunk</td><td>LOWERTRUNK</td></tr>
    <tr><td>SCT</td><td>38266002</td><td>Entire body</td><td>WHOLEBODY</td></tr>
    <tr><td>SCT</td><td>53120007</td><td>Upper limb</td><td>UPPERLIMB</td></tr>
    <tr><td>SCT</td><td>61685007</td><td>Lower limb</td><td>LOWERLIMB</td></tr>
    <tr><td>SCT</td><td>67734004</td><td>Upper trunk</td><td>UPPERTRUNK</td></tr>
    <tr><td>SCT</td><td>774007</td><td>Head and neck</td><td>HEADNECK</td></tr>
  </tbody>
</table>


<!-- page 61 -->

______________________________________________________________________________

*Note: The above codes and associated definitions are an extract from DICOM CID-4031, except (1141981001, SCT,*

*”Vertebral Column”) which is defined as a region in SNOMED CT replaces (421060004, SCT, “Spine”) which*

1350

*technically only covers the bony structure of the spine. The DICOM Body Part Examined retains the value of SPINE*

*because it is common usage.*

<a id="table-page-61-table-1"></a>
<table>
  <caption>Table (page 61, table 1)</caption>
  <thead>
    <tr><th>Coding Scheme</th><th></th><th></th><th>Corresponding</th></tr>
  </thead>
  <tbody>
    <tr><td>Designator</td><td>Code Value</td><td>Code Meaning</td><td>DICOM Body Part Examined</td></tr>
    <tr><td>SCT</td><td>113257007</td><td>Cardiovascular system</td><td>CARDIOVASCSYS</td></tr>
    <tr><td>SCT</td><td>80891009</td><td>Heart</td><td>HEART</td></tr>
    <tr><td>SCT</td><td>76752008</td><td>Breast</td><td>BREAST</td></tr>
    <tr><td>SCT</td><td>1141981001</td><td>Vertebral Column</td><td>SPINE</td></tr>
  </tbody>
</table>


<!-- page 62 -->

______________________________________________________________________________


<a id="appendices-to-volume-3"></a>
# Appendices to Volume 3


<!-- page 63 -->

______________________________________________________________________________


<a id="appendix-a-mapping-of-mado-search-parameters-to-mhd-and"></a>
## Appendix A – Mapping of MADO Search Parameters to MHD and

1355


<a id="xdsb-metadata"></a>
## XDS.b Metadata

This appendix provides information on the mappings between the named MADO Search & Return parameters (see RAD TF-3: Section 6.X.6 Imaging Study Manifest Search Metadata) and: 1360 1. MHD FHIR DocumentReference metadata 2. XDS.b DocumentEntry metadata These mappings are not intended to be used as MHD FHIR DocumentReference to/from XDS.b DocumentEntry mappings although they are based on the IHE MHD – “XDS-on-FHIR” Comprehensive DocumentReference Mappings. 1365 The Cardinality and Value Sets are not defined but left to the detailed Implementation Guides (to be defined). Table A-1 defines the general search request parameter mappings to MHD and XDS.b.


**Table A-1: MADO Generic Search Request Parameters**

1370 Table A-2 defines the imaging specific search request parameter mappings to MHD and XDS.b.


**Table A-2: MADO Imaging Specific Search Request Parameters**

<a id="table-a-1-mado-generic-search-request-parameters"></a>
<table>
  <caption>Table A-1: MADO Generic Search Request Parameters</caption>
  <thead>
    <tr><th>MADO Name</th><th></th><th></th><th></th><th>MHD FHIR</th><th></th><th>XDS.b DocumentEntry</th></tr>
  </thead>
  <tbody>
    <tr><td></td><td></td><td></td><td></td><td>DocumentReference</td><td></td><td></td></tr>
    <tr><td></td><td>Patient Business</td><td></td><td>patient.identifier</td><td>patient.identifier</td><td></td><td>patientId</td></tr>
    <tr><td></td><td>Identifier</td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Period</td><td>Period</td><td></td><td></td><td>period.start</td><td></td><td>serviceStartTime</td></tr>
    <tr><td></td><td></td><td></td><td></td><td>period.end</td><td></td><td>serviceStopTime</td></tr>
    <tr><td></td><td>Document Creation</td><td></td><td>creation</td><td>creation</td><td></td><td>creationTime</td></tr>
    <tr><td></td><td>Date/Time</td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td></td><td>Category</td><td></td><td>category</td><td></td><td></td><td>classCode</td></tr>
    <tr><td></td><td>Practice Setting</td><td></td><td></td><td>setting</td><td></td><td>practiceSettingCode</td></tr>
  </tbody>
</table>

<a id="table-a-2-mado-imaging-specific-search-request-parameters"></a>
<table>
  <caption>Table A-2: MADO Imaging Specific Search Request Parameters</caption>
  <thead>
    <tr><th>MADO Name</th><th></th><th>MHD FHIR</th><th></th><th>XDS.b DocumentEntry</th></tr>
  </thead>
  <tbody>
    <tr><td></td><td></td><td>DocumentReference</td><td></td><td></td></tr>
    <tr><td>Modality Type</td><td>context.event
[Modality]</td><td></td><td></td><td>eventCodeList
[Modality]</td></tr>
    <tr><td>Anatomical Region</td><td>context.event
[Atomic Region/Body Part]</td><td></td><td></td><td>eventCodeList
[Atomic Region/Body Part]</td></tr>
    <tr><td>Study Instance UID</td><td>related
[referenced ImagingStudy.identifier
(Study Instance UID)]</td><td></td><td></td><td>referenceIdList
[urn:ihe:iti:xds:2016:studyInstanceUID]</td></tr>
  </tbody>
</table>

<a id="table-a-2-mado-imaging-specific-search-request-parameters-2"></a>
<table>
  <caption>Table A-2: MADO Imaging Specific Search Request Parameters</caption>
  <thead>
    <tr><th>referenceIdList</th></tr>
  </thead>
  <tbody>
    <tr><td>[urn:ihe:iti:xds:2016:studyInstanceUID]</td></tr>
  </tbody>
</table>


<!-- page 64 -->

______________________________________________________________________________ Table A-3 defines the return response parameter mappings to MHD and XDS.b.


**Table A-3: MADO Return Response Parameters**

1375 Table A-4 defines some additional technical return response parameter mappings to MHD and XDS.b. The parameters are not explicitly named in the MADO Profile.


**Table A-4: Additional Technical Return Response Parameters**

<a id="table-page-64-table-1"></a>
<table>
  <caption>Table (page 64, table 1)</caption>
  <thead>
    <tr><th>MADO Name</th><th></th><th>MHD FHIR
DocumentReference</th><th>XDS.b DocumentEntry</th></tr>
  </thead>
  <tbody>
    <tr><td>Accession Number</td><td>related
[referenced ImagingStudy.identifier
(Accession Number)]</td><td></td><td>referenceIdList</td></tr>
    <tr><td></td><td></td><td></td><td>[urn:ihe:iti:xds:2013:accession]</td></tr>
    <tr><td>Order identifier</td><td>related
[referenced ServiceRequest.identifier
(Order Identifier)]</td><td></td><td>referenceIdList</td></tr>
    <tr><td></td><td></td><td></td><td>[urn:ihe:iti:xds:2013:order]</td></tr>
  </tbody>
</table>

<a id="table-a-3-mado-return-response-parameters"></a>
<table>
  <caption>Table A-3: MADO Return Response Parameters</caption>
  <thead>
    <tr><th>MADO Name</th><th></th><th>MHD FHIR
DocumentReference</th><th>XDS.b DocumentEntry</th></tr>
  </thead>
  <tbody>
    <tr><td>Repository Location
Unique Identifier</td><td>content.attachment.url</td><td></td><td>repositoryUniqueId + uniqueId
or URI</td></tr>
    <tr><td>Document Identifier</td><td>masterIdentifier</td><td></td><td>uniqueId</td></tr>
    <tr><td>Document Type</td><td>type</td><td></td><td>typeCode</td></tr>
    <tr><td>Document Format</td><td>content.format</td><td></td><td>formatCode</td></tr>
    <tr><td>Document Mime
Type</td><td>content.attachment.contentType</td><td></td><td>mimeType</td></tr>
    <tr><td>Document
Author(s)</td><td>author</td><td></td><td>author.authorPerson</td></tr>
    <tr><td>Document
Organization Name
and ID</td><td>custodian</td><td></td><td>author.authorInstitution</td></tr>
    <tr><td>Order identifier(s)</td><td>related
[referenced ServiceRequest.identifier
(Order Identifier)]</td><td></td><td>referenceIdList
[urn:ihe:iti:xds:2013:order]</td></tr>
    <tr><td>Procedure code(s)</td><td>related
[referenced
ImagingStudy.procedureCode]</td><td></td><td>eventCodeList
[DICOM Imaging Procedure Code –
DisplayName]</td></tr>
  </tbody>
</table>

<a id="table-a-4-additional-technical-return-response-parameters"></a>
<table>
  <caption>Table A-4: Additional Technical Return Response Parameters</caption>
  <thead>
    <tr><th></th><th>MADO Name</th><th></th><th></th><th>MHD FHIR DocumentReference</th><th></th><th>XDS.b DocumentEntry</th><th></th></tr>
  </thead>
  <tbody>
    <tr><td></td><td></td><td></td><td>identifier:entryUUID</td><td></td><td>entryUUID</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>status</td><td></td><td>availabilityStatus</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>authenticator</td><td></td><td>legalAuthenticator</td><td></td><td></td></tr>
  </tbody>
</table>


<!-- page 65 -->

______________________________________________________________________________

<a id="table-page-65-table-1"></a>
<table>
  <caption>Table (page 65, table 1)</caption>
  <thead>
    <tr><th></th><th>MADO Name</th><th></th><th></th><th>MHD FHIR DocumentReference</th><th></th><th></th><th>XDS.b DocumentEntry</th><th></th></tr>
  </thead>
  <tbody>
    <tr><td></td><td></td><td></td><td>description</td><td></td><td></td><td>comments</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>securityLabel</td><td></td><td></td><td>confidentialityCode</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>content.attachment.language</td><td></td><td></td><td>languageCode</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>content.attachment.size</td><td></td><td></td><td>size</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>content.attachment.hash</td><td></td><td></td><td>hash</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>content.attachment.title</td><td></td><td></td><td>title</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>context.encounter</td><td></td><td></td><td>referenceIdList [ihe:iti:xds:2015:encounterId]</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>context.facilityType</td><td></td><td></td><td>healthcareFacilityTypeCode</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>context.sourcePatientInfo.reference</td><td></td><td></td><td>sourcePatientInfo</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td>context.sourcePatientInfo.identifier</td><td></td><td></td><td>sourcePatientId</td><td></td><td></td></tr>
  </tbody>
</table>
