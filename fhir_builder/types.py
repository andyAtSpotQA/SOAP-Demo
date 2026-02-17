"""
FHIR R4 enumerations and constant system URIs for NHS/UK Core resources.

# FHIR_SPEC: All enum values match the FHIR R4 value sets exactly.
# NHS-specific system URIs follow https://fhir.nhs.uk/Id/ conventions.
# UK Core profile URLs follow https://fhir.hl7.org.uk/StructureDefinition/ conventions.
"""

from enum import Enum


class ResourceType(str, Enum):
    """FHIR R4 resource type codes.

    # FHIR_SPEC: Used in Bundle.entry.resource and meta.profile to identify
    # the resource type. Each value is the exact resourceType string.
    """
    PATIENT = "Patient"
    ORGANIZATION = "Organization"
    PRACTITIONER = "Practitioner"
    MEDICATION_REQUEST = "MedicationRequest"
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    CONDITION = "Condition"
    MESSAGE_HEADER = "MessageHeader"
    BUNDLE = "Bundle"


class BundleType(str, Enum):
    """FHIR R4 Bundle.type value set.

    # FHIR_SPEC: Indicates the purpose of a Bundle. Message bundles carry
    # inter-system messages; transaction bundles are atomic REST operations;
    # searchset bundles wrap search results.
    """
    DOCUMENT = "document"
    MESSAGE = "message"
    TRANSACTION = "transaction"
    TRANSACTION_RESPONSE = "transaction-response"
    BATCH = "batch"
    BATCH_RESPONSE = "batch-response"
    HISTORY = "history"
    SEARCHSET = "searchset"
    COLLECTION = "collection"


class HTTPVerb(str, Enum):
    """HTTP verbs for Bundle.entry.request in transaction/batch bundles.

    # FHIR_SPEC: Transaction bundle entries must specify the HTTP method
    # that the server should execute for each entry.
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"


class AdministrativeGender(str, Enum):
    """FHIR R4 administrative gender value set.

    # FHIR_SPEC: http://hl7.org/fhir/administrative-gender
    """
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class NameUse(str, Enum):
    """FHIR R4 HumanName.use value set.

    # FHIR_SPEC: http://hl7.org/fhir/name-use
    """
    USUAL = "usual"
    OFFICIAL = "official"
    TEMP = "temp"
    NICKNAME = "nickname"
    ANONYMOUS = "anonymous"
    OLD = "old"
    MAIDEN = "maiden"


class AddressUse(str, Enum):
    """FHIR R4 Address.use value set.

    # FHIR_SPEC: http://hl7.org/fhir/address-use
    """
    HOME = "home"
    WORK = "work"
    TEMP = "temp"
    OLD = "old"
    BILLING = "billing"


class AddressType(str, Enum):
    """FHIR R4 Address.type value set.

    # FHIR_SPEC: http://hl7.org/fhir/address-type
    """
    POSTAL = "postal"
    PHYSICAL = "physical"
    BOTH = "both"


class IdentifierUse(str, Enum):
    """FHIR R4 Identifier.use value set.

    # FHIR_SPEC: http://hl7.org/fhir/identifier-use
    """
    USUAL = "usual"
    OFFICIAL = "official"
    TEMP = "temp"
    SECONDARY = "secondary"
    OLD = "old"


class ContactPointSystem(str, Enum):
    """FHIR R4 ContactPoint.system value set.

    # FHIR_SPEC: http://hl7.org/fhir/contact-point-system
    """
    PHONE = "phone"
    FAX = "fax"
    EMAIL = "email"
    PAGER = "pager"
    URL = "url"
    SMS = "sms"
    OTHER = "other"


class ContactPointUse(str, Enum):
    """FHIR R4 ContactPoint.use value set.

    # FHIR_SPEC: http://hl7.org/fhir/contact-point-use
    """
    HOME = "home"
    WORK = "work"
    TEMP = "temp"
    OLD = "old"
    MOBILE = "mobile"


class ClinicalStatus(str, Enum):
    """FHIR R4 condition/allergy clinical status codes.

    # FHIR_SPEC: http://terminology.hl7.org/CodeSystem/condition-clinical
    # and http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical
    """
    ACTIVE = "active"
    RECURRENCE = "recurrence"
    RELAPSE = "relapse"
    INACTIVE = "inactive"
    REMISSION = "remission"
    RESOLVED = "resolved"


class VerificationStatus(str, Enum):
    """FHIR R4 condition/allergy verification status codes.

    # FHIR_SPEC: http://terminology.hl7.org/CodeSystem/condition-ver-status
    # and http://terminology.hl7.org/CodeSystem/allergyintolerance-verification
    """
    UNCONFIRMED = "unconfirmed"
    PROVISIONAL = "provisional"
    DIFFERENTIAL = "differential"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    ENTERED_IN_ERROR = "entered-in-error"


class MedicationRequestStatus(str, Enum):
    """FHIR R4 MedicationRequest.status value set.

    # FHIR_SPEC: http://hl7.org/fhir/CodeSystem/medicationrequest-status
    """
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    STOPPED = "stopped"
    DRAFT = "draft"
    UNKNOWN = "unknown"


class MedicationRequestIntent(str, Enum):
    """FHIR R4 MedicationRequest.intent value set.

    # FHIR_SPEC: http://hl7.org/fhir/CodeSystem/medicationrequest-intent
    """
    PROPOSAL = "proposal"
    PLAN = "plan"
    ORDER = "order"
    ORIGINAL_ORDER = "original-order"
    REFLEX_ORDER = "reflex-order"
    FILLER_ORDER = "filler-order"
    INSTANCE_ORDER = "instance-order"
    OPTION = "option"


class NHSSystem(str, Enum):
    """NHS identifier system URIs used in FHIR Identifier.system.

    # FHIR_SPEC: These are the canonical system URIs for NHS identifiers
    # as defined at https://fhir.nhs.uk/Id/
    """
    NHS_NUMBER = "https://fhir.nhs.uk/Id/nhs-number"
    ODS_ORGANIZATION_CODE = "https://fhir.nhs.uk/Id/ods-organization-code"
    ODS_SITE_CODE = "https://fhir.nhs.uk/Id/ods-site-code"
    SDS_USER_ID = "https://fhir.nhs.uk/Id/sds-user-id"
    SDS_ROLE_PROFILE_ID = "https://fhir.nhs.uk/Id/sds-role-profile-id"
    SPINE_ASID = "https://fhir.nhs.uk/Id/spine-asid"
    PRESCRIPTION_ORDER_ID = "https://fhir.nhs.uk/Id/prescription-order-number"
    CROSS_CARE_SETTING_ID = "https://fhir.nhs.uk/Id/cross-care-setting-identifier"


class UKCoreProfile(str, Enum):
    """UK Core FHIR profile URLs for meta.profile.

    # FHIR_SPEC: UK Core profiles extend base FHIR R4 resources with
    # NHS-specific constraints and extensions. Declared in resource.meta.profile.
    """
    PATIENT = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Patient"
    ORGANIZATION = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
    PRACTITIONER = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Practitioner"
    MEDICATION_REQUEST = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-MedicationRequest"
    ALLERGY_INTOLERANCE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-AllergyIntolerance"
    CONDITION = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Condition"
    MESSAGE_HEADER = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-MessageHeader"
    BUNDLE = "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Bundle"


class SnomedSystem(str, Enum):
    """Code system URIs for SNOMED CT and dm+d.

    # FHIR_SPEC: SNOMED CT is the primary clinical terminology used
    # in UK FHIR resources. dm+d is the NHS dictionary of medicines.
    """
    SNOMED_CT = "http://snomed.info/sct"
    DMD = "https://dmd.nhs.uk"


# Terminology system URIs (not enums, just constants)
# FHIR_SPEC: These are CodeSystem URIs used in CodeableConcept.coding.system
CONDITION_CLINICAL_STATUS_SYSTEM = (
    "http://terminology.hl7.org/CodeSystem/condition-clinical"
)
CONDITION_VERIFICATION_STATUS_SYSTEM = (
    "http://terminology.hl7.org/CodeSystem/condition-ver-status"
)
ALLERGY_CLINICAL_STATUS_SYSTEM = (
    "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical"
)
ALLERGY_VERIFICATION_STATUS_SYSTEM = (
    "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification"
)
