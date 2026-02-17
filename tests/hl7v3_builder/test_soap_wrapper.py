"""Tests for hl7v3_builder.soap_wrapper — SOAP 1.1 + WS-Addressing wrapping."""

import pytest
from lxml import etree

from hl7v3_builder.soap_wrapper import (
    wrap_in_soap,
    extract_from_soap,
    SOAP_NS,
    WSA_NS,
)
from hl7v3_builder.exceptions import SoapWrappingError


class TestWrapInSoap:
    def test_returns_xml_string(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        assert isinstance(xml, str)

    def test_has_soap_envelope(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        root = etree.fromstring(xml.encode("utf-8"))
        assert etree.QName(root.tag).localname == "Envelope"

    def test_has_soap_header(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        root = etree.fromstring(xml.encode("utf-8"))
        header = root.find(f"{{{SOAP_NS}}}Header")
        assert header is not None

    def test_has_soap_body(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        root = etree.fromstring(xml.encode("utf-8"))
        body = root.find(f"{{{SOAP_NS}}}Body")
        assert body is not None

    def test_wsa_to_header(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        root = etree.fromstring(xml.encode("utf-8"))
        to_el = root.find(f".//{{{WSA_NS}}}To")
        assert to_el.text == "https://spine.nhs.uk/Spine"

    def test_wsa_action_auto(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        root = etree.fromstring(xml.encode("utf-8"))
        action = root.find(f".//{{{WSA_NS}}}Action")
        assert "PRPA_IN201305UV02" in action.text

    def test_wsa_action_override(self, hl7_message):
        xml = wrap_in_soap(
            hl7_message,
            to_url="https://spine.nhs.uk/Spine",
            wsa_action="urn:custom:action",
        )
        root = etree.fromstring(xml.encode("utf-8"))
        action = root.find(f".//{{{WSA_NS}}}Action")
        assert action.text == "urn:custom:action"

    def test_wsa_message_id(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        root = etree.fromstring(xml.encode("utf-8"))
        msg_id = root.find(f".//{{{WSA_NS}}}MessageID")
        assert msg_id.text.startswith("uuid:")

    def test_wsa_message_id_override(self, hl7_message):
        xml = wrap_in_soap(
            hl7_message,
            to_url="https://spine.nhs.uk/Spine",
            wsa_message_id="uuid:custom-id",
        )
        root = etree.fromstring(xml.encode("utf-8"))
        msg_id = root.find(f".//{{{WSA_NS}}}MessageID")
        assert msg_id.text == "uuid:custom-id"

    def test_from_url_present(self, hl7_message):
        xml = wrap_in_soap(
            hl7_message,
            to_url="https://spine.nhs.uk/Spine",
            from_url="https://my-system.nhs.uk",
        )
        root = etree.fromstring(xml.encode("utf-8"))
        from_el = root.find(f".//{{{WSA_NS}}}From")
        address = from_el.find(f"{{{WSA_NS}}}Address")
        assert address.text == "https://my-system.nhs.uk"

    def test_from_url_absent(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        root = etree.fromstring(xml.encode("utf-8"))
        assert root.find(f".//{{{WSA_NS}}}From") is None

    def test_missing_to_url_raises(self, hl7_message):
        with pytest.raises(SoapWrappingError):
            wrap_in_soap(hl7_message, to_url="")

    def test_body_contains_hl7_message(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        root = etree.fromstring(xml.encode("utf-8"))
        body = root.find(f"{{{SOAP_NS}}}Body")
        hl7_root = body[0]
        assert "PRPA_IN201305UV02" in hl7_root.tag

    def test_xml_declaration(self, hl7_message):
        xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        assert xml.startswith("<?xml")


class TestExtractFromSoap:
    def test_extract_hl7_payload(self, hl7_message):
        soap_xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        payload = extract_from_soap(soap_xml)
        assert "PRPA_IN201305UV02" in payload.tag

    def test_extract_from_bytes(self, hl7_message):
        soap_xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        payload = extract_from_soap(soap_xml.encode("utf-8"))
        assert payload is not None

    def test_invalid_xml_raises(self):
        with pytest.raises(SoapWrappingError):
            extract_from_soap("<<< not xml")

    def test_no_body_raises(self):
        xml = '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Header/></soap:Envelope>'
        with pytest.raises(SoapWrappingError):
            extract_from_soap(xml)

    def test_empty_body_raises(self):
        xml = '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body/></soap:Envelope>'
        with pytest.raises(SoapWrappingError):
            extract_from_soap(xml)

    def test_roundtrip(self, hl7_message):
        soap_xml = wrap_in_soap(hl7_message, to_url="https://spine.nhs.uk/Spine")
        extracted = extract_from_soap(soap_xml)
        assert etree.QName(extracted.tag).localname == hl7_message.interaction
