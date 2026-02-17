"""
Pre-built Bundle templates for common NHS FHIR interactions.

# FHIR_SPEC: Each template creates a FHIRBundleBuilder pre-configured
# for a specific NHS interaction pattern. The caller can add/modify
# entries and call .build() to produce the final Bundle.

Usage:
    bundle = patient_search_bundle(
        "9999999999", "Smith", "John", "1980-01-15", "male"
    ).build()
    print(bundle.to_xml())
"""

from __future__ import annotations

from .builder import FHIRBundleBuilder
from .resources import (
    patient,
    organization,
    practitioner,
    medication_request,
    allergy_intolerance,
    condition,
    message_header,
)
from .types import (
    BundleType,
    HTTPVerb,
    NHSSystem,
    SnomedSystem,
    ClinicalStatus,
    VerificationStatus,
)


def patient_search_bundle(
    nhs_number: str,
    family_name: str,
    given_name: str,
    birth_date: str,
    gender: str,
    gp_ods_code: str | None = None,
    gp_name: str | None = None,
) -> FHIRBundleBuilder:
    """Template for a PDS-style patient search result Bundle.

    # FHIR_SPEC: PDS FHIR API returns a searchset Bundle containing
    # matching Patient resources. If the patient has a registered GP,
    # the Organization is included and referenced via generalPractitioner.

    Returns a builder — call .build() to produce the Bundle.

    Args:
        nhs_number: Patient's NHS Number.
        family_name: Patient's surname.
        given_name: Patient's first name.
        birth_date: Date of birth (YYYY-MM-DD).
        gender: Administrative gender.
        gp_ods_code: Optional GP practice ODS code.
        gp_name: Optional GP practice name.
    """
    builder = (
        FHIRBundleBuilder()
        .set_type(BundleType.SEARCHSET)
        .set_timestamp()
    )

    gp_ref = None
    if gp_ods_code and gp_name:
        org_el = organization(ods_code=gp_ods_code, name=gp_name)
        org_id = org_el.find("{http://hl7.org/fhir}id").get("value")
        gp_ref = f"Organization/{org_id}"
        builder.add_entry(org_el, search_mode="include")

    patient_el = patient(
        nhs_number=nhs_number,
        family_name=family_name,
        given_name=given_name,
        birth_date=birth_date,
        gender=gender,
        gp_reference=gp_ref,
    )
    builder.add_entry(patient_el, search_mode="match")
    builder.set_total(1)

    return builder


def message_bundle(
    event_system: str,
    event_code: str,
    source_endpoint: str,
    destination_endpoint: str | None = None,
    focus_resources: list | None = None,
    event_display: str | None = None,
    source_name: str | None = None,
) -> FHIRBundleBuilder:
    """Template for a generic FHIR message Bundle.

    # FHIR_SPEC: Message bundles are used for inter-system messaging.
    # The first entry must be a MessageHeader, which references the
    # focus resources that the message is about.

    Returns a builder — call .build() to produce the Bundle.

    Args:
        event_system: Code system for the message event.
        event_code: Event code identifying the message type.
        source_endpoint: Sending system endpoint URL.
        destination_endpoint: Receiving system endpoint URL.
        focus_resources: List of lxml.etree.Element resources to include.
        event_display: Display text for the event.
        source_name: Name of the source application.
    """
    focus_resources = focus_resources or []

    # Collect focus references from resource IDs
    focus_refs = []
    for res in focus_resources:
        id_el = res.find("{http://hl7.org/fhir}id")
        if id_el is not None:
            res_type = res.tag.split("}")[-1] if "}" in res.tag else res.tag
            focus_refs.append(f"{res_type}/{id_el.get('value')}")

    header_el = message_header(
        event_system=event_system,
        event_code=event_code,
        source_endpoint=source_endpoint,
        destination_endpoint=destination_endpoint,
        focus_refs=focus_refs,
        event_display=event_display,
        source_name=source_name,
    )

    builder = (
        FHIRBundleBuilder()
        .set_type(BundleType.MESSAGE)
        .set_timestamp()
        .add_entry(header_el)
    )

    for res in focus_resources:
        builder.add_entry(res)

    return builder


def gp_connect_structured_record(
    nhs_number: str,
    family_name: str,
    given_name: str,
    birth_date: str,
    gender: str,
    gp_ods_code: str = "Y12345",
    gp_name: str = "Test GP Practice",
    practitioner_sds_id: str = "555254240100",
    practitioner_family: str = "Doctor",
    practitioner_given: str = "Test",
    allergies: list[dict] | None = None,
    conditions: list[dict] | None = None,
) -> FHIRBundleBuilder:
    """Template for a GP Connect Access Structured Record response.

    # FHIR_SPEC: GP Connect returns a searchset Bundle containing the
    # patient's structured clinical record: Patient, Organization,
    # Practitioner, plus clinical resources (AllergyIntolerance,
    # Condition, MedicationRequest, etc.).

    Returns a builder — call .build() to produce the Bundle.

    Args:
        nhs_number: Patient's NHS Number.
        family_name: Patient's surname.
        given_name: Patient's first name.
        birth_date: Date of birth (YYYY-MM-DD).
        gender: Administrative gender.
        gp_ods_code: GP practice ODS code.
        gp_name: GP practice name.
        practitioner_sds_id: Practitioner's SDS User ID.
        practitioner_family: Practitioner's surname.
        practitioner_given: Practitioner's first name.
        allergies: List of allergy dicts with keys: code_system, code, display.
        conditions: List of condition dicts with keys: code_system, code, display.
    """
    builder = (
        FHIRBundleBuilder()
        .set_type(BundleType.SEARCHSET)
        .set_timestamp()
    )

    # Organization
    org_el = organization(ods_code=gp_ods_code, name=gp_name)
    org_id = org_el.find("{http://hl7.org/fhir}id").get("value")
    builder.add_entry(org_el, search_mode="include")

    # Practitioner
    prac_el = practitioner(
        sds_user_id=practitioner_sds_id,
        family_name=practitioner_family,
        given_name=practitioner_given,
    )
    builder.add_entry(prac_el, search_mode="include")

    # Patient
    patient_el = patient(
        nhs_number=nhs_number,
        family_name=family_name,
        given_name=given_name,
        birth_date=birth_date,
        gender=gender,
        gp_reference=f"Organization/{org_id}",
    )
    patient_id = patient_el.find("{http://hl7.org/fhir}id").get("value")
    builder.add_entry(patient_el, search_mode="match")

    patient_ref = f"Patient/{patient_id}"

    # Allergies
    if allergies:
        for allergy_data in allergies:
            allergy_el = allergy_intolerance(
                patient_ref=patient_ref,
                code_system=allergy_data.get("code_system", SnomedSystem.SNOMED_CT.value),
                code_value=allergy_data["code"],
                code_display=allergy_data.get("display"),
            )
            builder.add_entry(allergy_el, search_mode="match")

    # Conditions
    if conditions:
        for condition_data in conditions:
            condition_el = condition(
                patient_ref=patient_ref,
                code_system=condition_data.get("code_system", SnomedSystem.SNOMED_CT.value),
                code_value=condition_data["code"],
                code_display=condition_data.get("display"),
            )
            builder.add_entry(condition_el, search_mode="match")

    return builder


def medication_request_bundle(
    patient_nhs_number: str,
    patient_family_name: str,
    patient_given_name: str,
    patient_birth_date: str,
    patient_gender: str,
    medication_snomed_code: str,
    medication_display: str,
    dosage_text: str,
    prescriber_sds_id: str = "555254240100",
    prescriber_family: str = "Doctor",
    prescriber_given: str = "Test",
    organization_ods_code: str = "Y12345",
    organization_name: str = "Test GP Practice",
    prescription_id: str | None = None,
) -> FHIRBundleBuilder:
    """Template for an EPS-style MedicationRequest transaction Bundle.

    # FHIR_SPEC: EPS uses transaction Bundles to submit prescriptions.
    # Each entry has a request.method (POST) and request.url targeting
    # the resource type. The Bundle contains: MedicationRequest, Patient,
    # Practitioner, and Organization.

    Returns a builder — call .build() to produce the Bundle.

    Args:
        patient_nhs_number: Patient's NHS Number.
        patient_family_name: Patient's surname.
        patient_given_name: Patient's first name.
        patient_birth_date: Patient date of birth (YYYY-MM-DD).
        patient_gender: Administrative gender.
        medication_snomed_code: SNOMED CT code for the medication.
        medication_display: Medication display name.
        dosage_text: Free-text dosage instruction.
        prescriber_sds_id: Prescriber's SDS User ID.
        prescriber_family: Prescriber's surname.
        prescriber_given: Prescriber's first name.
        organization_ods_code: Prescribing organization ODS code.
        organization_name: Prescribing organization name.
        prescription_id: Optional prescription order number.
    """
    builder = (
        FHIRBundleBuilder()
        .set_type(BundleType.TRANSACTION)
        .set_timestamp()
    )

    # Create resources
    org_el = organization(ods_code=organization_ods_code, name=organization_name)
    org_id = org_el.find("{http://hl7.org/fhir}id").get("value")

    prac_el = practitioner(
        sds_user_id=prescriber_sds_id,
        family_name=prescriber_family,
        given_name=prescriber_given,
    )
    prac_id = prac_el.find("{http://hl7.org/fhir}id").get("value")

    patient_el = patient(
        nhs_number=patient_nhs_number,
        family_name=patient_family_name,
        given_name=patient_given_name,
        birth_date=patient_birth_date,
        gender=patient_gender,
        gp_reference=f"Organization/{org_id}",
    )
    patient_id = patient_el.find("{http://hl7.org/fhir}id").get("value")

    med_req_el = medication_request(
        status="active",
        intent="order",
        patient_ref=f"Patient/{patient_id}",
        medication_code_system=SnomedSystem.SNOMED_CT.value,
        medication_code=medication_snomed_code,
        medication_display=medication_display,
        requester_ref=f"Practitioner/{prac_id}",
        group_identifier_value=prescription_id,
        dosage_text=dosage_text,
    )

    # Add entries with transaction request metadata
    post = HTTPVerb.POST.value

    builder.add_entry(
        med_req_el, request_method=post, request_url="MedicationRequest",
    )
    builder.add_entry(
        patient_el, request_method=post, request_url="Patient",
    )
    builder.add_entry(
        prac_el, request_method=post, request_url="Practitioner",
    )
    builder.add_entry(
        org_el, request_method=post, request_url="Organization",
    )

    return builder
