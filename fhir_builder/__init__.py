"""
FHIR R4 resource builder for NHS API test automation.

Provides a fluent API for constructing FHIR R4 XML Bundles containing
UK Core-profiled resources, ready for signing and transmission to
NHS services (PDS FHIR, GP Connect, EPS).

Usage:
    from fhir_builder import FHIRBundleBuilder, BundleType
    from fhir_builder.templates import patient_search_bundle
    from fhir_builder.resources import patient, organization

    # Using a template
    bundle = (
        patient_search_bundle("9999999999", "Smith", "John", "1980-01-15", "male")
        .build()
    )

    # Using the builder directly
    bundle = (
        FHIRBundleBuilder()
        .set_type(BundleType.SEARCHSET)
        .set_timestamp()
        .add_entry(patient(...))
        .build()
    )
    print(bundle.to_xml())
"""

from .builder import FHIRBundleBuilder, FHIRBundle
from .types import (
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
)
from .exceptions import (
    FHIRBuilderError,
    ValidationError,
    TemplateError,
    SerializationError,
)
from .datatypes import (
    identifier,
    human_name,
    address,
    coding,
    codeable_concept,
    codeable_concept_from_codings,
    reference,
    period,
    contact_point,
    meta,
)

__all__ = [
    # Builder
    "FHIRBundleBuilder",
    "FHIRBundle",
    # Types
    "ResourceType",
    "BundleType",
    "HTTPVerb",
    "AdministrativeGender",
    "NameUse",
    "AddressUse",
    "AddressType",
    "IdentifierUse",
    "ContactPointSystem",
    "ContactPointUse",
    "ClinicalStatus",
    "VerificationStatus",
    "MedicationRequestStatus",
    "MedicationRequestIntent",
    "NHSSystem",
    "UKCoreProfile",
    "SnomedSystem",
    # Exceptions
    "FHIRBuilderError",
    "ValidationError",
    "TemplateError",
    "SerializationError",
    # Data types
    "identifier",
    "human_name",
    "address",
    "coding",
    "codeable_concept",
    "codeable_concept_from_codings",
    "reference",
    "period",
    "contact_point",
    "meta",
]
