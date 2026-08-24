# WITHDRAWN — tx.fhir.org `urn:ietf:bcp:13` (MimeType) validation is correct (grammar-based by design)

**Status:** Withdrawn / not a defect (do not file).
**Server:** FHIRsmith 0.11.2 at `https://tx.fhir.org/r4` (fhirVersion 4.0.1), observed 2026-08-24

## Why this was withdrawn
The original draft claimed `$validate-code` "accepts invalid media types" because the control
value `not/a-real-type` returned `result = true`. Inspecting the FHIRsmith source shows that
value is actually a **well-formed** `type/subtype` token, so the control was invalid — the server
behaviour is correct.

## Source evidence — `tx/cs/cs-mimetypes.js`
`urn:ietf:bcp:13` is implemented as an **open, grammar-validated** code system (no IANA
enumeration), which is the intended design:

```js
// MimeTypeConcept.#parseMimeType(code)
const trimmed = code.trim();
const parts   = trimmed.split(';')[0].trim();   // strip ;parameters
const typeParts = parts.split('/');
if (typeParts.length === 2 && typeParts[0] && typeParts[1]) {
  return { type: typeParts[0], subtype: typeParts[1], isValid: true, ... };
}
return { isValid: false, ... };
// isValid() = mimeType.isValid && !!mimeType.subtype
```
Supporting metadata in the same provider: `totalCount() => -1` ("Not bounded"),
`canBeExpanded() => false` ("cannot be iterated / enumerated"), `isNotClosed() => true`.

So a code is valid iff it is `type/subtype` with both parts non-empty (parameters after `;`
ignored). That is the appropriate way to validate BCP-13 media types, which are an open set.

## Verification against tx.fhir.org (2026-08-24)
```
GET /r4/ValueSet/$validate-code?url=http://hl7.org/fhir/ValueSet/mimetypes&system=urn:ietf:bcp:13&code=<enc>
```
| code | result | note |
|---|---|---|
| `application/dicom` | true | valid |
| `not/a-real-type` | true | **well-formed** `type/subtype` — bad control in original draft |
| `not-a-real-type` (no `/`) | false | correctly rejected |
| `application/` (empty subtype) | false | correctly rejected |
| `/json` (empty type) | false | correctly rejected |
| `text/html; charset=utf-8` | true | valid; parameters stripped |

## Conclusion
The MimeType validation is working as intended and correctly rejects malformed input. There is no
defect here. The real, actionable problem is the session-cache expiry that turns *valid* media
types into build ERRORs — see `tx-mimetype-session-cache-expiry.md`.
