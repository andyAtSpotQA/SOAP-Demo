# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A minimal SOAP web service demo built with Python 3 and the Spyne framework, plus a mock SafeSign SDK signing service.

- `soap_demo.py` — SOAP services (Spyne, port 8000)
- `signing_service.py` — REST signing API (Flask, port 5001)
- `safesign_mock/` — Mock PKCS#11 SDK package (software RSA keys replacing smartcard hardware)

## Running the Services

```bash
pip install -r requirements.txt

# SOAP service (port 8000)
python soap_demo.py

# Signing service (port 5001) — auto-generates key pair + cert on startup
python signing_service.py
```

- SOAP: `http://localhost:8000` (WSDL at `/?wsdl`)
- Signing: `http://localhost:5001` (health check at `/health`)

## Architecture

The app uses Spyne's `Application` to register two services under one SOAP 1.1 endpoint with namespace `urn:demo`:

- **CustomerService** — `GetCustomerByEmail(email) -> Customer` — looks up a customer by email from an in-memory dict. Returns a placeholder with `customerId=0` and `fullName="NOT_FOUND"` for unknown emails.
- **InvoiceService** — `GetInvoicesByCustomerId(customerId) -> Iterable(Invoice)` — returns invoices for a customer ID (intended to chain with CustomerService output).

Data models (`Customer`, `Invoice`) are Spyne `ComplexModel` subclasses. All data is hardcoded in-memory dicts (`CUSTOMERS`, `INVOICES`). Input validation uses lxml.

### Signing Service (`signing_service.py`)

Flask REST API (port 5001) wrapping the mock SafeSign SDK. PIN required for signing/admin ops.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | SDK status, token info |
| POST | `/sign/raw` | Sign base64 data, return base64 signature |
| POST | `/sign/xml` | Enveloped XML signature (via signxml) |
| GET | `/certificate` | Get signing cert (PEM/DER) |
| GET | `/certificate/info` | Cert metadata |
| POST | `/verify/raw` | Verify a raw signature |
| POST | `/verify/xml` | Verify an XML signature |
| POST | `/admin/generate-keypair` | Generate new key pair |
| POST | `/admin/generate-cert` | Create self-signed cert |
| POST | `/admin/change-pin` | Change token PIN |
| GET | `/admin/token-info` | Token details |

### Mock SafeSign SDK (`safesign_mock/`)

Mirrors the PKCS#11 object model: Library -> Slot -> Token -> Session. Uses real RSA cryptography (`cryptography` lib); only key storage is mocked (in-memory instead of smartcard). Every class/method has `# REAL_SDK:` comments explaining the real SafeSign/PKCS#11 equivalent.

Default PIN: `1234`. PIN locks after 3 failed attempts.

## Dependencies

All deps in `requirements.txt`: spyne, lxml, cryptography, signxml, flask.
