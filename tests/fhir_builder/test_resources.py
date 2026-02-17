"""Tests for fhir_builder.resources — FHIR R4 resource factories."""

from lxml import etree

from fhir_builder.datatypes import FHIR_NS
from fhir_builder.resources import (
    patient,
    organization,
    practitioner,
    medication_request,
    allergy_intolerance,
    condition,
    message_header,
)
from fhir_builder.types import (
    NHSSystem,
    UKCoreProfile,
    SnomedSystem,
)


def _localname(el):
    return etree.QName(el.tag).localname


def _child(el, name):
    return el.find(f"{{{FHIR_NS}}}{name}")


def _child_val(el, name):
    child = _child(el, name)
    return child.get("value") if child is not None else None


def _find_val(el, path):
    """Find deep nested child and return its value attribute.
    Path segments are each namespaced, e.g. 'meta/profile' -> {ns}meta/{ns}profile.
    """
    parts = path.split("/")
    xpath = "/".join(f"{{{FHIR_NS}}}{p}" for p in parts)
    found = el.find(f".//{xpath}")
    return found.get("value") if found is not None else None


class TestPatient:
    def test_resource_type(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        assert _localname(el) == "Patient"

    def test_has_id(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        assert _child_val(el, "id") is not None

    def test_custom_id(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male",
                     resource_id="custom-123")
        assert _child_val(el, "id") == "custom-123"

    def test_has_uk_core_profile(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        profile = _find_val(el, "meta/profile")
        assert profile == UKCoreProfile.PATIENT.value

    def test_nhs_number_identifier(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        ident = _child(el, "identifier")
        system = _child_val(ident, "system")
        assert system == NHSSystem.NHS_NUMBER.value

    def test_nhs_number_value(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        ident = _child(el, "identifier")
        assert _child_val(ident, "value") == "9999999999"

    def test_name_family(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        name = _child(el, "name")
        assert _child_val(name, "family") == "Smith"

    def test_name_given(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        name = _child(el, "name")
        assert _child_val(name, "given") == "John"

    def test_gender(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        assert _child_val(el, "gender") == "male"

    def test_birth_date(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        assert _child_val(el, "birthDate") == "1980-01-15"

    def test_telecom_phone(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male",
                     telecom_phone="01onal123456")
        telecoms = el.findall(f"{{{FHIR_NS}}}telecom")
        assert len(telecoms) >= 1

    def test_address(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male",
                     address_city="London", address_postal_code="SW1A 1AA")
        addr = _child(el, "address")
        assert addr is not None

    def test_gp_reference(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male",
                     gp_reference="Organization/123")
        gp = _child(el, "generalPractitioner")
        assert _child_val(gp, "reference") == "Organization/123"

    def test_namespace(self):
        el = patient(nhs_number="9999999999", family_name="Smith",
                     given_name="John", birth_date="1980-01-15", gender="male")
        assert FHIR_NS in el.tag


class TestOrganization:
    def test_resource_type(self):
        el = organization(ods_code="Y12345", name="Test GP Practice")
        assert _localname(el) == "Organization"

    def test_ods_code_identifier(self):
        el = organization(ods_code="Y12345", name="Test GP Practice")
        ident = _child(el, "identifier")
        assert _child_val(ident, "system") == NHSSystem.ODS_ORGANIZATION_CODE.value

    def test_name(self):
        el = organization(ods_code="Y12345", name="Test GP Practice")
        assert _child_val(el, "name") == "Test GP Practice"

    def test_has_uk_core_profile(self):
        el = organization(ods_code="Y12345", name="Test GP Practice")
        assert _find_val(el, "meta/profile") == UKCoreProfile.ORGANIZATION.value

    def test_telecom(self):
        el = organization(ods_code="Y12345", name="Test", telecom_phone="01234567890")
        assert _child(el, "telecom") is not None

    def test_address(self):
        el = organization(ods_code="Y12345", name="Test",
                          address_city="Leeds", address_postal_code="LS1 1AA")
        assert _child(el, "address") is not None


class TestPractitioner:
    def test_resource_type(self):
        el = practitioner(sds_user_id="555254240100", family_name="Doctor")
        assert _localname(el) == "Practitioner"

    def test_sds_identifier(self):
        el = practitioner(sds_user_id="555254240100", family_name="Doctor")
        ident = _child(el, "identifier")
        assert _child_val(ident, "system") == NHSSystem.SDS_USER_ID.value

    def test_name(self):
        el = practitioner(sds_user_id="555254240100", family_name="Doctor",
                          given_name="Test")
        name = _child(el, "name")
        assert _child_val(name, "family") == "Doctor"

    def test_prefix(self):
        el = practitioner(sds_user_id="555254240100", family_name="Doctor",
                          prefix="Dr")
        name = _child(el, "name")
        assert _child_val(name, "prefix") == "Dr"

    def test_has_uk_core_profile(self):
        el = practitioner(sds_user_id="555254240100", family_name="Doctor")
        assert _find_val(el, "meta/profile") == UKCoreProfile.PRACTITIONER.value


class TestMedicationRequest:
    def test_resource_type(self):
        el = medication_request(status="active", intent="order",
                                patient_ref="Patient/123")
        assert _localname(el) == "MedicationRequest"

    def test_status(self):
        el = medication_request(status="active", intent="order",
                                patient_ref="Patient/123")
        assert _child_val(el, "status") == "active"

    def test_intent(self):
        el = medication_request(status="active", intent="order",
                                patient_ref="Patient/123")
        assert _child_val(el, "intent") == "order"

    def test_subject_reference(self):
        el = medication_request(status="active", intent="order",
                                patient_ref="Patient/123")
        subject = _child(el, "subject")
        assert _child_val(subject, "reference") == "Patient/123"

    def test_medication_codeable_concept(self):
        el = medication_request(
            status="active", intent="order", patient_ref="Patient/123",
            medication_code_system=SnomedSystem.SNOMED_CT.value,
            medication_code="322236009",
            medication_display="Paracetamol 500mg tablets",
        )
        med = _child(el, "medicationCodeableConcept")
        assert med is not None

    def test_medication_reference(self):
        el = medication_request(
            status="active", intent="order", patient_ref="Patient/123",
            medication_ref="Medication/456",
        )
        med_ref = _child(el, "medicationReference")
        assert _child_val(med_ref, "reference") == "Medication/456"

    def test_requester(self):
        el = medication_request(
            status="active", intent="order", patient_ref="Patient/123",
            requester_ref="Practitioner/456",
        )
        assert _child(el, "requester") is not None

    def test_group_identifier(self):
        el = medication_request(
            status="active", intent="order", patient_ref="Patient/123",
            group_identifier_value="RX-001",
        )
        gi = _child(el, "groupIdentifier")
        assert _child_val(gi, "value") == "RX-001"

    def test_dosage_instruction(self):
        el = medication_request(
            status="active", intent="order", patient_ref="Patient/123",
            dosage_text="Take one tablet twice daily",
        )
        dosage = _child(el, "dosageInstruction")
        assert _child_val(dosage, "text") == "Take one tablet twice daily"

    def test_has_uk_core_profile(self):
        el = medication_request(status="active", intent="order",
                                patient_ref="Patient/123")
        assert _find_val(el, "meta/profile") == UKCoreProfile.MEDICATION_REQUEST.value


class TestAllergyIntolerance:
    def test_resource_type(self):
        el = allergy_intolerance(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="91936005",
        )
        assert _localname(el) == "AllergyIntolerance"

    def test_clinical_status(self):
        el = allergy_intolerance(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="91936005",
        )
        cs = _child(el, "clinicalStatus")
        assert cs is not None

    def test_verification_status(self):
        el = allergy_intolerance(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="91936005",
        )
        vs = _child(el, "verificationStatus")
        assert vs is not None

    def test_code(self):
        el = allergy_intolerance(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="91936005",
            code_display="Penicillin allergy",
        )
        code_el = _child(el, "code")
        assert code_el is not None

    def test_patient_ref(self):
        el = allergy_intolerance(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="91936005",
        )
        patient_el = _child(el, "patient")
        assert _child_val(patient_el, "reference") == "Patient/123"

    def test_has_uk_core_profile(self):
        el = allergy_intolerance(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="91936005",
        )
        assert _find_val(el, "meta/profile") == UKCoreProfile.ALLERGY_INTOLERANCE.value


class TestCondition:
    def test_resource_type(self):
        el = condition(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="73211009",
        )
        assert _localname(el) == "Condition"

    def test_clinical_status(self):
        el = condition(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="73211009",
        )
        assert _child(el, "clinicalStatus") is not None

    def test_subject_reference(self):
        el = condition(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="73211009",
        )
        subject = _child(el, "subject")
        assert _child_val(subject, "reference") == "Patient/123"

    def test_has_uk_core_profile(self):
        el = condition(
            patient_ref="Patient/123",
            code_system=SnomedSystem.SNOMED_CT.value,
            code_value="73211009",
        )
        assert _find_val(el, "meta/profile") == UKCoreProfile.CONDITION.value


class TestMessageHeader:
    def test_resource_type(self):
        el = message_header(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test-system.nhs.uk",
        )
        assert _localname(el) == "MessageHeader"

    def test_event_coding(self):
        el = message_header(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test-system.nhs.uk",
        )
        event = _child(el, "eventCoding")
        assert event is not None

    def test_source_endpoint(self):
        el = message_header(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test-system.nhs.uk",
        )
        source = _child(el, "source")
        assert _child_val(source, "endpoint") == "https://test-system.nhs.uk"

    def test_destination(self):
        el = message_header(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test-system.nhs.uk",
            destination_endpoint="https://spine.nhs.uk",
        )
        dest = _child(el, "destination")
        assert _child_val(dest, "endpoint") == "https://spine.nhs.uk"

    def test_focus_refs(self):
        el = message_header(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test-system.nhs.uk",
            focus_refs=["MedicationRequest/123", "Patient/456"],
        )
        focus_elements = el.findall(f"{{{FHIR_NS}}}focus")
        assert len(focus_elements) == 2

    def test_source_name(self):
        el = message_header(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test-system.nhs.uk",
            source_name="TestApp",
        )
        source = _child(el, "source")
        assert _child_val(source, "name") == "TestApp"

    def test_has_uk_core_profile(self):
        el = message_header(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test-system.nhs.uk",
        )
        assert _find_val(el, "meta/profile") == UKCoreProfile.MESSAGE_HEADER.value
