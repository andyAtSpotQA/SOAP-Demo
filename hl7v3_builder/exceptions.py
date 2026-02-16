"""
Exception hierarchy for the HL7 v3 message builder.

# HL7_SPEC: These are builder-side exceptions, not HL7 acknowledgement errors.
# They indicate problems constructing or validating a message before it is sent.
"""


class HL7BuilderError(Exception):
    """Base exception for all HL7 v3 builder errors.

    # HL7_SPEC: Analogous to PKCS11Error in the safesign_mock package.
    """


class ValidationError(HL7BuilderError):
    """Message failed structural validation before serialization.

    # HL7_SPEC: The built message is missing required elements or has
    # invalid attribute combinations per the HL7 v3 RIM rules.
    """

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)


class TemplateError(HL7BuilderError):
    """Error loading or applying a message template.

    # HL7_SPEC: A pre-built template for an interaction type could not
    # be found or the provided overrides are incompatible.
    """


class SerializationError(HL7BuilderError):
    """Error serializing the message to XML.

    # HL7_SPEC: lxml raised an error during Element tree serialization.
    """


class SoapWrappingError(HL7BuilderError):
    """Error wrapping the HL7 payload in a SOAP envelope.

    # HL7_SPEC: The SOAP envelope or WS-Addressing headers could not
    # be constructed, typically due to missing addressing parameters.
    """
