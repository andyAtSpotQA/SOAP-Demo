"""Tests for fhir_builder.types — FHIR R4 enumerations and constants."""

from fhir_builder.types import (
    ResourceType,
    BundleType,
    HTTPVerb,
    AdministrativeGender,
    NameUse,
    AddressUse,
    AddressType,
    IdentifierUse,
    ContactPointSystem,
    ContactPointUse,
    ClinicalStatus,
    VerificationStatus,
    MedicationRequestStatus,
    MedicationRequestIntent,
    NHSSystem,
    UKCoreProfile,
    SnomedSystem,
    CONDITION_CLINICAL_STATUS_SYSTEM,
    CONDITION_VERIFICATION_STATUS_SYSTEM,
    ALLERGY_CLINICAL_STATUS_SYSTEM,
    ALLERGY_VERIFICATION_STATUS_SYSTEM,
)


class TestResourceType:
    def test_patient(self):
        assert ResourceType.PATIENT == "Patient"

    def test_organization(self):
        assert ResourceType.ORGANIZATION == "Organization"

    def test_practitioner(self):
        assert ResourceType.PRACTITIONER == "Practitioner"

    def test_medication_request(self):
        assert ResourceType.MEDICATION_REQUEST == "MedicationRequest"

    def test_bundle(self):
        assert ResourceType.BUNDLE == "Bundle"

    def test_member_count(self):
        assert len(ResourceType) == 8


class TestBundleType:
    def test_message(self):
        assert BundleType.MESSAGE == "message"

    def test_transaction(self):
        assert BundleType.TRANSACTION == "transaction"

    def test_searchset(self):
        assert BundleType.SEARCHSET == "searchset"

    def test_document(self):
        assert BundleType.DOCUMENT == "document"

    def test_batch(self):
        assert BundleType.BATCH == "batch"

    def test_member_count(self):
        assert len(BundleType) == 9


class TestHTTPVerb:
    def test_get(self):
        assert HTTPVerb.GET == "GET"

    def test_post(self):
        assert HTTPVerb.POST == "POST"

    def test_put(self):
        assert HTTPVerb.PUT == "PUT"

    def test_delete(self):
        assert HTTPVerb.DELETE == "DELETE"

    def test_member_count(self):
        assert len(HTTPVerb) == 6


class TestAdministrativeGender:
    def test_male(self):
        assert AdministrativeGender.MALE == "male"

    def test_female(self):
        assert AdministrativeGender.FEMALE == "female"

    def test_other(self):
        assert AdministrativeGender.OTHER == "other"

    def test_unknown(self):
        assert AdministrativeGender.UNKNOWN == "unknown"


class TestNameUse:
    def test_official(self):
        assert NameUse.OFFICIAL == "official"

    def test_usual(self):
        assert NameUse.USUAL == "usual"

    def test_maiden(self):
        assert NameUse.MAIDEN == "maiden"

    def test_member_count(self):
        assert len(NameUse) == 7


class TestAddressUse:
    def test_home(self):
        assert AddressUse.HOME == "home"

    def test_work(self):
        assert AddressUse.WORK == "work"

    def test_billing(self):
        assert AddressUse.BILLING == "billing"


class TestAddressType:
    def test_postal(self):
        assert AddressType.POSTAL == "postal"

    def test_physical(self):
        assert AddressType.PHYSICAL == "physical"

    def test_both(self):
        assert AddressType.BOTH == "both"


class TestIdentifierUse:
    def test_official(self):
        assert IdentifierUse.OFFICIAL == "official"

    def test_secondary(self):
        assert IdentifierUse.SECONDARY == "secondary"

    def test_member_count(self):
        assert len(IdentifierUse) == 5


class TestContactPointSystem:
    def test_phone(self):
        assert ContactPointSystem.PHONE == "phone"

    def test_email(self):
        assert ContactPointSystem.EMAIL == "email"

    def test_member_count(self):
        assert len(ContactPointSystem) == 7


class TestContactPointUse:
    def test_home(self):
        assert ContactPointUse.HOME == "home"

    def test_mobile(self):
        assert ContactPointUse.MOBILE == "mobile"


class TestClinicalStatus:
    def test_active(self):
        assert ClinicalStatus.ACTIVE == "active"

    def test_resolved(self):
        assert ClinicalStatus.RESOLVED == "resolved"

    def test_member_count(self):
        assert len(ClinicalStatus) == 6


class TestVerificationStatus:
    def test_confirmed(self):
        assert VerificationStatus.CONFIRMED == "confirmed"

    def test_entered_in_error(self):
        assert VerificationStatus.ENTERED_IN_ERROR == "entered-in-error"

    def test_member_count(self):
        assert len(VerificationStatus) == 6


class TestMedicationRequestStatus:
    def test_active(self):
        assert MedicationRequestStatus.ACTIVE == "active"

    def test_completed(self):
        assert MedicationRequestStatus.COMPLETED == "completed"

    def test_member_count(self):
        assert len(MedicationRequestStatus) == 8


class TestMedicationRequestIntent:
    def test_order(self):
        assert MedicationRequestIntent.ORDER == "order"

    def test_plan(self):
        assert MedicationRequestIntent.PLAN == "plan"

    def test_member_count(self):
        assert len(MedicationRequestIntent) == 8


class TestNHSSystem:
    def test_nhs_number(self):
        assert NHSSystem.NHS_NUMBER == "https://fhir.nhs.uk/Id/nhs-number"

    def test_ods_organization_code(self):
        assert NHSSystem.ODS_ORGANIZATION_CODE == "https://fhir.nhs.uk/Id/ods-organization-code"

    def test_sds_user_id(self):
        assert NHSSystem.SDS_USER_ID == "https://fhir.nhs.uk/Id/sds-user-id"

    def test_spine_asid(self):
        assert NHSSystem.SPINE_ASID == "https://fhir.nhs.uk/Id/spine-asid"

    def test_member_count(self):
        assert len(NHSSystem) == 8

    def test_is_str_enum(self):
        assert isinstance(NHSSystem.NHS_NUMBER, str)


class TestUKCoreProfile:
    def test_patient(self):
        assert "UKCore-Patient" in UKCoreProfile.PATIENT

    def test_organization(self):
        assert "UKCore-Organization" in UKCoreProfile.ORGANIZATION

    def test_medication_request(self):
        assert "UKCore-MedicationRequest" in UKCoreProfile.MEDICATION_REQUEST

    def test_profile_url_prefix(self):
        for p in UKCoreProfile:
            assert p.value.startswith("https://fhir.hl7.org.uk/StructureDefinition/")

    def test_member_count(self):
        assert len(UKCoreProfile) == 8


class TestSnomedSystem:
    def test_snomed_ct(self):
        assert SnomedSystem.SNOMED_CT == "http://snomed.info/sct"

    def test_dmd(self):
        assert SnomedSystem.DMD == "https://dmd.nhs.uk"


class TestTerminologyConstants:
    def test_condition_clinical_status_system(self):
        assert "condition-clinical" in CONDITION_CLINICAL_STATUS_SYSTEM

    def test_condition_verification_status_system(self):
        assert "condition-ver-status" in CONDITION_VERIFICATION_STATUS_SYSTEM

    def test_allergy_clinical_status_system(self):
        assert "allergyintolerance-clinical" in ALLERGY_CLINICAL_STATUS_SYSTEM

    def test_allergy_verification_status_system(self):
        assert "allergyintolerance-verification" in ALLERGY_VERIFICATION_STATUS_SYSTEM
