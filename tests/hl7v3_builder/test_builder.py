"""Tests for hl7v3_builder.builder — HL7v3MessageBuilder and HL7v3Message."""

from datetime import datetime

import pytest
from lxml import etree

from hl7v3_builder.builder import HL7v3MessageBuilder, HL7v3Message
from hl7v3_builder.datatypes import HL7_NS
from hl7v3_builder.types import (
    InteractionType,
    ProcessingCode,
    ProcessingModeCode,
    AckCode,
    NHSOid,
)
from hl7v3_builder.exceptions import ValidationError


class TestBuilderValidation:
    def test_missing_interaction_fails(self):
        b = HL7v3MessageBuilder().set_sender(asid="S").set_receiver(asid="R")
        errors = b.validate()
        assert any("interaction" in e for e in errors)

    def test_missing_sender_fails(self):
        b = HL7v3MessageBuilder().set_interaction(InteractionType.PRPA_IN201305UV02).set_receiver(asid="R")
        errors = b.validate()
        assert any("sender" in e for e in errors)

    def test_missing_receiver_fails(self):
        b = HL7v3MessageBuilder().set_interaction(InteractionType.PRPA_IN201305UV02).set_sender(asid="S")
        errors = b.validate()
        assert any("receiver" in e for e in errors)

    def test_valid_builder_no_errors(self, hl7_builder):
        assert hl7_builder.validate() == []

    def test_build_raises_on_invalid(self):
        with pytest.raises(ValidationError):
            HL7v3MessageBuilder().build()

    def test_validation_error_has_field(self):
        try:
            HL7v3MessageBuilder().build()
        except ValidationError as e:
            assert e.field is not None


class TestBuilderBuild:
    def test_returns_hl7v3_message(self, hl7_builder):
        msg = hl7_builder.build()
        assert isinstance(msg, HL7v3Message)

    def test_root_element_name_matches_interaction(self, hl7_builder):
        msg = hl7_builder.build()
        assert etree.QName(msg.root.tag).localname == "PRPA_IN201305UV02"

    def test_its_version_attribute(self, hl7_builder):
        msg = hl7_builder.build()
        assert msg.root.get("ITSVersion") == "XML_1.0"

    def test_auto_generated_message_id(self, hl7_builder):
        msg = hl7_builder.build()
        assert msg.message_id is not None
        assert len(msg.message_id) > 0

    def test_explicit_message_id(self):
        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.PRPA_IN201305UV02)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .set_message_id("MY-ID-123")
            .build()
        )
        assert msg.message_id == "MY-ID-123"

    def test_interaction_property(self, hl7_builder):
        msg = hl7_builder.build()
        assert msg.interaction == "PRPA_IN201305UV02"

    def test_message_id_element_in_xml(self, hl7_builder):
        msg = hl7_builder.build()
        id_el = msg.root.find(f"{{{HL7_NS}}}id")
        assert id_el.get("root") == NHSOid.SPINE_MESSAGE_ID.value

    def test_creation_time_element(self, hl7_builder):
        msg = hl7_builder.build()
        ct = msg.root.find(f"{{{HL7_NS}}}creationTime")
        assert ct is not None
        assert ct.get("value") is not None

    def test_explicit_creation_time(self):
        dt = datetime(2024, 6, 15, 12, 0, 0)
        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.PRPA_IN201305UV02)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .set_creation_time(dt)
            .build()
        )
        ct = msg.root.find(f"{{{HL7_NS}}}creationTime")
        assert ct.get("value") == "20240615120000"

    def test_version_code_element(self, hl7_builder):
        msg = hl7_builder.build()
        vc = msg.root.find(f"{{{HL7_NS}}}versionCode")
        assert vc.get("code") == "V3NPfIT4.2.00"

    def test_interaction_id_element(self, hl7_builder):
        msg = hl7_builder.build()
        iid = msg.root.find(f"{{{HL7_NS}}}interactionId")
        assert iid.get("root") == NHSOid.SPINE_INTERACTION.value
        assert iid.get("extension") == "PRPA_IN201305UV02"


class TestBuilderProcessingCodes:
    def test_default_processing_code_is_debugging(self, hl7_builder):
        msg = hl7_builder.build()
        pc = msg.root.find(f"{{{HL7_NS}}}processingCode")
        assert pc.get("code") == "D"

    def test_set_processing_code(self):
        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.PRPA_IN201305UV02)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .set_processing_code(ProcessingCode.PRODUCTION)
            .build()
        )
        pc = msg.root.find(f"{{{HL7_NS}}}processingCode")
        assert pc.get("code") == "P"

    def test_default_processing_mode_is_current(self, hl7_builder):
        msg = hl7_builder.build()
        pm = msg.root.find(f"{{{HL7_NS}}}processingModeCode")
        assert pm.get("code") == "T"

    def test_default_accept_ack_is_never(self, hl7_builder):
        msg = hl7_builder.build()
        ack = msg.root.find(f"{{{HL7_NS}}}acceptAckCode")
        assert ack.get("code") == "NE"


class TestBuilderSenderReceiver:
    def test_sender_asid_in_xml(self, hl7_builder):
        msg = hl7_builder.build()
        snd = msg.root.find(f"{{{HL7_NS}}}communicationFunctionSnd")
        assert snd is not None
        device_id = snd.find(f".//{{{HL7_NS}}}id")
        assert device_id.get("extension") == "TEST-SENDER"

    def test_receiver_asid_in_xml(self, hl7_builder):
        msg = hl7_builder.build()
        rcv = msg.root.find(f"{{{HL7_NS}}}communicationFunctionRcv")
        device_id = rcv.find(f".//{{{HL7_NS}}}id")
        assert device_id.get("extension") == "TEST-RECEIVER"


class TestBuilderControlAct:
    def test_control_act_event_present(self, hl7_builder):
        msg = hl7_builder.build()
        cae = msg.root.find(f"{{{HL7_NS}}}ControlActEvent")
        assert cae is not None
        assert cae.get("classCode") == "CACT"
        assert cae.get("moodCode") == "EVN"

    def test_author_element(self):
        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.PRPA_IN201305UV02)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .set_author(user_id="U1", role_profile_id="RP1")
            .build()
        )
        cae = msg.root.find(f"{{{HL7_NS}}}ControlActEvent")
        author_el = cae.find(f"{{{HL7_NS}}}author")
        assert author_el is not None

    def test_trigger_event(self):
        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.PRPA_IN201305UV02)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .set_trigger_event("PRPA_TE201305UV02")
            .build()
        )
        cae = msg.root.find(f"{{{HL7_NS}}}ControlActEvent")
        code_el = cae.find(f"{{{HL7_NS}}}code")
        assert code_el.get("code") == "PRPA_TE201305UV02"

    def test_query_params_in_control_act(self):
        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.PRPA_IN201305UV02)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .set_query_params(nhs_number="9999999999")
            .build()
        )
        cae = msg.root.find(f"{{{HL7_NS}}}ControlActEvent")
        qbp = cae.find(f"{{{HL7_NS}}}queryByParameter")
        assert qbp is not None

    def test_payload_in_subject(self):
        payload = etree.Element(f"{{{HL7_NS}}}ClinicalDocument")
        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.REPC_IN150016UK05)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .set_payload(payload)
            .build()
        )
        cae = msg.root.find(f"{{{HL7_NS}}}ControlActEvent")
        subject = cae.find(f"{{{HL7_NS}}}subject")
        assert subject is not None
        assert etree.QName(subject[0].tag).localname == "ClinicalDocument"

    def test_add_control_act_content(self):
        extra = etree.Element(f"{{{HL7_NS}}}customElement")
        msg = (
            HL7v3MessageBuilder()
            .set_interaction(InteractionType.PRPA_IN201305UV02)
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .add_control_act_content(extra)
            .build()
        )
        cae = msg.root.find(f"{{{HL7_NS}}}ControlActEvent")
        assert cae.find(f"{{{HL7_NS}}}customElement") is not None


class TestHL7v3Message:
    def test_to_xml_returns_string(self, hl7_message):
        xml = hl7_message.to_xml()
        assert isinstance(xml, str)

    def test_to_xml_has_declaration(self, hl7_message):
        xml = hl7_message.to_xml()
        assert xml.startswith("<?xml")

    def test_to_xml_no_declaration(self, hl7_message):
        xml = hl7_message.to_xml(xml_declaration=False)
        assert not xml.startswith("<?xml")

    def test_to_element_returns_element(self, hl7_message):
        el = hl7_message.to_element()
        assert isinstance(el, etree._Element)

    def test_root_property(self, hl7_message):
        assert hl7_message.root is hl7_message.to_element()

    def test_interaction_property(self, hl7_message):
        assert hl7_message.interaction == "PRPA_IN201305UV02"

    def test_message_id_property(self, hl7_message):
        assert len(hl7_message.message_id) > 0


class TestFluentChaining:
    def test_all_setters_return_builder(self):
        b = HL7v3MessageBuilder()
        assert isinstance(b.set_interaction(InteractionType.PRPA_IN201305UV02), HL7v3MessageBuilder)
        assert isinstance(b.set_sender(asid="S"), HL7v3MessageBuilder)
        assert isinstance(b.set_receiver(asid="R"), HL7v3MessageBuilder)
        assert isinstance(b.set_message_id("X"), HL7v3MessageBuilder)
        assert isinstance(b.set_creation_time(datetime.utcnow()), HL7v3MessageBuilder)
        assert isinstance(b.set_processing_code(ProcessingCode.DEBUGGING), HL7v3MessageBuilder)
        assert isinstance(b.set_processing_mode(ProcessingModeCode.CURRENT), HL7v3MessageBuilder)
        assert isinstance(b.set_accept_ack(AckCode.NEVER), HL7v3MessageBuilder)
        assert isinstance(b.set_author(user_id="U", role_profile_id="R"), HL7v3MessageBuilder)
        assert isinstance(b.set_trigger_event("X"), HL7v3MessageBuilder)
        assert isinstance(b.set_query_params(nhs_number="123"), HL7v3MessageBuilder)

    def test_string_interaction_type(self):
        msg = (
            HL7v3MessageBuilder()
            .set_interaction("CUSTOM_INTERACTION")
            .set_sender(asid="S")
            .set_receiver(asid="R")
            .build()
        )
        assert msg.interaction == "CUSTOM_INTERACTION"
