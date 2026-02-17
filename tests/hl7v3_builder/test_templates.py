"""Tests for hl7v3_builder.templates — pre-built interaction templates."""

from lxml import etree

from hl7v3_builder.builder import HL7v3MessageBuilder, HL7v3Message
from hl7v3_builder.datatypes import HL7_NS
from hl7v3_builder.types import InteractionType, ProcessingCode
from hl7v3_builder.templates import (
    patient_demographics_query,
    scr_query,
    gp_summary_upload,
)


class TestPatientDemographicsQuery:
    def test_returns_builder(self):
        b = patient_demographics_query(sender_asid="S", receiver_asid="R")
        assert isinstance(b, HL7v3MessageBuilder)

    def test_interaction_is_pdq(self):
        b = patient_demographics_query(sender_asid="S", receiver_asid="R")
        msg = b.set_query_params(nhs_number="9999999999").build()
        assert msg.interaction == InteractionType.PRPA_IN201305UV02.value

    def test_builds_valid_message(self):
        msg = (
            patient_demographics_query("S", "R")
            .set_query_params(nhs_number="9999999999")
            .build()
        )
        assert isinstance(msg, HL7v3Message)

    def test_sender_and_receiver_set(self):
        msg = (
            patient_demographics_query("SENDER-001", "RECEIVER-002")
            .set_query_params(nhs_number="9999999999")
            .build()
        )
        snd = msg.root.find(f".//{{{HL7_NS}}}communicationFunctionSnd//{{{HL7_NS}}}id")
        rcv = msg.root.find(f".//{{{HL7_NS}}}communicationFunctionRcv//{{{HL7_NS}}}id")
        assert snd.get("extension") == "SENDER-001"
        assert rcv.get("extension") == "RECEIVER-002"

    def test_author_is_set(self):
        msg = (
            patient_demographics_query("S", "R")
            .set_query_params(nhs_number="9999999999")
            .build()
        )
        cae = msg.root.find(f"{{{HL7_NS}}}ControlActEvent")
        assert cae.find(f"{{{HL7_NS}}}author") is not None

    def test_custom_processing_code(self):
        msg = (
            patient_demographics_query(
                "S", "R", processing_code=ProcessingCode.PRODUCTION,
            )
            .set_query_params(nhs_number="9999999999")
            .build()
        )
        pc = msg.root.find(f"{{{HL7_NS}}}processingCode")
        assert pc.get("code") == "P"


class TestSCRQuery:
    def test_returns_builder(self):
        b = scr_query(sender_asid="S", receiver_asid="R")
        assert isinstance(b, HL7v3MessageBuilder)

    def test_interaction_is_scr(self):
        msg = scr_query("S", "R", nhs_number="9999999999").build()
        assert msg.interaction == InteractionType.QUPC_IN160101UK05.value

    def test_nhs_number_pre_set(self):
        msg = scr_query("S", "R", nhs_number="9999999999").build()
        cae = msg.root.find(f"{{{HL7_NS}}}ControlActEvent")
        qbp = cae.find(f"{{{HL7_NS}}}queryByParameter")
        assert qbp is not None

    def test_nhs_number_not_pre_set(self):
        b = scr_query("S", "R")
        # No query params set, should still be a valid builder
        assert b.validate() == []


class TestGPSummaryUpload:
    def test_returns_builder(self):
        b = gp_summary_upload(sender_asid="S", receiver_asid="R")
        assert isinstance(b, HL7v3MessageBuilder)

    def test_interaction_is_gp_summary(self):
        payload = etree.Element(f"{{{HL7_NS}}}ClinicalDocument")
        msg = gp_summary_upload("S", "R").set_payload(payload).build()
        assert msg.interaction == InteractionType.REPC_IN150016UK05.value

    def test_job_role_code(self):
        payload = etree.Element(f"{{{HL7_NS}}}ClinicalDocument")
        msg = gp_summary_upload("S", "R", job_role_code="R0260").set_payload(payload).build()
        part_role = msg.root.find(f".//{{{HL7_NS}}}partSDSRole")
        assert part_role is not None

    def test_builds_valid_message(self):
        payload = etree.Element(f"{{{HL7_NS}}}ClinicalDocument")
        msg = gp_summary_upload("S", "R").set_payload(payload).build()
        assert isinstance(msg, HL7v3Message)
