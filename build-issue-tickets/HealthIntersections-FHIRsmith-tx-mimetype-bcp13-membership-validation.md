# tx.fhir.org — MimeType (`urn:ietf:bcp:13`) `$validate-code` does not enforce membership for a Required binding

Github issue: https://github.com/HealthIntersections/FHIRsmith/issues/278

**Server:** FHIRsmith 0.11.2 at `https://tx.fhir.org/r4` (fhirVersion 4.0.1), observed 2026-08-24
**Client:** direct `curl` (single, non-session calls)

## Summary
`Attachment.contentType` (and `Binary.contentType`, `Endpoint.payloadMimeType`,
`Signature.targetFormat`/`sigFormat`, `CapabilityStatement.format`, etc.) are bound to the
`MimeTypes` value set (`http://hl7.org/fhir/ValueSet/mimetypes`) with **binding strength =
Required**. That value set is defined as *"all codes from BCP-13"* (the IANA media-type registry).

FHIRsmith validates `urn:ietf:bcp:13` **by grammar only** — it accepts any `type/subtype`
token with two non-empty parts, without checking that the media type is an actual BCP-13/IANA
media type. As a result `$validate-code` returns `result = true` for `not/a-real-type`, which is
not a registered media type. For a **Required** binding, membership in the value set should be
enforced, so this value should be `false` (or at least flagged).

## Spec basis
- FHIR R5 — Attachment: `Attachment.contentType : code [0..1]` — *"The mime type of an
  attachment. Any valid mime type is allowed. (Strength=Required)"*, bound to
  `http://hl7.org/fhir/ValueSet/mimetypes`.
  https://hl7.org/fhir/R5/datatypes.html#Attachment
- FHIR R5 — mimetypes value set: *"This value set includes all possible codes from BCP-13"*,
  content logical definition *"Include all codes defined in `urn:ietf:bcp:13`"*, and
  *"cannot be expanded … it has an infinite number of members."* Normative from v4.0.0.
  https://hl7.org/fhir/R5/valueset-mimetypes.html
- Same binding + value set in R4:
  https://hl7.org/fhir/R4/datatypes.html#Attachment ,
  https://hl7.org/fhir/R4/valueset-mimetypes.html

The value set is the set of BCP-13 media types; a Required binding therefore requires the code to
be a member of that set (a real media type), not merely a `type/subtype`-shaped string.

## Source behaviour — `tx/cs/cs-mimetypes.js`
Validation is purely syntactic (no registry/membership check):
```js
// MimeTypeConcept.#parseMimeType(code)
const trimmed   = code.trim();
const parts     = trimmed.split(';')[0].trim();   // strip ;parameters
const typeParts = parts.split('/');
if (typeParts.length === 2 && typeParts[0] && typeParts[1]) {
  return { type: typeParts[0], subtype: typeParts[1], isValid: true, ... };
}
return { isValid: false, ... };
// isValid() = mimeType.isValid && !!mimeType.subtype
```
Provider metadata: `totalCount() => -1`, `canBeExpanded() => false`, `isNotClosed() => true`.
So any two-part `type/subtype` token is accepted; only structurally malformed input is rejected.

## Verification against tx.fhir.org (2026-08-24)
```
GET /r4/ValueSet/$validate-code?url=http://hl7.org/fhir/ValueSet/mimetypes&system=urn:ietf:bcp:13&code=<enc>
```
| code | result | expected under Required binding |
|---|---|---|
| `application/dicom` | true | true (registered) |
| `application/fhir+json` | true | true (registered) |
| `text/html` | true | true (registered) |
| `not/a-real-type` | **true** | **false** — not a BCP-13/IANA media type |
| `not-a-real-type` (no `/`) | false | false |
| `application/` (empty subtype) | false | false |
| `/json` (empty type) | false | false |

## Expected behaviour
For the Required binding to the mimetypes value set, `$validate-code` should confirm that the
code is an actual BCP-13 media type (registered IANA type, or a validly-formed subtype in the
standards/vendor (`vnd.`)/personal (`prs.`)/unregistered (`x.`) trees per RFC 6838), returning
`result = false` for tokens like `not/a-real-type` that are merely syntactically shaped.
At minimum the value set should be "populated appropriately" so a Required binding is meaningful.

## Reproduction (standalone)
```bash
for c in application/dicom application/fhir+json text/html not/a-real-type not-a-real-type; do
  enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$c")
  echo -n "$c -> "
  curl -s "https://tx.fhir.org/r4/ValueSet/\$validate-code?url=http://hl7.org/fhir/ValueSet/mimetypes&system=urn:ietf:bcp:13&code=$enc" \
    | python3 -c "import sys,json;d=json.load(sys.stdin);print({p['name']:p.get('valueBoolean') for p in d['parameter'] if p['name']=='result'})"
done
```

## Note for triage
Many terminology servers (including the reference implementation) validate BCP-13 syntactically
because the IANA registry is large and frequently updated. If syntactic validation is the
intended policy, please confirm/document that; the concern is that a **Required** binding then
does not actually constrain the value beyond `type/subtype` shape.

## Related
- Distinct reliability issue: session-cache expiry turning *valid* media types into build ERRORs —
  `HealthIntersections-FHIRsmith-tx-mimetype-session-cache-expiry.md`.
