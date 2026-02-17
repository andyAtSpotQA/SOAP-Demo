"""Tests for hl7v3_builder.types — HL7 v3 enumerations."""

from hl7v3_builder.types import (
    InteractionType,
    ProcessingCode,
    ProcessingModeCode,
    AckCode,
    ClassCode,
    MoodCode,
    NHSOid,
)


class TestInteractionType:
    def test_pdq_query(self):
        assert InteractionType.PRPA_IN201305UV02 == "PRPA_IN201305UV02"

    def test_pdq_response(self):
        assert InteractionType.PRPA_IN201306UV02 == "PRPA_IN201306UV02"

    def test_scr_query(self):
        assert InteractionType.QUPC_IN160101UK05 == "QUPC_IN160101UK05"

    def test_gp_summary_upload(self):
        assert InteractionType.REPC_IN150016UK05 == "REPC_IN150016UK05"

    def test_pds_retrieval(self):
        assert InteractionType.QUPA_IN040000UK32 == "QUPA_IN040000UK32"

    def test_pds_trace(self):
        assert InteractionType.QUPA_IN020000UK31 == "QUPA_IN020000UK31"

    def test_member_count(self):
        assert len(InteractionType) == 6

    def test_is_str_enum(self):
        assert isinstance(InteractionType.PRPA_IN201305UV02, str)


class TestProcessingCode:
    def test_production(self):
        assert ProcessingCode.PRODUCTION == "P"

    def test_training(self):
        assert ProcessingCode.TRAINING == "T"

    def test_debugging(self):
        assert ProcessingCode.DEBUGGING == "D"


class TestProcessingModeCode:
    def test_current(self):
        assert ProcessingModeCode.CURRENT == "T"

    def test_initial_load(self):
        assert ProcessingModeCode.INITIAL_LOAD == "I"

    def test_restore(self):
        assert ProcessingModeCode.RESTORE == "R"


class TestAckCode:
    def test_always(self):
        assert AckCode.ALWAYS == "AL"

    def test_never(self):
        assert AckCode.NEVER == "NE"

    def test_error_only(self):
        assert AckCode.ERROR_ONLY == "ER"


class TestClassCode:
    def test_control_act(self):
        assert ClassCode.CONTROL_ACT == "CACT"

    def test_patient(self):
        assert ClassCode.PATIENT == "PAT"

    def test_person(self):
        assert ClassCode.PERSON == "PSN"

    def test_organization(self):
        assert ClassCode.ORGANIZATION == "ORG"

    def test_device(self):
        assert ClassCode.DEVICE == "DEV"

    def test_assigned(self):
        assert ClassCode.ASSIGNED == "ASSIGNED"

    def test_agent(self):
        assert ClassCode.AGENT == "AGNT"

    def test_member_count(self):
        assert len(ClassCode) == 7


class TestMoodCode:
    def test_event(self):
        assert MoodCode.EVENT == "EVN"

    def test_request(self):
        assert MoodCode.REQUEST == "RQO"

    def test_definition(self):
        assert MoodCode.DEFINITION == "DEF"

    def test_intent(self):
        assert MoodCode.INTENT == "INT"


class TestNHSOid:
    def test_nhs_number(self):
        assert NHSOid.NHS_NUMBER == "2.16.840.1.113883.2.1.4.1"

    def test_spine_interaction(self):
        assert NHSOid.SPINE_INTERACTION == "2.16.840.1.113883.2.1.3.2.4.12"

    def test_spine_message_id(self):
        assert NHSOid.SPINE_MESSAGE_ID == "2.16.840.1.113883.2.1.3.2.4.17"

    def test_spine_asid(self):
        assert NHSOid.SPINE_ASID == "1.2.826.0.1285.0.2.0.107"

    def test_sds_user_id(self):
        assert NHSOid.SDS_USER_ID == "1.2.826.0.1285.0.2.0.65"

    def test_snomed_ct(self):
        assert NHSOid.SNOMED_CT == "2.16.840.1.113883.2.1.3.2.4.15"

    def test_member_count(self):
        assert len(NHSOid) == 13

    def test_is_str_enum(self):
        assert isinstance(NHSOid.NHS_NUMBER, str)
