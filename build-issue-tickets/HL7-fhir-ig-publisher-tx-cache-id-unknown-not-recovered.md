# IG Publisher — validation aborts on server `CACHE_ID_UNKNOWN` instead of re-establishing the terminology session

https://github.com/HL7/fhir-ig-publisher/issues/1359

**Client:** HL7 FHIR IG Publisher 2.3.2 (Git# 04466d0486ed)
**Server:** FHIRsmith 0.11.2 at `https://tx.fhir.org/r4` (fhirVersion 4.0.1), observed 2026-08-24

## Summary
When the terminology server reports that the publisher's cached validation session is unknown or
expired, the publisher surfaces it as a **content validation ERROR** on the resource under test
(e.g. a required-binding MimeType/LOINC/SNOMED code "not found in value set"), instead of
**re-creating the session (`$cache-control?mode=start`) and retrying** the validation. Valid
instances are therefore reported as invalid, non-deterministically, during long builds.

## Server response the publisher does not recover from
FHIRsmith returns a specific, server-authoritative coded error when a cache-id is not known
(`CACHE_ID_UNKNOWN`, `translations/Messages.properties`; enforced in `tx/workers/worker.js`):

```
The cache '<uuid>' is not known to this server. Caches are created with
$cache-control?mode=start; this one was never created, or has expired or been released
```

FHIRsmith deliberately made cache creation explicit and now rejects unknown/expired cache-ids
rather than silently auto-creating a new cache (see `tx/workers/metadata.js`,
`tx/workers/worker.js`, `tests/tx/cache-id.test.js`). A cache the publisher opened can legitimately
be expired/released by the server mid-build (or, on a scaled `tx.fhir.org` deployment, a request
can reach an instance that never held that session).

## Observed behaviour (as seen in a build)
```
ERROR: Binary/kos-binary-example: Binary.contentType: The value provided ('application/dicom')
was not found in the value set 'MimeType' (http://hl7.org/fhir/ValueSet/mimetypes|4.0.1), and a
code is required from this value set
  (error message = Error from https://tx.fhir.org/r4: … The cache '<uuid>' is not known to this
   server … expired or been released)
```
The same code validates as `true` when re-checked, confirming the code is valid and the failure
is purely the lost session. Multiple distinct cache UUIDs appear across a single build.

## Expected behaviour
On receiving `CACHE_ID_UNKNOWN` (server-side "cache not known / expired / released"), the publisher
should:
1. Treat it as a **transient session-state signal**, not a terminology result.
2. Re-establish a session via `$cache-control?mode=start`, re-front-load as needed, and **retry**
   the failed `$validate-code` (bounded retry).
3. Only emit a validation error if the retried call returns an actual negative terminology result.

This keeps a server-side cache lifecycle event from being reported as a false content error.

## Impact
Non-deterministic ERRORs on valid codes block clean QA and make builds against public
`tx.fhir.org` unreliable, independent of the IG content.

## Related
- Server-side companion (session lifecycle / affinity that drops a still-in-use cache):
  `HealthIntersections-FHIRsmith-tx-mimetype-session-cache-expiry.md`.
    