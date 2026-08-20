# index.md Coverage Analysis

Analysis of `imaging-manifest-fork/input/pagecontent/index.md` against the IG's actual content (as of 2026-08-20).

## What the IG actually contains

- **11 profiles**: `EuMadoBundle`, `EuMadoComposition`, `EuMadoImagingStudy`, `EuMadoPatient`, `EuMadoCreatorOrganization`, `EuMadoCreator` (Device), `EuMadoRequestedProcedure` (ServiceRequest), `EuMadoWebViewerEndpoint`, `EuMadoWadoEndpoint`, `EuMadoFhirDocumentReference`, `EuMadoDicomKosDocumentReference`
- **3 ActorDefinitions** (Producer, Consumer, MHD Document Responder) + **1 CapabilityStatement**
- **Content pages**: functional-requirements, EHDS logical model mapping (xtehr-mapping), Volumes 1/2/3, FHIR manifest, DICOM KOS manifest, MHD envelopes, FHIR/KOS mappings, changes, current-status
- **Terminology** (anatomical region, procedure type, etc.) and **DICOM KOS examples** under `examples/dicom/kos`

## What index.md covers well

- **Scope, Purpose, Relationship/scope boundaries** — the report-vs-manifest separation and EHDS/MyHealth@EU framing are clear and accurate.
- **Structure** — correctly describes the IHE supplement skeleton (Vol1 actors/transactions, Vol2 WADO-RS, Vol3 manifest content: A=DICOM KOS, B=FHIR, C=mapping). This maps onto the real pages.
- **Summary of differences** — the EU-profile reuse, Xt-EHR mapping, and anatomical-region requirement are all real deliverables.

## Gaps — recommended changes

1. **The dual-manifest nature is underplayed.** The IG delivers **two** manifest representations — a **FHIR Bundle** manifest and a **DICOM KOS** manifest, plus **MHD envelopes** — but the Scope bullet only says "FHIR imaging study manifests." The DICOM KOS manifest and MHD packaging are equally central. Add them explicitly to Scope.

2. **No orientation/navigation to the content.** The home page never links to the key pages a reader needs (Functional Requirements, EHDS logical-model mapping, the FHIR/KOS/envelope manifest pages) or to the **Artifacts** page / profile list. Everything below "Structure" is auto-generated boilerplate (dependencies, cross-version, IP). Add a short "How to read this guide" section linking the volumes and the profile artifacts.

3. **Actors are invisible.** The IG defines Producer, Consumer, and MHD Document Responder actors + a CapabilityStatement. "Structure" mentions Volume 1 actor/transactions abstractly but never names or links them. Add a sentence pointing to them.

4. **Possible over-claim on examples.** Scope says *"Example implementations of the defined models for Imaging Study Manifests."* However, this IG generates **zero FHIR example instances** — the only examples present are DICOM KOS files under `examples/dicom/`. Either add the FHIR examples, or reword the bullet to reflect that examples are DICOM-KOS-oriented (or hosted externally). This is the one place where the index and the built IG genuinely disagree.

5. **Terminology not mentioned.** The mandated anatomical-region value set is in "Summary of differences," but the broader terminology work (procedure types, performer types, endpoint codes) gets no mention. Minor, optional.

6. **Minor wording.** "In term of structure of the profile here the skeleton:" reads awkwardly — worth a light copyedit.

## Bottom line

index.md gives a solid **conceptual** overview (scope, purpose, ecosystem positioning) but functions poorly as a **map of the IG's deliverables**. The most important substantive fixes are **#1** (surface the DICOM KOS + MHD manifests in Scope) and **#4** (reconcile the "example implementations" claim with the fact that no FHIR examples are built). #2 and #3 would materially improve navigability.
