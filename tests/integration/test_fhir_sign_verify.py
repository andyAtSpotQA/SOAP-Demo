"""Integration test: Build FHIR Bundle -> sign -> verify."""

import base64
import json

from fhir_builder.templates import (
    patient_search_bundle,
    medication_request_bundle,
    gp_connect_structured_record,
)


class TestFHIRSignVerify:
    def test_sign_and_verify_patient_search_bundle(self, client):
        """Build a PDS-style search bundle, sign XML, verify."""

        bundle = patient_search_bundle(
            "9999999999", "Smith", "John", "1980-01-15", "male",
        ).build()

        xml_str = bundle.to_xml()
        assert "Bundle" in xml_str

        # Sign
        sign_resp = client.post("/sign/xml", json={
            "xml": xml_str,
            "pin": "1234",
        })
        assert sign_resp.status_code == 200
        signed_xml = json.loads(sign_resp.data)["signed_xml"]
        assert "Signature" in signed_xml

        # Verify
        verify_resp = client.post("/verify/xml", json={"xml": signed_xml})
        assert json.loads(verify_resp.data)["valid"] is True

    def test_sign_raw_fhir_bundle(self, client):
        """Sign raw FHIR Bundle bytes and verify."""

        bundle = medication_request_bundle(
            patient_nhs_number="9999999999",
            patient_family_name="Smith",
            patient_given_name="John",
            patient_birth_date="1980-01-15",
            patient_gender="male",
            medication_snomed_code="322236009",
            medication_display="Paracetamol 500mg tablets",
            dosage_text="Take one tablet twice daily",
        ).build()

        xml_bytes = bundle.to_xml().encode("utf-8")
        data_b64 = base64.b64encode(xml_bytes).decode()

        # Sign
        sign_resp = client.post("/sign/raw", json={
            "data": data_b64,
            "pin": "1234",
        })
        assert sign_resp.status_code == 200
        sig_b64 = json.loads(sign_resp.data)["signature"]

        # Verify
        verify_resp = client.post("/verify/raw", json={
            "data": data_b64,
            "signature": sig_b64,
        })
        assert json.loads(verify_resp.data)["valid"] is True

    def test_gp_connect_bundle_sign_verify(self, client):
        """Build a GP Connect structured record, sign and verify."""

        bundle = gp_connect_structured_record(
            "9999999999", "Smith", "John", "1980-01-15", "male",
            allergies=[{"code": "91936005", "display": "Penicillin allergy"}],
            conditions=[{"code": "73211009", "display": "Diabetes mellitus"}],
        ).build()

        xml_str = bundle.to_xml()

        # Sign
        sign_resp = client.post("/sign/xml", json={
            "xml": xml_str,
            "pin": "1234",
        })
        assert sign_resp.status_code == 200
        signed_xml = json.loads(sign_resp.data)["signed_xml"]

        # Verify
        verify_resp = client.post("/verify/xml", json={"xml": signed_xml})
        assert json.loads(verify_resp.data)["valid"] is True
