---
description: "Guidance for maintaining the mado-volume2 page for the HL7 Europe Imaging Manifest IG."
applyTo: "imaging-manifest-fork/input/pagecontent/mado-volume2.md"
---

This instruction applies when editing the mado-volume2 page.

- Goal: clearly state the delta between this EU specification and IHE MADO Volume 2 (Transactions), with explicit source references.
- Audience: implementers and reviewers validating transaction behavior and interoperability obligations.
- Tone: concise, factual, traceable to base text.

## Required references

When updating this page, include references to both:

- IHE MADO Volume 2 HTML page:
  `https://build.fhir.org/ig/IHE/RAD.MADO/volume-2.html`
- IHE MADO PDF anchored at transaction pages (page 32+):
  `https://build.fhir.org/ig/IHE/RAD.MADO/IHE_RAD_Suppl_MADO.pdf#page=32`

## Required content sections

Keep these sections (or equivalent) in the page:

1. "Delta relative to IHE MADO Volume 2"
- List concrete deltas only.
- If no normative divergence is introduced, state that explicitly and still list profile-level clarifications relevant to this IG.

2. "Topics addressed in IHE MADO Volume 2 (page 32+)"
- Provide a topic list derived from transaction pages.
- Include a short summary for each topic.

3. "EU implementation emphasis"
- Describe how EU deployment context (including cross-community/cross-border exchange behavior) should interpret and apply the same transaction baseline.

## Baseline transaction topics to cover

For page 32+ updates, include at least:

- Update/reuse of RAD-107 WADO-RS Retrieve transaction messaging.
- Four message pairs and support rules:
  - Get Instances
  - Get Metadata
  - Get Bulkdata
  - Get Rendered Instances
- MADO profile constraints for mandatory/optional support (including Rendered Instances option behavior).
- XC-WADO interaction expectations and support scope.
- Appendix XA cross-community retrieval-address handling:
  - Retrieve Location UID handling
  - Retrieve URL handling
  - Gateway URL transformation patterns across communities

## Authoring guardrails

- Do not claim EU-specific transaction changes unless they are present in this repository and traceable.
- Distinguish clearly between:
  - Base IHE transaction rules (source specification), and
  - EU deployment emphasis/interpretation in this IG.
- Keep references stable and direct (Volume 2 HTML + PDF page anchor).
- Keep wording implementation-oriented; avoid broad narrative not tied to transactions.
