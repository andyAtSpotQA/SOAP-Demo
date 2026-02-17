"""Tests for hl7v3_builder.elements — composite element builders."""

from lxml import etree
from hl7v3_builder.elements import (
    communication_function_snd,
    communication_function_rcv,
    author,
    query_by_parameter,
    trigger_event,
)
from hl7v3_builder.datatypes import HL7_NS
from hl7v3_builder.types import NHSOid


def _localname(el):
    return etree.QName(el.tag).localname


class TestCommunicationFunctionSnd:
    def test_type_code_snd(self):
        el = communication_function_snd(device_id="msg1", asid="ASID-001")
        assert el.get("typeCode") == "SND"

    def test_device_has_class_code(self):
        el = communication_function_snd(device_id="msg1", asid="ASID-001")
        device = el.find(f"{{{HL7_NS}}}device")
        assert device.get("classCode") == "DEV"

    def test_device_id_has_asid(self):
        el = communication_function_snd(device_id="msg1", asid="ASID-001")
        device = el.find(f"{{{HL7_NS}}}device")
        id_el = device.find(f"{{{HL7_NS}}}id")
        assert id_el.get("root") == NHSOid.SPINE_ASID.value
        assert id_el.get("extension") == "ASID-001"

    def test_tag_name(self):
        el = communication_function_snd(device_id="msg1", asid="X")
        assert _localname(el) == "communicationFunctionSnd"


class TestCommunicationFunctionRcv:
    def test_type_code_rcv(self):
        el = communication_function_rcv(device_id="msg1", asid="ASID-002")
        assert el.get("typeCode") == "RCV"

    def test_device_id_has_asid(self):
        el = communication_function_rcv(device_id="msg1", asid="ASID-002")
        device = el.find(f"{{{HL7_NS}}}device")
        id_el = device.find(f"{{{HL7_NS}}}id")
        assert id_el.get("extension") == "ASID-002"

    def test_tag_name(self):
        el = communication_function_rcv(device_id="msg1", asid="X")
        assert _localname(el) == "communicationFunctionRcv"


class TestAuthor:
    def test_type_code_aut(self):
        el = author(user_id="U1", role_profile_id="R1")
        assert el.get("typeCode") == "AUT"

    def test_agent_person_sds(self):
        el = author(user_id="U1", role_profile_id="R1")
        agent = el.find(f"{{{HL7_NS}}}AgentPersonSDS")
        assert agent is not None
        assert agent.get("classCode") == "AGNT"

    def test_role_profile_id(self):
        el = author(user_id="U1", role_profile_id="R1")
        agent = el.find(f"{{{HL7_NS}}}AgentPersonSDS")
        id_el = agent.find(f"{{{HL7_NS}}}id")
        assert id_el.get("root") == NHSOid.SDS_ROLE_PROFILE.value
        assert id_el.get("extension") == "R1"

    def test_user_id(self):
        el = author(user_id="U1", role_profile_id="R1")
        agent_person = el.find(f".//{{{HL7_NS}}}agentPersonSDS")
        id_el = agent_person.find(f"{{{HL7_NS}}}id")
        assert id_el.get("root") == NHSOid.SDS_USER_ID.value
        assert id_el.get("extension") == "U1"

    def test_job_role_code_present(self):
        el = author(user_id="U1", role_profile_id="R1", sds_job_role_code="R0260")
        part_role = el.find(f".//{{{HL7_NS}}}partSDSRole")
        id_el = part_role.find(f"{{{HL7_NS}}}id")
        assert id_el.get("root") == NHSOid.SDS_JOB_ROLE.value
        assert id_el.get("extension") == "R0260"

    def test_job_role_code_absent(self):
        el = author(user_id="U1", role_profile_id="R1")
        assert el.find(f".//{{{HL7_NS}}}partSDSRole") is None


class TestQueryByParameter:
    def test_has_query_id(self):
        el = query_by_parameter(nhs_number="9999999999")
        query_id = el.find(f"{{{HL7_NS}}}queryId")
        assert query_id is not None
        assert query_id.get("root") == NHSOid.SPINE_MESSAGE_ID.value

    def test_has_status_code(self):
        el = query_by_parameter(nhs_number="9999999999")
        status = el.find(f"{{{HL7_NS}}}statusCode")
        assert status.get("code") == "new"

    def test_nhs_number_parameter(self):
        el = query_by_parameter(nhs_number="9999999999")
        param_list = el.find(f"{{{HL7_NS}}}parameterList")
        nhs_num = param_list.find(f"{{{HL7_NS}}}nhsNumber")
        value_el = nhs_num.find(f"{{{HL7_NS}}}value")
        assert value_el.get("extension") == "9999999999"
        assert value_el.get("root") == NHSOid.NHS_NUMBER.value

    def test_person_name_parameter(self):
        el = query_by_parameter(family_name="Smith", given_name="John")
        param_list = el.find(f"{{{HL7_NS}}}parameterList")
        person_name = param_list.find(f"{{{HL7_NS}}}personName")
        value_el = person_name.find(f"{{{HL7_NS}}}value")
        assert value_el.find(f"{{{HL7_NS}}}given").text == "John"
        assert value_el.find(f"{{{HL7_NS}}}family").text == "Smith"

    def test_date_of_birth_parameter(self):
        el = query_by_parameter(date_of_birth="19800115")
        param_list = el.find(f"{{{HL7_NS}}}parameterList")
        dob = param_list.find(f"{{{HL7_NS}}}personDateOfBirth")
        assert dob.find(f"{{{HL7_NS}}}value").get("value") == "19800115"

    def test_postcode_parameter(self):
        el = query_by_parameter(postcode="SW1A 1AA")
        param_list = el.find(f"{{{HL7_NS}}}parameterList")
        address = param_list.find(f"{{{HL7_NS}}}personAddress")
        pc = address.find(f".//{{{HL7_NS}}}postalCode")
        assert pc.text == "SW1A 1AA"

    def test_gender_parameter(self):
        el = query_by_parameter(gender="M")
        param_list = el.find(f"{{{HL7_NS}}}parameterList")
        gender = param_list.find(f"{{{HL7_NS}}}personGender")
        value_el = gender.find(f"{{{HL7_NS}}}value")
        assert value_el.get("code") == "M"


class TestTriggerEvent:
    def test_returns_code_element(self):
        el = trigger_event("PRPA_TE201305UV02")
        assert _localname(el) == "code"
        assert el.get("code") == "PRPA_TE201305UV02"

    def test_code_system(self):
        el = trigger_event("PRPA_TE201305UV02", code_system="2.16.840.1.113883.1.6")
        assert el.get("codeSystem") == "2.16.840.1.113883.1.6"
