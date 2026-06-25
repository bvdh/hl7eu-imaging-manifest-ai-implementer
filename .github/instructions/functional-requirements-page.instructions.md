---
description: "Guidance for maintaining the functional-requirements page for the HL7 Europe Imaging Manifest IG."
applyTo: "imaging-manifest-fork/input/pagecontent/functional-requirements.md"
---

This instruction applies when editing `functional-requirements.md`.

- Goal: explain the EU-specific functional requirements of this implementation guide and make the delta relative to IHE MADO explicit.
- Audience: implementers, reviewers, and specification readers who need a concise explanation of what this guide adds on top of IHE MADO.
- Tone: factual, specification-oriented, and concise.

## Required content

When rewriting or extending this page, keep the following points explicit:

- State that this implementation guide provides EU-specific requirements and content on top of IHE MADO.
- Mention alignment with the EU Health Data API:
  `https://build.fhir.org/ig/euridice-org/eu-health-data-api/en/`
- State that the guide supports Xt-EHR requirements for ImagingStudy and related EHDS imaging concepts.
- Mention that the guide provides an explicit mapping between the Xt-EHR logical model and the FHIR artifacts in this guide.
- State that the guide is compatible with EU-core where EU-core requirements apply.
- State that the anatomical-region extension is mandatory in the EU ImagingStudy profiling and that its value set binding is required.

## Delta guidance

The page should explicitly describe the delta relative to IHE MADO.

That delta should normally cover:

- traceability from FHIR artifacts to Xt-EHR logical model elements;
- EU-specific profiling of inherited MADO artifacts;
- publication of Xt-EHR mapping content;
- stricter anatomical-region requirements than in base IHE MADO;
- EU-core compatibility where relevant resources carry patient and related clinical data.

## Local source anchors

Use the current implementation in this repository as the primary evidence source for the page text.
In particular, verify wording against:

- `imaging-manifest-fork/input/pagecontent/mado-volume1.md`
- `imaging-manifest-fork/input/pagecontent/mado-volume2.md`
- `imaging-manifest-fork/input/pagecontent/mado-volume3.md`
- `imaging-manifest-fork/input/pagecontent/xtehr-mapping.md`
- `imaging-manifest-fork/input/fsh/profiles/ImagingStudy-MADO-eu.fsh`
- `imaging-manifest-fork/input/fsh/profiles/Patient-MADO-eu.fsh`
- `imaging-manifest-fork/input/fsh/profiles/Bundle-MADO-eu.fsh`

Prefer describing requirements that are already reflected in these local artifacts rather than speculative future scope.

## Recommended structure

Use this general structure unless there is a strong reason to deviate:

```markdown
# Functional Requirements

{% include variable-definitions.md %}

[Short introduction stating that the IG extends IHE MADO with EU-specific requirements.]

## EU-specific requirements

* [EU Health Data API alignment]
* [Xt-EHR ImagingStudy support]
* [Xt-EHR logical-model mapping]
* [EU-core compatibility]
* [Mandatory anatomical-region extension and required value set]

## Delta relative to IHE MADO

* [Traceability and obligations]
* [EU-specific profile refinement]
* [Xt-EHR mapping publication]
* [Anatomical-region strengthening]

## Requirements realized in this guide

* [Concrete implementation statements grounded in local profiles/pages]

## Summary

[Short closing paragraph]
```

## Avoid

- Do not describe the page as a generic restatement of IHE MADO.
- Do not introduce future commitments unless they are already documented elsewhere in the repo.
- Do not claim EU-core conformance for artifacts that are not locally profiled that way.
- Do not describe anatomical-region requirements vaguely; state both mandatory presence and required value set binding.
- Do not rely only on external source text when the local delta in this repo is more specific.