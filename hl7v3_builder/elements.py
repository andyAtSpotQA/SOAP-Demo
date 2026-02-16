"""
Reusable HL7 v3 composite element builders.

# HL7_SPEC: These build the standard structural elements that appear in
# the transmission wrapper and control act wrapper of HL7 v3 messages.
# Each function composes lower-level data types from datatypes.py into
# the correct element hierarchy per NHS Spine Message Implementation Guides.
"""

from lxml import etree
from .datatypes import HL7_NS, ii, cd, ts, pn
from .types import NHSOid


def _sub(parent: etree._Element, tag: str, **attribs) -> etree._Element:
    """Create a namespaced sub-element."""
    clean = {k: v for k, v in attribs.items() if v is not None}
    return etree.SubElement(parent, f"{{{HL7_NS}}}{tag}", **clean)


def communication_function_snd(
    device_id: str,
    asid: str,
) -> etree._Element:
    """Build a <communicationFunctionSnd> sender device element.

    # HL7_SPEC: Part of the transmission wrapper. Identifies the sending
    # system by its Spine Accredited System Identifier (ASID).
    # Structure: communicationFunctionSnd > device > id(ASID)
    """
    snd = etree.Element(f"{{{HL7_NS}}}communicationFunctionSnd", typeCode="SND")
    device = _sub(snd, "device", classCode="DEV", determinerCode="INSTANCE")
    device.append(ii(root=NHSOid.SPINE_ASID.value, extension=asid))
    return snd


def communication_function_rcv(
    device_id: str,
    asid: str,
) -> etree._Element:
    """Build a <communicationFunctionRcv> receiver device element.

    # HL7_SPEC: Part of the transmission wrapper. Identifies the target
    # system on the Spine network by its ASID.
    # Structure: communicationFunctionRcv > device > id(ASID)
    """
    rcv = etree.Element(f"{{{HL7_NS}}}communicationFunctionRcv", typeCode="RCV")
    device = _sub(rcv, "device", classCode="DEV", determinerCode="INSTANCE")
    device.append(ii(root=NHSOid.SPINE_ASID.value, extension=asid))
    return rcv


def author(
    user_id: str,
    role_profile_id: str,
    sds_job_role_code: str | None = None,
) -> etree._Element:
    """Build an <author> element for the control act wrapper.

    # HL7_SPEC: Identifies the person or system that authored the request.
    # NHS Spine requires:
    #   - SDS User ID (identifies the user on the Spine Directory)
    #   - SDS Role Profile ID (identifies the user's role)
    #   - Optionally SDS Job Role Code (RBAC role code)
    # Structure:
    #   author > AgentPersonSDS > id(SDS_ROLE_PROFILE)
    #     > agentPersonSDS > id(SDS_USER_ID)
    #     > part > partSDSRole > id(SDS_JOB_ROLE)
    """
    author_el = etree.Element(f"{{{HL7_NS}}}author", typeCode="AUT")

    agent = _sub(author_el, "AgentPersonSDS", classCode="AGNT")
    agent.append(ii(root=NHSOid.SDS_ROLE_PROFILE.value, extension=role_profile_id))

    agent_person = _sub(agent, "agentPersonSDS", classCode="PSN", determinerCode="INSTANCE")
    agent_person.append(ii(root=NHSOid.SDS_USER_ID.value, extension=user_id))

    if sds_job_role_code:
        part = _sub(agent, "part", typeCode="PART")
        part_role = _sub(part, "partSDSRole", classCode="ROL")
        part_role.append(ii(root=NHSOid.SDS_JOB_ROLE.value, extension=sds_job_role_code))

    return author_el


def query_by_parameter(
    nhs_number: str | None = None,
    family_name: str | None = None,
    given_name: str | None = None,
    date_of_birth: str | None = None,
    postcode: str | None = None,
    gender: str | None = None,
) -> etree._Element:
    """Build a <queryByParameter> element for demographic queries.

    # HL7_SPEC: Used in PRPA_IN201305UV02 (Patient Demographics Query)
    # to specify search criteria. Each parameter is wrapped in its own
    # element with a <value> child. At least one parameter should be set.
    # Structure:
    #   queryByParameter
    #     > queryId
    #     > statusCode code="new"
    #     > parameterList
    #       > nhsNumber > value > [II with NHS number]
    #       > person.name > value > [PN with name parts]
    #       > person.birthTime > value > [TS with date]
    #       > person.postalCode > value > [ST with postcode]
    #       > person.gender > value > [CD with gender code]
    """
    import uuid

    qbp = etree.Element(f"{{{HL7_NS}}}queryByParameter")

    # Query ID
    qbp.append(ii(root=NHSOid.SPINE_MESSAGE_ID.value,
                   extension=str(uuid.uuid4()).upper(),
                   tag="queryId"))

    # Status code
    _sub(qbp, "statusCode", code="new")

    # Response element grouping
    _sub(qbp, "responsePriorityCode", code="I")

    # Parameter list
    param_list = _sub(qbp, "parameterList")

    if nhs_number is not None:
        param = _sub(param_list, "nhsNumber")
        value_wrapper = _sub(param, "value")
        value_wrapper.set("root", NHSOid.NHS_NUMBER.value)
        value_wrapper.set("extension", nhs_number)

    if family_name is not None or given_name is not None:
        param = _sub(param_list, "personName")
        name_value = _sub(param, "value")
        if given_name is not None:
            given_el = _sub(name_value, "given")
            given_el.text = given_name
        if family_name is not None:
            family_el = _sub(name_value, "family")
            family_el.text = family_name

    if date_of_birth is not None:
        param = _sub(param_list, "personDateOfBirth")
        _sub(param, "value", value=date_of_birth)

    if postcode is not None:
        param = _sub(param_list, "personAddress")
        value_wrapper = _sub(param, "value")
        pc_el = _sub(value_wrapper, "postalCode")
        pc_el.text = postcode

    if gender is not None:
        param = _sub(param_list, "personGender")
        _sub(param, "value", code=gender, codeSystem="2.16.840.1.113883.5.1")

    return qbp


def trigger_event(
    code: str,
    code_system: str | None = None,
) -> etree._Element:
    """Build a trigger event <code> element for the control act.

    # HL7_SPEC: Identifies the trigger event that caused this message.
    # Placed as a <code> child of the ControlActEvent element.
    # Format: <code code="PRPA_TE201305UV02" codeSystem="..."/>
    """
    return cd(code, code_system, tag="code")
