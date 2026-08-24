# tx.fhir.org — MimeType required-binding validation fails when the cached session expires mid-build

https://github.com/HealthIntersections/FHIRsmith/issues/279

**Server:** FHIRsmith 0.11.2 at `https://tx.fhir.org/r4` (fhirVersion 4.0.1), observed 2026-08-24
**Client:** HL7 FHIR IG Publisher 2.3.2 building an R4 Implementation Guide

## Summary
During an IG Publisher build, `$validate-code` for media-type codes bound (required) to
`http://hl7.org/fhir/ValueSet/mimetypes` (system `urn:ietf:bcp:13`) intermittently fails
because the server reports the cached validation session as unknown/expired. Because the
binding is `required`, the publisher cannot obtain a definitive answer and emits a content
**ERROR** for codes that are actually valid.

## Bindings / elements involved
- ValueSet: `http://hl7.org/fhir/ValueSet/mimetypes|4.0.1` (system `urn:ietf:bcp:13`)
- Affected R4 elements (all `required` binding): `Attachment.contentType`, `Binary.contentType`, `Endpoint.payloadMimeType`
- Example codes affected: `application/dicom`, `application/fhir+json`, `text/html`

## Observed behaviour
The IG Publisher opens a cached validation session (`$cache-control?mode=start`) and streams
`$validate-code` calls into it. On long/parallel builds the server responds:

```
Error from https://tx.fhir.org/r4: Error: The cache '<uuid>' is not known to this server.
Caches are created with $cache-control?mode=start; this one was never created, or has
expired or been released
```

Resulting QA error (valid code reported as invalid):

```
ERROR: Binary/kos-binary-example: Binary.contentType: The value provided ('application/dicom')
was not found in the value set 'MimeType' (http://hl7.org/fhir/ValueSet/mimetypes|4.0.1), and a
code is required from this value set
  (error message = Error from https://tx.fhir.org/r4: … The cache '<uuid>' is not known to this
   server … expired or been released)
```

The same codes validate as `true` when called individually (outside the batched session) — this
confirms the codes are structurally accepted and the failure is the session cache, not the
request itself (see the companion ticket
`HealthIntersections-FHIRsmith-tx-mimetype-bcp13-membership-validation.md`).

## Expected behaviour
A session that was opened during the build should not later be reported as "never created"
while the build is still running; or the server should transparently re-establish/renew the
session so that a valid code is never reported as invalid due to server-side cache lifecycle.

## Impact
IG builds against `tx.fhir.org` produce **non-deterministic ERRORs on valid MIME types**,
blocking a clean QA result even though the instances are correct.

## Frequency / correlation
Correlates with longer builds and periods of higher server load; not every build, and different
cache UUIDs appear across runs.

## Notes
- Reproduction is workflow-dependent (requires the IG Publisher session-cache flow), so it is
  not reliably reproducible with a single `curl`.
- A separate, distinct concern about BCP-13 membership validation is filed in
  `HealthIntersections-FHIRsmith-tx-mimetype-bcp13-membership-validation.md`.
- This message (`CACHE_ID_UNKNOWN`) is emitted by FHIRsmith and is server-authoritative
  (`translations/Messages.properties`; `tx/workers/worker.js`). The primary fix is server-side
  (do not expire/release a cache a client is still using; ensure session affinity across
  scaled instances). A **companion client-side ticket** asks the IG Publisher to recover from
  `CACHE_ID_UNKNOWN` instead of surfacing a content error:
  [`HL7-fhir-ig-publisher-tx-cache-id-unknown-not-recovered.md`.](https://github.com/HL7/fhir-ig-publisher/issues/1359)
