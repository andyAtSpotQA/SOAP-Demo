"""
Exception hierarchy for the FHIR R4 resource builder.

Mirrors the HL7 v3 builder exception pattern. No SoapWrappingError
since FHIR uses REST, not SOAP.
"""


class FHIRBuilderError(Exception):
    """Base exception for all FHIR builder errors."""


class ValidationError(FHIRBuilderError):
    """Raised when a required field is missing or invalid.

    # FHIR_SPEC: FHIR resources have required elements; omitting them
    # produces an invalid resource that Spine/GP Connect will reject.
    """

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        detail = f" (field: {field})" if field else ""
        super().__init__(f"{message}{detail}")


class TemplateError(FHIRBuilderError):
    """Raised when a template cannot be configured correctly."""


class SerializationError(FHIRBuilderError):
    """Raised when XML serialization fails."""
