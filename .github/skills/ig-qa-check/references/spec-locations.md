# Specification Locations

This file is the persistent location memory for the `ig-qa-check` skill. It records web locations used when checking dependency references. Treat `sushi-config.yaml` in the target IG as authoritative for the configured version; verify these locations against the current build and dependency metadata before relying on them.

| Package or specification | Version observed | Build or current location | Release or versioned location | Verification status |
|---|---:|---|---|---|
| IHE RAD MADO (`ihe.rad.mado`) | `dev` | https://build.fhir.org/ig/IHE/RAD.MADO/ | None recorded; use the build location for `dev` | Verify during each QA run |
| IHE ITI MHD (`ihe.iti.mhd`) | `4.2.3` | https://profiles.ihe.net/ITI/MHD/ | Release-specific path not recorded | Verify against the dependency release metadata |
| HL7 EU Base (`hl7.fhir.eu.base`) | `2.0.0` | https://build.fhir.org/ig/hl7-eu/base-r5/ | Version-specific path not recorded | Verify against the package version and FHIR release |
| HL7 Europe Extensions R4 (`hl7.fhir.eu.extensions.r4`) | `1.3.0` | https://build.fhir.org/ig/hl7-eu/extensions-r4/ | Canonical ImplementationGuide: http://hl7.eu/fhir/extensions/ImplementationGuide/hl7.fhir.eu.extensions | Verify against the R4 package metadata |
| FHIR cross-version extensions R5-to-R4 (`hl7.fhir.uv.xver-r5.r4`) | `0.1.0` | https://hl7.org/fhir/uv/xver-r5.r4/0.1.0/ | Same versioned location | Verify against the package metadata |
| Xt-EHR common / imaging | External | https://build.fhir.org/ig/Xt-EHR/xt-ehr-common/en/ | Versioned links may occur in mapping pages | Verify the version in each source link |
| HL7 Europe Imaging Report | External | https://build.fhir.org/ig/hl7-eu/imaging-r4/ | Versioned release not recorded | Verify the intended release before publication |
| EU Health Data API | External | https://build.fhir.org/ig/euridice-org/eu-health-data-api/en/ | Versioned release not recorded | Verify the intended release before publication |
| DICOM SR to FHIR | External | https://build.fhir.org/ig/HL7/dicom-sr/ | Versioned links may occur in source pages | Verify the version in each source link |

## Maintenance Rules

- Add or change an entry only after confirming the location from `sushi-config.yaml`, dependency package metadata, a fresh build, or an authoritative published specification page.
- Keep `dev` and `build` dependencies mapped to their `build.fhir.org` locations.
- Do not infer a release URL from a package id alone. Record `not recorded` and verify it during the QA run when the exact release path is unknown.
- Keep canonical FHIR URLs separate from documentation URLs; a canonical is not automatically a navigational link.
- When a QA run discovers a corrected or new location, update this file with the observed version and verification status so later runs can reuse it.
- Do not record generated output paths, local cache paths, credentials, access tokens, or other secrets.
