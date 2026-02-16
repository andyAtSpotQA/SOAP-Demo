# SOAP Demo + Mock SafeSign Signing Service

A minimal SOAP web service demo (Spyne) paired with a mock SafeSign PKCS#11 SDK and REST signing API.

## Components

| Component | File(s) | Port | Description |
|-----------|---------|------|-------------|
| SOAP Service | `soap_demo.py` | 8000 | Customer & Invoice lookup via SOAP 1.1 |
| Signing Service | `signing_service.py` | 5001 | Flask REST API for digital signatures |
| Mock SafeSign SDK | `safesign_mock/` | — | Software PKCS#11 simulation with real RSA crypto |

## Quick Start

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

## Dependencies

- `spyne` / `lxml` — SOAP framework
- `cryptography` — RSA keys, X.509 certificates
- `signxml` — XML digital signatures
- `flask` — REST API
