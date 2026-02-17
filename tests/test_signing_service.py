"""Tests for signing_service.py — Flask REST API wrapping mock SafeSign SDK."""

import base64
import json


class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_status_ok(self, client):
        data = resp_json(client.get("/health"))
        assert data["status"] == "ok"

    def test_health_includes_library_info(self, client):
        data = resp_json(client.get("/health"))
        assert "library" in data

    def test_health_includes_token_info(self, client):
        data = resp_json(client.get("/health"))
        assert "token" in data


class TestSignRaw:
    def test_sign_raw_success(self, client):
        resp = client.post("/sign/raw", json={
            "data": base64.b64encode(b"hello").decode(),
            "pin": "1234",
        })
        assert resp.status_code == 200
        data = resp_json(resp)
        assert "signature" in data
        # Verify it's valid base64
        base64.b64decode(data["signature"])

    def test_sign_raw_missing_pin(self, client):
        resp = client.post("/sign/raw", json={"data": "aGVsbG8="})
        assert resp.status_code == 401

    def test_sign_raw_missing_data(self, client):
        resp = client.post("/sign/raw", json={"pin": "1234"})
        assert resp.status_code == 400

    def test_sign_raw_invalid_base64(self, client):
        resp = client.post("/sign/raw", json={
            "data": "!!!not-base64!!!",
            "pin": "1234",
        })
        assert resp.status_code == 400

    def test_sign_raw_wrong_pin(self, client):
        resp = client.post("/sign/raw", json={
            "data": "aGVsbG8=",
            "pin": "wrong",
        })
        assert resp.status_code == 401

    def test_sign_raw_includes_mechanism(self, client):
        resp = client.post("/sign/raw", json={
            "data": "aGVsbG8=",
            "pin": "1234",
        })
        data = resp_json(resp)
        assert data["mechanism"] == "SHA256_RSA_PKCS"


class TestSignXml:
    def test_sign_xml_success(self, client):
        resp = client.post("/sign/xml", json={
            "xml": "<Root><Data>test</Data></Root>",
            "pin": "1234",
        })
        assert resp.status_code == 200
        assert "signed_xml" in resp_json(resp)

    def test_sign_xml_missing_pin(self, client):
        resp = client.post("/sign/xml", json={"xml": "<Root/>"})
        assert resp.status_code == 401

    def test_sign_xml_missing_xml(self, client):
        resp = client.post("/sign/xml", json={"pin": "1234"})
        assert resp.status_code == 400

    def test_sign_xml_invalid_xml(self, client):
        resp = client.post("/sign/xml", json={
            "xml": "<<< not xml",
            "pin": "1234",
        })
        assert resp.status_code == 400

    def test_sign_xml_contains_signature_element(self, client):
        resp = client.post("/sign/xml", json={
            "xml": "<Root><Data>test</Data></Root>",
            "pin": "1234",
        })
        signed = resp_json(resp)["signed_xml"]
        assert "Signature" in signed


class TestGetCertificate:
    def test_get_certificate_pem_format(self, client):
        resp = client.get("/certificate")
        assert resp.status_code == 200

    def test_get_certificate_der_format(self, client):
        resp = client.get("/certificate?format=der")
        assert resp.status_code == 200
        assert resp.content_type == "application/x-x509-ca-cert"

    def test_pem_starts_with_begin_certificate(self, client):
        resp = client.get("/certificate")
        assert resp.data.decode().strip().startswith("-----BEGIN CERTIFICATE-----")


class TestCertificateInfo:
    def test_certificate_info_returns_200(self, client):
        assert client.get("/certificate/info").status_code == 200

    def test_certificate_info_has_subject(self, client):
        data = resp_json(client.get("/certificate/info"))
        assert "subject" in data

    def test_certificate_info_has_issuer(self, client):
        data = resp_json(client.get("/certificate/info"))
        assert "issuer" in data

    def test_certificate_info_has_serial_number(self, client):
        data = resp_json(client.get("/certificate/info"))
        assert "serial_number" in data

    def test_certificate_info_has_validity_dates(self, client):
        data = resp_json(client.get("/certificate/info"))
        assert "not_valid_before" in data
        assert "not_valid_after" in data

    def test_certificate_info_has_key_size(self, client):
        data = resp_json(client.get("/certificate/info"))
        assert data["public_key_size"] == 2048


class TestVerifyRaw:
    def test_verify_valid_signature(self, client):
        data_b64 = base64.b64encode(b"test data").decode()
        sign_resp = client.post("/sign/raw", json={"data": data_b64, "pin": "1234"})
        sig_b64 = resp_json(sign_resp)["signature"]

        resp = client.post("/verify/raw", json={"data": data_b64, "signature": sig_b64})
        assert resp_json(resp)["valid"] is True

    def test_verify_invalid_signature(self, client):
        data_b64 = base64.b64encode(b"test data").decode()
        bad_sig = base64.b64encode(b"not a real signature").decode()
        resp = client.post("/verify/raw", json={"data": data_b64, "signature": bad_sig})
        assert resp_json(resp)["valid"] is False

    def test_verify_missing_fields(self, client):
        resp = client.post("/verify/raw", json={"data": "aGVsbG8="})
        assert resp.status_code == 400


class TestVerifyXml:
    def test_verify_valid_signed_xml(self, client):
        sign_resp = client.post("/sign/xml", json={
            "xml": "<Root><Data>verify me</Data></Root>",
            "pin": "1234",
        })
        signed_xml = resp_json(sign_resp)["signed_xml"]
        resp = client.post("/verify/xml", json={"xml": signed_xml})
        assert resp_json(resp)["valid"] is True

    def test_verify_tampered_xml(self, client):
        sign_resp = client.post("/sign/xml", json={
            "xml": "<Root><Data>original</Data></Root>",
            "pin": "1234",
        })
        signed_xml = resp_json(sign_resp)["signed_xml"]
        tampered = signed_xml.replace("original", "tampered")
        resp = client.post("/verify/xml", json={"xml": tampered})
        assert resp_json(resp)["valid"] is False

    def test_verify_missing_xml(self, client):
        resp = client.post("/verify/xml", json={})
        assert resp.status_code == 400


class TestAdminGenerateKeypair:
    def test_generate_keypair_success(self, client):
        resp = client.post("/admin/generate-keypair", json={
            "pin": "1234",
            "label": "newkey",
        })
        assert resp.status_code == 200
        data = resp_json(resp)
        assert "public_key_handle" in data
        assert "private_key_handle" in data

    def test_generate_keypair_missing_pin(self, client):
        resp = client.post("/admin/generate-keypair", json={"label": "x"})
        assert resp.status_code == 401

    def test_generate_keypair_custom_label(self, client):
        resp = client.post("/admin/generate-keypair", json={
            "pin": "1234",
            "label": "custom",
        })
        assert resp_json(resp)["label"] == "custom"


class TestAdminGenerateCert:
    def test_generate_cert_success(self, client):
        resp = client.post("/admin/generate-cert", json={
            "pin": "1234",
            "label": "default",
        })
        assert resp.status_code == 200
        assert "certificate_handle" in resp_json(resp)

    def test_generate_cert_missing_pin(self, client):
        resp = client.post("/admin/generate-cert", json={"label": "default"})
        assert resp.status_code == 401

    def test_generate_cert_custom_subject(self, client):
        resp = client.post("/admin/generate-cert", json={
            "pin": "1234",
            "label": "default",
            "subject_cn": "Test User",
        })
        assert resp_json(resp)["subject_cn"] == "Test User"


class TestAdminChangePin:
    def test_change_pin_success(self, client):
        resp = client.post("/admin/change-pin", json={
            "old_pin": "1234",
            "new_pin": "5678",
        })
        assert resp.status_code == 200

    def test_change_pin_wrong_old_pin(self, client):
        resp = client.post("/admin/change-pin", json={
            "old_pin": "wrong",
            "new_pin": "5678",
        })
        assert resp.status_code == 401

    def test_change_pin_short_new_pin(self, client):
        resp = client.post("/admin/change-pin", json={
            "old_pin": "1234",
            "new_pin": "12",
        })
        assert resp.status_code == 400

    def test_change_pin_missing_fields(self, client):
        resp = client.post("/admin/change-pin", json={"old_pin": "1234"})
        assert resp.status_code == 400


class TestAdminTokenInfo:
    def test_token_info_returns_200(self, client):
        assert client.get("/admin/token-info").status_code == 200

    def test_token_info_has_label(self, client):
        data = resp_json(client.get("/admin/token-info"))
        assert "label" in data

    def test_token_info_has_objects_stored(self, client):
        data = resp_json(client.get("/admin/token-info"))
        assert "objects_stored" in data
        assert data["objects_stored"] >= 3  # bootstrap creates key pair + cert


# Helper to parse JSON response
def resp_json(resp):
    return json.loads(resp.data)
