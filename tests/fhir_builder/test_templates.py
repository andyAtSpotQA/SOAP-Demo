"""Tests for fhir_builder.templates — pre-built Bundle templates."""

from lxml import etree

from fhir_builder.builder import FHIRBundleBuilder, FHIRBundle
from fhir_builder.datatypes import FHIR_NS
from fhir_builder.types import BundleType
from fhir_builder.templates import (
    patient_search_bundle,
    message_bundle,
    gp_connect_structured_record,
    medication_request_bundle,
)


def _child_val(el, name):
    child = el.find(f"{{{FHIR_NS}}}{name}")
    return child.get("value") if child is not None else None


class TestPatientSearchBundle:
    def test_returns_builder(self):
        b = patient_search_bundle(
            "9999999999", "Smith", "John", "1980-01-15", "male",
        )
        assert isinstance(b, FHIRBundleBuilder)

    def test_builds_searchset(self):
        bundle = patient_search_bundle(
            "9999999999", "Smith", "John", "1980-01-15", "male",
        ).build()
        assert bundle.bundle_type == BundleType.SEARCHSET

    def test_has_patient_entry(self):
        bundle = patient_search_bundle(
            "9999999999", "Smith", "John", "1980-01-15", "male",
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) >= 1

    def test_total_is_set(self):
        bundle = patient_search_bundle(
            "9999999999", "Smith", "John", "1980-01-15", "male",
        ).build()
        assert _child_val(bundle.root, "total") == "1"

    def test_with_gp(self):
        bundle = patient_search_bundle(
            "9999999999", "Smith", "John", "1980-01-15", "male",
            gp_ods_code="Y12345", gp_name="Test GP",
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 2  # org + patient

    def test_gp_organization_included(self):
        bundle = patient_search_bundle(
            "9999999999", "Smith", "John", "1980-01-15", "male",
            gp_ods_code="Y12345", gp_name="Test GP",
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        resource_types = []
        for entry in entries:
            res = entry.find(f"{{{FHIR_NS}}}resource")
            if res is not None and len(res) > 0:
                resource_types.append(etree.QName(res[0].tag).localname)
        assert "Organization" in resource_types


class TestMessageBundle:
    def test_returns_builder(self):
        b = message_bundle(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test.nhs.uk",
        )
        assert isinstance(b, FHIRBundleBuilder)

    def test_builds_message_type(self):
        bundle = message_bundle(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test.nhs.uk",
        ).build()
        assert bundle.bundle_type == BundleType.MESSAGE

    def test_first_entry_is_message_header(self):
        bundle = message_bundle(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test.nhs.uk",
        ).build()
        first_entry = bundle.root.find(f"{{{FHIR_NS}}}entry")
        resource = first_entry.find(f"{{{FHIR_NS}}}resource")
        assert etree.QName(resource[0].tag).localname == "MessageHeader"

    def test_focus_resources_added(self):
        from fhir_builder.resources import patient
        pat = patient(
            nhs_number="9999999999", family_name="Smith",
            given_name="John", birth_date="1980-01-15", gender="male",
        )
        bundle = message_bundle(
            event_system="https://fhir.nhs.uk/MessageEvent",
            event_code="prescription-order",
            source_endpoint="https://test.nhs.uk",
            focus_resources=[pat],
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 2  # header + patient


class TestGPConnectStructuredRecord:
    def test_returns_builder(self):
        b = gp_connect_structured_record(
            "9999999999", "Smith", "John", "1980-01-15", "male",
        )
        assert isinstance(b, FHIRBundleBuilder)

    def test_builds_searchset(self):
        bundle = gp_connect_structured_record(
            "9999999999", "Smith", "John", "1980-01-15", "male",
        ).build()
        assert bundle.bundle_type == BundleType.SEARCHSET

    def test_has_org_practitioner_patient(self):
        bundle = gp_connect_structured_record(
            "9999999999", "Smith", "John", "1980-01-15", "male",
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 3  # org + practitioner + patient

    def test_with_allergies(self):
        bundle = gp_connect_structured_record(
            "9999999999", "Smith", "John", "1980-01-15", "male",
            allergies=[{"code": "91936005", "display": "Penicillin allergy"}],
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 4  # org + prac + patient + allergy

    def test_with_conditions(self):
        bundle = gp_connect_structured_record(
            "9999999999", "Smith", "John", "1980-01-15", "male",
            conditions=[{"code": "73211009", "display": "Diabetes mellitus"}],
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 4  # org + prac + patient + condition

    def test_with_allergies_and_conditions(self):
        bundle = gp_connect_structured_record(
            "9999999999", "Smith", "John", "1980-01-15", "male",
            allergies=[{"code": "91936005"}],
            conditions=[{"code": "73211009"}],
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 5  # org + prac + patient + allergy + condition


class TestMedicationRequestBundle:
    def test_returns_builder(self):
        b = medication_request_bundle(
            patient_nhs_number="9999999999",
            patient_family_name="Smith",
            patient_given_name="John",
            patient_birth_date="1980-01-15",
            patient_gender="male",
            medication_snomed_code="322236009",
            medication_display="Paracetamol 500mg tablets",
            dosage_text="Take one tablet",
        )
        assert isinstance(b, FHIRBundleBuilder)

    def test_builds_transaction(self):
        bundle = medication_request_bundle(
            patient_nhs_number="9999999999",
            patient_family_name="Smith",
            patient_given_name="John",
            patient_birth_date="1980-01-15",
            patient_gender="male",
            medication_snomed_code="322236009",
            medication_display="Paracetamol 500mg tablets",
            dosage_text="Take one tablet",
        ).build()
        assert bundle.bundle_type == BundleType.TRANSACTION

    def test_has_four_entries(self):
        bundle = medication_request_bundle(
            patient_nhs_number="9999999999",
            patient_family_name="Smith",
            patient_given_name="John",
            patient_birth_date="1980-01-15",
            patient_gender="male",
            medication_snomed_code="322236009",
            medication_display="Paracetamol 500mg tablets",
            dosage_text="Take one tablet",
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 4  # med_req + patient + prac + org

    def test_all_entries_have_request(self):
        bundle = medication_request_bundle(
            patient_nhs_number="9999999999",
            patient_family_name="Smith",
            patient_given_name="John",
            patient_birth_date="1980-01-15",
            patient_gender="male",
            medication_snomed_code="322236009",
            medication_display="Paracetamol 500mg tablets",
            dosage_text="Take one tablet",
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        for entry in entries:
            request = entry.find(f"{{{FHIR_NS}}}request")
            assert request is not None
            assert entry.find(f"{{{FHIR_NS}}}request/{{{FHIR_NS}}}method") is not None

    def test_all_entries_use_post(self):
        bundle = medication_request_bundle(
            patient_nhs_number="9999999999",
            patient_family_name="Smith",
            patient_given_name="John",
            patient_birth_date="1980-01-15",
            patient_gender="male",
            medication_snomed_code="322236009",
            medication_display="Paracetamol 500mg tablets",
            dosage_text="Take one tablet",
        ).build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        for entry in entries:
            method = entry.find(f"{{{FHIR_NS}}}request/{{{FHIR_NS}}}method")
            assert method.get("value") == "POST"
