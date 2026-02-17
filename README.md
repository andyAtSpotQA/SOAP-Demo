# SOAP Demo + Mock SafeSign Signing Service + HL7 v3 Builder + FHIR R4 Builder

A healthcare API test automation platform: SOAP demo service, mock SafeSign PKCS#11 SDK with REST signing API, HL7 v3 message builder for NHS Spine interactions, and FHIR R4 resource builder for modern NHS APIs.

## Components

| Component | File(s) | Port | Description |
|-----------|---------|------|-------------|
| SOAP Service | `soap_demo.py` | 8000 | Customer & Invoice lookup via SOAP 1.1 |
| Signing Service | `signing_service.py` | 5001 | Flask REST API for digital signatures |
| Mock SafeSign SDK | `safesign_mock/` | — | Software PKCS#11 simulation with real RSA crypto |
| HL7 v3 Builder | `hl7v3_builder/` | — | Fluent API for constructing HL7 v3 XML messages |
| FHIR R4 Builder | `fhir_builder/` | — | Fluent API for constructing FHIR R4 XML Bundles |

## Quick Start — Docker (recommended)

```bash
docker compose up --build -d

# Both services start automatically:
#   SOAP service  → http://localhost:8000      (WSDL at ?wsdl)
#   Signing API   → http://localhost:5001      (health at /health)

docker compose ps          # check both are healthy
docker compose down        # tear down
```

## Quick Start — Local

```bash
pip install -r requirements.txt

# Start the SOAP service
python soap_demo.py

# Start the signing service (in a separate terminal)
python signing_service.py
```

## SOAP Service

Exposes two services under namespace `urn:demo`:

- **CustomerService** — `GetCustomerByEmail(email)` → Customer record
- **InvoiceService** — `GetInvoicesByCustomerId(customerId)` → Invoice list

WSDL available at `http://localhost:8000/?wsdl`.

## Signing Service

REST API wrapping the mock SafeSign SDK. Auto-generates an RSA 2048 key pair and self-signed certificate on startup.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | SDK status and token info |
| POST | `/sign/raw` | Sign base64 data → base64 signature |
| POST | `/sign/xml` | Enveloped XML digital signature |
| GET | `/certificate` | Signing certificate (PEM or DER) |
| GET | `/certificate/info` | Certificate metadata |
| POST | `/verify/raw` | Verify a raw signature |
| POST | `/verify/xml` | Verify an XML signature |
| POST | `/admin/generate-keypair` | Generate new RSA key pair |
| POST | `/admin/generate-cert` | Create self-signed certificate |
| POST | `/admin/change-pin` | Change token PIN |
| GET | `/admin/token-info` | Token details |

### Examples

```bash
# Health check
curl http://localhost:5001/health

# Get the signing certificate
curl http://localhost:5001/certificate

# Sign data (default PIN: 1234)
curl -X POST http://localhost:5001/sign/raw \
  -H "Content-Type: application/json" \
  -d '{"data":"aGVsbG8=","pin":"1234"}'

# Sign XML
curl -X POST http://localhost:5001/sign/xml \
  -H "Content-Type: application/json" \
  -d '{"xml":"<Invoice><id>1</id></Invoice>","pin":"1234"}'
```

## Mock SafeSign SDK

The `safesign_mock/` package mirrors the PKCS#11 object model used by real SafeSign smartcard middleware:

```
Library → Slot → Token → Session → crypto operations
```

All cryptography is real (RSA keys, SHA-256 signatures via Python's `cryptography` library). Only key *storage* is mocked — in-memory dicts instead of smartcard hardware.

Every class and method has `# REAL_SDK:` comments explaining the exact SafeSign/PKCS#11 call it replaces. Default PIN is `1234`; locks after 3 failed attempts.

### Swapping for Real SafeSign

| Mock | Real SafeSign |
|------|---------------|
| `MockPKCS11Library()` | `pkcs11.lib("/path/to/libaetpkss.so")` |
| `lib.get_token(token_label=...)` | Same API via python-pkcs11 |
| `token.open(rw=True, user_pin=...)` | Same API |
| `session.sign(handle, data, mech)` | `key.sign(data, mechanism=mech)` |
| `session.generate_keypair()` | Same — but key stays on card |

## HL7 v3 Message Builder

The `hl7v3_builder/` package provides a fluent Python API for constructing HL7 v3 XML messages targeting NHS Spine APIs. It builds the standard three-layer structure (transmission wrapper, control act wrapper, payload) with correct element ordering and `urn:hl7-org:v3` namespacing.

### Using a Template

```python
from hl7v3_builder.templates import patient_demographics_query
from hl7v3_builder.soap_wrapper import wrap_in_soap

# Build a Patient Demographics Query
msg = (
    patient_demographics_query("SENDER-ASID-001", "RECEIVER-ASID-002")
    .set_query_params(nhs_number="9999999999")
    .build()
)

# Wrap in SOAP 1.1 + WS-Addressing for Spine delivery
soap_xml = wrap_in_soap(msg, to_url="https://spine.nhs.uk/Spine")

# Sign via the signing service and send
import requests
resp = requests.post("http://localhost:5001/sign/xml",
                     json={"xml": soap_xml, "pin": "1234"})
signed_xml = resp.json()["signed_xml"]
```

### Using the Builder Directly

```python
from hl7v3_builder import HL7v3MessageBuilder, InteractionType

msg = (
    HL7v3MessageBuilder()
    .set_interaction(InteractionType.PRPA_IN201305UV02)
    .set_sender(asid="SENDER-001")
    .set_receiver(asid="RECEIVER-002")
    .set_author(user_id="555254240100", role_profile_id="555254242101")
    .set_query_params(family_name="SMITH", date_of_birth="19800101")
    .build()
)
print(msg.to_xml())
```

### Available Templates

| Function | Interaction | Description |
|----------|-------------|-------------|
| `patient_demographics_query()` | PRPA_IN201305UV02 | PDS patient search by demographics |
| `scr_query()` | QUPC_IN160101UK05 | Summary Care Record retrieval |
| `gp_summary_upload()` | REPC_IN150016UK05 | GP Summary document upload |

Every class and method has `# HL7_SPEC:` comments referencing the relevant HL7 v3 specification.

## FHIR R4 Resource Builder

The `fhir_builder/` package provides a fluent Python API for constructing FHIR R4 XML Bundles targeting modern NHS APIs (PDS FHIR, GP Connect, EPS). Resources use UK Core profiles and NHS identifier systems.

### Using a Template

```python
from fhir_builder.templates import patient_search_bundle

# Build a PDS-style patient search result
bundle = (
    patient_search_bundle("9999999999", "Smith", "John", "1980-01-15", "male")
    .build()
)
print(bundle.to_xml())

# Sign via the signing service
import requests
resp = requests.post("http://localhost:5001/sign/xml",
                     json={"xml": bundle.to_xml(), "pin": "1234"})
signed_xml = resp.json()["signed_xml"]
```

### Using the Builder Directly

```python
from fhir_builder import FHIRBundleBuilder, BundleType
from fhir_builder.resources import patient, organization

bundle = (
    FHIRBundleBuilder()
    .set_type(BundleType.SEARCHSET)
    .set_timestamp()
    .add_entry(patient("9999999999", "Smith", "John", "1980-01-15", "male"))
    .build()
)
print(bundle.to_xml())
```

### Available Templates

| Function | Bundle Type | Description |
|----------|-------------|-------------|
| `patient_search_bundle()` | searchset | PDS-style patient search result |
| `message_bundle()` | message | Generic FHIR message with MessageHeader |
| `gp_connect_structured_record()` | searchset | GP Connect structured record response |
| `medication_request_bundle()` | transaction | EPS-style prescription submission |

Every class and method has `# FHIR_SPEC:` comments referencing the relevant FHIR R4 specification.

## Dependencies

- `spyne` / `lxml` — SOAP framework
- `cryptography` — RSA keys, X.509 certificates
- `signxml` — XML digital signatures
- `flask` — REST API
- `requests` — HTTP client for signing service integration
