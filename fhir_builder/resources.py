"""
FHIR R4 resource factory functions.

# FHIR_SPEC: Each factory creates a complete FHIR resource element with
# the correct resourceType, auto-generated UUID id, and UK Core profile
# in meta. Resources are returned as lxml.etree.Element instances ready
# to be added to a Bundle via FHIRBundleBuilder.

All resources use the FHIR namespace (http://hl7.org/fhir) and follow
UK Core profile conventions for NHS systems.
"""

from __future__ import annotations

import uuid
from lxml import etree

from .datatypes import (
    FHIR_NS,
    NSMAP,
    _fhir_sub,
    identifier,
    human_name,
    address,
    codeable_concept,
    reference,
    contact_point,
    meta,
)
from .types import (
    ResourceType,
    NHSSystem,
    UKCoreProfile,
    ClinicalStatus,
    VerificationStatus,
    CONDITION_CLINICAL_STATUS_SYSTEM,
    CONDITION_VERIFICATION_STATUS_SYSTEM,
    ALLERGY_CLINICAL_STATUS_SYSTEM,
    ALLERGY_VERIFICATION_STATUS_SYSTEM,
)


def _resource_root(
    resource_type: ResourceType,
    profile: UKCoreProfile,
    resource_id: str | None = None,
) -> etree._Element:
    """Create a resource root element with id and meta/profile.

    # FHIR_SPEC: Every resource has a resourceType (implicit in the XML
    # element name), an id, and a meta block declaring its profile.
    """
    root = etree.Element(f"{{{FHIR_NS}}}{resource_type.value}", nsmap=NSMAP)
    rid = resource_id or str(uuid.uuid4())
    _fhir_sub(root, "id", value=rid)
    root.append(meta(profile=profile.value))
    return root


def patient(
    nhs_number: str,
    family_name: str,
    given_name: str | list[str],
    birth_date: str,
    gender: str,
    address_lines: str | list[str] | None = None,
    address_city: str | None = None,
    address_postal_code: str | None = None,
    telecom_phone: str | None = None,
    telecom_email: str | None = None,
    gp_reference: str | None = None,
    resource_id: str | None = None,
) -> etree._Element:
    """Create a FHIR Patient resource with NHS Number identifier.

    # FHIR_SPEC: Patient is the core demographic resource. NHS Number is
    # the primary identifier (system: https://fhir.nhs.uk/Id/nhs-number).
    # UK Core profile: UKCore-Patient.

    Args:
        nhs_number: 10-digit NHS Number.
        family_name: Patient's surname.
        given_name: Patient's first name(s).
        birth_date: Date of birth (YYYY-MM-DD).
        gender: Administrative gender (male/female/other/unknown).
        address_lines: Street address line(s).
        address_city: City name.
        address_postal_code: UK postcode.
        telecom_phone: Phone number.
        telecom_email: Email address.
        gp_reference: Reference to GP Organization (e.g. "Organization/uuid").
        resource_id: Override auto-generated UUID.
    """
    root = _resource_root(ResourceType.PATIENT, UKCoreProfile.PATIENT, resource_id)

    root.append(identifier(
        system=NHSSystem.NHS_NUMBER.value,
        value=nhs_number,
        use="official",
    ))

    root.append(human_name(
        family=family_name,
        given=given_name,
        use="official",
    ))

    if telecom_phone:
        root.append(contact_point(system="phone", value=telecom_phone, use="home"))
    if telecom_email:
        root.append(contact_point(system="email", value=telecom_email, use="home"))

    _fhir_sub(root, "gender", value=gender)
    _fhir_sub(root, "birthDate", value=birth_date)

    if address_lines or address_city or address_postal_code:
        root.append(address(
            line=address_lines,
            city=address_city,
            postal_code=address_postal_code,
        ))

    if gp_reference:
        root.append(reference(ref=gp_reference, tag="generalPractitioner"))

    return root


def organization(
    ods_code: str,
    name: str,
    telecom_phone: str | None = None,
    address_lines: str | list[str] | None = None,
    address_city: str | None = None,
    address_postal_code: str | None = None,
    resource_id: str | None = None,
) -> etree._Element:
    """Create a FHIR Organization resource with ODS code identifier.

    # FHIR_SPEC: Organization represents a GP practice, trust, etc.
    # ODS code is the primary NHS identifier for organizations
    # (system: https://fhir.nhs.uk/Id/ods-organization-code).
    """
    root = _resource_root(
        ResourceType.ORGANIZATION, UKCoreProfile.ORGANIZATION, resource_id,
    )

    root.append(identifier(
        system=NHSSystem.ODS_ORGANIZATION_CODE.value,
        value=ods_code,
        use="official",
    ))

    _fhir_sub(root, "name", value=name)

    if telecom_phone:
        root.append(contact_point(system="phone", value=telecom_phone, use="work"))

    if address_lines or address_city or address_postal_code:
        root.append(address(
            line=address_lines,
            city=address_city,
            postal_code=address_postal_code,
        ))

    return root


def practitioner(
    sds_user_id: str,
    family_name: str,
    given_name: str | list[str] | None = None,
    prefix: str | None = None,
    resource_id: str | None = None,
) -> etree._Element:
    """Create a FHIR Practitioner resource with SDS User ID.

    # FHIR_SPEC: Practitioner represents a healthcare provider.
    # SDS User ID is the Spine Directory Service identifier
    # (system: https://fhir.nhs.uk/Id/sds-user-id).
    """
    root = _resource_root(
        ResourceType.PRACTITIONER, UKCoreProfile.PRACTITIONER, resource_id,
    )

    root.append(identifier(
        system=NHSSystem.SDS_USER_ID.value,
        value=sds_user_id,
        use="official",
    ))

    root.append(human_name(
        family=family_name,
        given=given_name,
        prefix=prefix,
        use="official",
    ))

    return root


def medication_request(
    status: str,
    intent: str,
    patient_ref: str,
    medication_code_system: str | None = None,
    medication_code: str | None = None,
    medication_display: str | None = None,
    medication_ref: str | None = None,
    requester_ref: str | None = None,
    group_identifier_value: str | None = None,
    dosage_text: str | None = None,
    resource_id: str | None = None,
) -> etree._Element:
    """Create a FHIR MedicationRequest resource.

    # FHIR_SPEC: MedicationRequest represents an order or request for
    # medication supply/administration. Used heavily in EPS (Electronic
    # Prescription Service). Can reference medication by code or by
    # reference to a Medication resource.

    Args:
        status: Request status (active, completed, etc.).
        intent: Request intent (order, plan, etc.).
        patient_ref: Reference to the Patient (e.g. "Patient/uuid").
        medication_code_system: Code system for medication (e.g. dm+d).
        medication_code: Medication code value.
        medication_display: Medication display name.
        medication_ref: Alternative: reference to a Medication resource.
        requester_ref: Reference to the prescriber Practitioner.
        group_identifier_value: Prescription group identifier.
        dosage_text: Free-text dosage instruction.
    """
    root = _resource_root(
        ResourceType.MEDICATION_REQUEST, UKCoreProfile.MEDICATION_REQUEST,
        resource_id,
    )

    if group_identifier_value:
        root.append(identifier(
            system=NHSSystem.PRESCRIPTION_ORDER_ID.value,
            value=group_identifier_value,
            tag="groupIdentifier",
        ))

    _fhir_sub(root, "status", value=status)
    _fhir_sub(root, "intent", value=intent)

    if medication_code_system and medication_code:
        root.append(codeable_concept(
            system=medication_code_system,
            code=medication_code,
            display=medication_display,
            tag="medicationCodeableConcept",
        ))
    elif medication_ref:
        root.append(reference(ref=medication_ref, tag="medicationReference"))

    root.append(reference(ref=patient_ref, tag="subject"))

    if requester_ref:
        root.append(reference(ref=requester_ref, tag="requester"))

    if dosage_text:
        dosage_el = _fhir_sub(root, "dosageInstruction")
        _fhir_sub(dosage_el, "text", value=dosage_text)

    return root


def allergy_intolerance(
    patient_ref: str,
    code_system: str,
    code_value: str,
    code_display: str | None = None,
    clinical_status: str = ClinicalStatus.ACTIVE.value,
    verification_status: str = VerificationStatus.CONFIRMED.value,
    resource_id: str | None = None,
) -> etree._Element:
    """Create a FHIR AllergyIntolerance resource.

    # FHIR_SPEC: AllergyIntolerance records a patient's allergies or
    # adverse reactions. Clinical status and verification status are
    # required CodeableConcepts with specific terminology system URIs.
    """
    root = _resource_root(
        ResourceType.ALLERGY_INTOLERANCE, UKCoreProfile.ALLERGY_INTOLERANCE,
        resource_id,
    )

    root.append(codeable_concept(
        system=ALLERGY_CLINICAL_STATUS_SYSTEM,
        code=clinical_status,
        tag="clinicalStatus",
    ))

    root.append(codeable_concept(
        system=ALLERGY_VERIFICATION_STATUS_SYSTEM,
        code=verification_status,
        tag="verificationStatus",
    ))

    root.append(codeable_concept(
        system=code_system,
        code=code_value,
        display=code_display,
        tag="code",
    ))

    root.append(reference(ref=patient_ref, tag="patient"))

    return root


def condition(
    patient_ref: str,
    code_system: str,
    code_value: str,
    code_display: str | None = None,
    clinical_status: str = ClinicalStatus.ACTIVE.value,
    verification_status: str = VerificationStatus.CONFIRMED.value,
    resource_id: str | None = None,
) -> etree._Element:
    """Create a FHIR Condition resource.

    # FHIR_SPEC: Condition records a clinical condition, problem, or
    # diagnosis. Similar to AllergyIntolerance but uses condition-specific
    # terminology system URIs for clinical/verification status.
    """
    root = _resource_root(
        ResourceType.CONDITION, UKCoreProfile.CONDITION, resource_id,
    )

    root.append(codeable_concept(
        system=CONDITION_CLINICAL_STATUS_SYSTEM,
        code=clinical_status,
        tag="clinicalStatus",
    ))

    root.append(codeable_concept(
        system=CONDITION_VERIFICATION_STATUS_SYSTEM,
        code=verification_status,
        tag="verificationStatus",
    ))

    root.append(codeable_concept(
        system=code_system,
        code=code_value,
        display=code_display,
        tag="code",
    ))

    root.append(reference(ref=patient_ref, tag="subject"))

    return root


def message_header(
    event_system: str,
    event_code: str,
    source_endpoint: str,
    destination_endpoint: str | None = None,
    focus_refs: list[str] | None = None,
    event_display: str | None = None,
    source_name: str | None = None,
    resource_id: str | None = None,
) -> etree._Element:
    """Create a FHIR MessageHeader resource.

    # FHIR_SPEC: MessageHeader is the first resource in a message Bundle.
    # It carries the event code identifying the message type, the source
    # and destination systems, and references to the focus resources
    # that the message is about.

    Args:
        event_system: Code system URI for the event (e.g. a MessageEvent URI).
        event_code: Event code value.
        source_endpoint: URL of the sending system.
        destination_endpoint: URL of the receiving system.
        focus_refs: List of references to focus resources in the bundle.
        event_display: Display text for the event coding.
        source_name: Name of the source application.
    """
    root = _resource_root(
        ResourceType.MESSAGE_HEADER, UKCoreProfile.MESSAGE_HEADER, resource_id,
    )

    root.append(codeable_concept(
        system=event_system,
        code=event_code,
        display=event_display,
        tag="eventCoding",
    ))

    if destination_endpoint:
        dest_el = _fhir_sub(root, "destination")
        _fhir_sub(dest_el, "endpoint", value=destination_endpoint)

    source_el = _fhir_sub(root, "source")
    if source_name:
        _fhir_sub(source_el, "name", value=source_name)
    _fhir_sub(source_el, "endpoint", value=source_endpoint)

    if focus_refs:
        for ref_str in focus_refs:
            root.append(reference(ref=ref_str, tag="focus"))

    return root
