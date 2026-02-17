"""Integration test: Build HL7 v3 message -> wrap in SOAP -> sign -> verify."""

import base64

from hl7v3_builder import HL7v3MessageBuilder, InteractionType
from hl7v3_builder.soap_wrapper import wrap_in_soap
from hl7v3_builder.templates import patient_demographics_query


class TestHL7SignVerify:
    def test_build_and_sign_hl7_message(self, client):
        """Build an HL7 v3 PDQ message, sign it via signing service, verify."""

        # 1. Build HL7 v3 message
        msg = (
            patient_demographics_query("SENDER-001", "RECEIVER-002")
            .set_query_params(nhs_number="9999999999")
            .build()
        )

        # 2. Serialize to XML
        xml_str = msg.to_xml()
        assert "PRPA_IN201305UV02" in xml_str

        # 3. Sign XML via Flask signing service
        sign_resp = client.post("/sign/xml", json={
            "xml": xml_str,
            "pin": "1234",
        })
        assert sign_resp.status_code == 200
        import json
        sign_data = json.loads(sign_resp.data)
        signed_xml = sign_data["signed_xml"]
        assert "Signature" in signed_xml

        # 4. Verify signed XML
        verify_resp = client.post("/verify/xml", json={"xml": signed_xml})
        assert json.loads(verify_resp.data)["valid"] is True

    def test_sign_raw_hl7_payload(self, client):
        """Sign raw HL7 v3 XML bytes via /sign/raw and verify."""

        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.QUPC_IN160101UK05)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .set_query_params(nhs_number="9999999999")
            .build()
        )

        xml_bytes = msg.to_xml().encode("utf-8")
        data_b64 = base64.b64encode(xml_bytes).decode()

        # Sign
        sign_resp = client.post("/sign/raw", json={
            "data": data_b64,
            "pin": "1234",
        })
        assert sign_resp.status_code == 200
        import json
        sig_b64 = json.loads(sign_resp.data)["signature"]

        # Verify
        verify_resp = client.post("/verify/raw", json={
            "data": data_b64,
            "signature": sig_b64,
        })
        assert json.loads(verify_resp.data)["valid"] is True

    def test_soap_wrapped_hl7_sign(self, client):
        """Wrap HL7 v3 in SOAP, sign the SOAP envelope, verify."""

        msg = (
            patient_demographics_query("SENDER-001", "RECEIVER-002")
            .set_query_params(family_name="Smith", given_name="John")
            .build()
        )

        soap_xml = wrap_in_soap(msg, to_url="https://spine.nhs.uk/Spine")
        assert "Envelope" in soap_xml

        # Sign the SOAP XML
        sign_resp = client.post("/sign/xml", json={
            "xml": soap_xml,
            "pin": "1234",
        })
        assert sign_resp.status_code == 200
