"""
Flask REST API wrapping the mock SafeSign SDK.

Exposes PKCS#11 smartcard operations (signing, certificate management, PIN auth)
over HTTP so they can be consumed the same way a real SafeSign integration would be.

On startup, auto-generates one RSA 2048 key pair + self-signed certificate
so the service is immediately usable.

Run:  python signing_service.py
Port: 5001
"""

import base64
import logging

from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate

from safesign_mock import (
    MockPKCS11Library,
    Mechanism,
    ObjectClass,
    PKCS11Error,
    PinIncorrect,
    PinLocked,
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("signing_service")

API_VERSION = "1.0.5"

# ---------------------------------------------------------------------------
# Global state — mirrors what a real integration would hold as module-level
# references to the PKCS#11 library, token, and default key/cert handles.
# ---------------------------------------------------------------------------
lib = MockPKCS11Library()
token = lib.get_token()

# Handles for the auto-generated default key pair and certificate
_default_pub_handle: int | None = None
_default_priv_handle: int | None = None
_default_cert_handle: int | None = None


def _bootstrap():
    """Generate a default key pair + self-signed cert on startup."""
    global _default_pub_handle, _default_priv_handle, _default_cert_handle

    session = token.open(rw=True, user_pin="1234")
    pub_h, priv_h = session.generate_keypair(label="default")
    cert_h = session.create_self_signed_cert(
        priv_h, pub_h,
        subject_cn="Mock SafeSign Signing Service",
        label="default",
    )
    _default_pub_handle = pub_h
    _default_priv_handle = priv_h
    _default_cert_handle = cert_h
    session.close()
    log.info("Bootstrap complete — default key pair and certificate generated")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_session(pin: str):
    """Open an authenticated session (validates PIN)."""
    return token.open(rw=True, user_pin=pin)


def _get_cert_pem() -> str:
    """Return the default certificate in PEM format."""
    session = token.open(rw=True, user_pin=None)
    _, cert_obj = session.get_certificate(label="default")
    cert = cert_obj["value"]
    session.close()
    return cert.public_bytes(serialization.Encoding.PEM).decode()


def _error(msg: str, status: int = 400):
    return jsonify({"error": msg}), status


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """SDK status and token info."""
    return jsonify({
        "status": "ok",
        "library": lib.get_info(),
        "token": token.get_info(),
    })


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------

@app.route("/sign/raw", methods=["POST"])
def sign_raw():
    """Sign base64-encoded data, return base64 signature.

    JSON body: { "data": "<base64>", "pin": "<pin>", "label": "default" }
    """
    body = request.get_json(silent=True) or {}
    pin = body.get("pin")
    data_b64 = body.get("data")
    label = body.get("label", "default")

    if not pin:
        return _error("'pin' is required", 401)
    if not data_b64:
        return _error("'data' (base64) is required")

    # Strip surrounding quotes that some clients add
    data_b64 = data_b64.strip().strip('"').strip("'")

    try:
        data = base64.b64decode(data_b64)
    except Exception:
        return _error("'data' is not valid base64")

    try:
        session = _open_session(pin)
    except (PinIncorrect, PinLocked) as e:
        return _error(str(e), 401)

    try:
        # Find the private key by label
        keys = session.find_objects(**{"class": ObjectClass.PRIVATE_KEY, "label": label})
        if not keys:
            return _error(f"No private key with label '{label}'", 404)
        priv_handle = keys[0][0]

        signature = session.sign(priv_handle, data, Mechanism.SHA256_RSA_PKCS)
        return jsonify({
            "signature": base64.b64encode(signature).decode(),
            "mechanism": "SHA256_RSA_PKCS",
            "label": label,
            "api_version": API_VERSION,
        })
    except PKCS11Error as e:
        return _error(str(e))
    finally:
        session.close()


@app.route("/sign/xml", methods=["POST"])
def sign_xml():
    """Create an enveloped XML signature.

    JSON body: { "xml": "<XML string>", "pin": "<pin>", "label": "default" }
    """
    from lxml import etree
    from signxml import XMLSigner, methods

    body = request.get_json(silent=True) or {}
    pin = body.get("pin")
    xml_str = body.get("xml")
    label = body.get("label", "default")

    if not pin:
        return _error("'pin' is required", 401)
    if not xml_str:
        return _error("'xml' is required")

    try:
        session = _open_session(pin)
    except (PinIncorrect, PinLocked) as e:
        return _error(str(e), 401)

    try:
        # Get private key
        keys = session.find_objects(**{"class": ObjectClass.PRIVATE_KEY, "label": label})
        if not keys:
            return _error(f"No private key with label '{label}'", 404)
        priv_key = keys[0][1]["key"]

        # Get certificate
        _, cert_obj = session.get_certificate(label=label)
        cert = cert_obj["value"]

        # Parse XML and sign
        root = etree.fromstring(xml_str.encode())
        signer = XMLSigner(method=methods.enveloped)
        signed_root = signer.sign(root, key=priv_key, cert=[cert])
        signed_xml = etree.tostring(signed_root, xml_declaration=True, encoding="UTF-8").decode()
        # Strip newlines from PEM cert formatting to avoid issues with
        # clients that mangle \n during JSON round-tripping (e.g. Virtuoso)
        signed_xml = signed_xml.replace("\n", "")

        return jsonify({"signed_xml": signed_xml, "api_version": API_VERSION})
    except PKCS11Error as e:
        return _error(str(e))
    except etree.XMLSyntaxError as e:
        return _error(f"Invalid XML: {e}")
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

@app.route("/certificate", methods=["GET"])
def get_certificate():
    """Return the signing certificate in PEM format."""
    fmt = request.args.get("format", "pem").lower()

    try:
        session = token.open(rw=True, user_pin=None)
        _, cert_obj = session.get_certificate(label="default")
        cert = cert_obj["value"]
        session.close()
    except PKCS11Error as e:
        return _error(str(e), 404)

    if fmt == "der":
        der_bytes = cert.public_bytes(serialization.Encoding.DER)
        return app.response_class(
            der_bytes,
            mimetype="application/x-x509-ca-cert",
            headers={"Content-Disposition": "attachment; filename=cert.der"},
        )

    pem = cert.public_bytes(serialization.Encoding.PEM).decode()
    return app.response_class(pem, mimetype="application/x-pem-file")


@app.route("/certificate/info", methods=["GET"])
def certificate_info():
    """Return certificate metadata as JSON."""
    try:
        session = token.open(rw=True, user_pin=None)
        _, cert_obj = session.get_certificate(label="default")
        cert = cert_obj["value"]
        session.close()
    except PKCS11Error as e:
        return _error(str(e), 404)

    return jsonify({
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "serial_number": str(cert.serial_number),
        "not_valid_before": cert.not_valid_before_utc.isoformat(),
        "not_valid_after": cert.not_valid_after_utc.isoformat(),
        "signature_algorithm": cert.signature_algorithm_oid.dotted_string,
        "public_key_size": cert.public_key().key_size,
    })


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

@app.route("/verify/raw", methods=["POST"])
def verify_raw():
    """Verify a raw signature.

    JSON body: { "data": "<base64>", "signature": "<base64>" }
    Uses the default certificate's public key.
    """
    body = request.get_json(silent=True) or {}
    if isinstance(body, dict):
        data_b64 = body.get("data")
        sig_b64 = body.get("signature")
    else:
        data_b64 = None
        sig_b64 = None

    if not data_b64 or not sig_b64:
        return _error("'data' and 'signature' (base64) are required")

    # Strip surrounding quotes that some clients add
    data_b64 = data_b64.strip().strip('"').strip("'")
    sig_b64 = sig_b64.strip().strip('"').strip("'")


    try:
        data = base64.b64decode(data_b64)
        signature = base64.b64decode(sig_b64)
    except Exception:
        return _error("Invalid base64 encoding")

    try:
        session = token.open(rw=True, user_pin=None)
        _, cert_obj = session.get_certificate(label="default")
        cert = cert_obj["value"]
        session.close()
    except PKCS11Error as e:
        return _error(str(e), 404)

    public_key = cert.public_key()
    try:
        public_key.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())
        return jsonify({"valid": True, "api_version": API_VERSION})
    except Exception:
        return jsonify({"valid": False, "api_version": API_VERSION})


@app.route("/verify/xml", methods=["POST"])
def verify_xml():
    """Verify an enveloped XML signature.

    Accepts:
      - Raw XML body (Content-Type: text/xml or text/plain)
      - JSON body: { "xml": "<signed XML>" } or { "signed_xml": "<signed XML>" }
    """
    from lxml import etree
    from signxml import XMLVerifier

    xml_str = None
    content_type = request.content_type or ""

    if "xml" in content_type or "text/plain" in content_type:
        # Raw XML body — no JSON wrapping
        xml_str = request.get_data(as_text=True)
    else:
        # Try JSON body
        body = request.get_json(silent=True) or {}
        if isinstance(body, dict):
            xml_str = body.get("xml") or body.get("signed_xml")
        elif isinstance(body, str):
            xml_str = body

    # Last resort: extract XML from raw body regardless of content type
    if not xml_str or not xml_str.strip().startswith("<"):
        import re
        raw = request.get_data(as_text=True)
        unescaped = raw.replace('\\"', '"').replace('\\n', '')
        match = re.search(r"(<\?xml.*</[^>]+>|<[A-Za-z].*</[^>]+>)", unescaped, re.DOTALL)
        if match:
            xml_str = match.group(1)

    if not xml_str:
        return _error("'xml' (or 'signed_xml') is required")

    try:
        session = token.open(rw=True, user_pin=None)
        _, cert_obj = session.get_certificate(label="default")
        cert = cert_obj["value"]
        session.close()
    except PKCS11Error as e:
        return _error(str(e), 404)
    except Exception as e:
        return _error(f"Failed to retrieve certificate: {e}", 500)

    try:
        verified_data = XMLVerifier().verify(xml_str.encode(), x509_cert=cert)
        return jsonify({"valid": True, "api_version": API_VERSION})
    except etree.XMLSyntaxError as e:
        return jsonify({"valid": False, "error": f"Invalid XML: {e}", "api_version": API_VERSION})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e), "api_version": API_VERSION})


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@app.route("/admin/generate-keypair", methods=["POST"])
def admin_generate_keypair():
    """Generate a new RSA key pair on the token.

    JSON body: { "pin": "<pin>", "label": "mykey", "key_size": 2048 }
    """
    body = request.get_json(silent=True) or {}
    pin = body.get("pin")
    label = body.get("label", "default")
    key_size = body.get("key_size", 2048)

    if not pin:
        return _error("'pin' is required", 401)

    try:
        session = _open_session(pin)
    except (PinIncorrect, PinLocked) as e:
        return _error(str(e), 401)

    try:
        pub_h, priv_h = session.generate_keypair(label=label, key_size=key_size)
        return jsonify({
            "public_key_handle": pub_h,
            "private_key_handle": priv_h,
            "label": label,
            "key_size": key_size,
        })
    except PKCS11Error as e:
        return _error(str(e))
    finally:
        session.close()


@app.route("/admin/generate-cert", methods=["POST"])
def admin_generate_cert():
    """Create a self-signed certificate for an existing key pair.

    JSON body: { "pin": "<pin>", "label": "default", "subject_cn": "My Name", "validity_days": 365 }
    """
    body = request.get_json(silent=True) or {}
    pin = body.get("pin")
    label = body.get("label", "default")
    subject_cn = body.get("subject_cn", "Mock SafeSign User")
    validity_days = body.get("validity_days", 365)

    if not pin:
        return _error("'pin' is required", 401)

    try:
        session = _open_session(pin)
    except (PinIncorrect, PinLocked) as e:
        return _error(str(e), 401)

    try:
        # Find key pair by label
        pub_keys = session.find_objects(**{"class": ObjectClass.PUBLIC_KEY, "label": label})
        priv_keys = session.find_objects(**{"class": ObjectClass.PRIVATE_KEY, "label": label})
        if not pub_keys or not priv_keys:
            return _error(f"No key pair with label '{label}'", 404)

        cert_h = session.create_self_signed_cert(
            priv_keys[0][0], pub_keys[0][0],
            subject_cn=subject_cn,
            validity_days=validity_days,
            label=label,
        )
        return jsonify({
            "certificate_handle": cert_h,
            "label": label,
            "subject_cn": subject_cn,
        })
    except PKCS11Error as e:
        return _error(str(e))
    finally:
        session.close()


@app.route("/admin/change-pin", methods=["POST"])
def admin_change_pin():
    """Change the token PIN.

    JSON body: { "old_pin": "<current>", "new_pin": "<new>" }
    """
    body = request.get_json(silent=True) or {}
    old_pin = body.get("old_pin")
    new_pin = body.get("new_pin")

    if not old_pin or not new_pin:
        return _error("'old_pin' and 'new_pin' are required")

    try:
        token.change_pin(old_pin, new_pin)
        return jsonify({"status": "PIN changed successfully"})
    except (PinIncorrect, PinLocked) as e:
        return _error(str(e), 401)
    except ValueError as e:
        return _error(str(e))


@app.route("/admin/token-info", methods=["GET"])
def admin_token_info():
    """Return detailed token information."""
    return jsonify(token.get_info())


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(_):
    return _error("Not found", 404)


@app.errorhandler(500)
def server_error(_):
    return _error("Internal server error", 500)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _bootstrap()
    log.info("Signing service starting on http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
