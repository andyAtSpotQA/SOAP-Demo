"""
HL7 v3 message builder for NHS Spine API test automation.

Provides a fluent API for constructing HL7 v3 XML payloads, wrapping them
in SOAP 1.1 envelopes with WS-Addressing headers, and serializing for
signing and transmission.

Usage:
    from hl7v3_builder import HL7v3MessageBuilder, InteractionType
    from hl7v3_builder.templates import patient_demographics_query
    from hl7v3_builder.soap_wrapper import wrap_in_soap

    # Using a template
    msg = (
        patient_demographics_query("SENDER-001", "RECEIVER-002")
        .set_query_params(nhs_number="9999999999")
        .build()
    )

    # Using the builder directly
    msg = (
        HL7v3MessageBuilder()
        .set_interaction(InteractionType.PRPA_IN201305UV02)
        .set_sender(asid="SENDER-001")
        .set_receiver(asid="RECEIVER-002")
        .set_author(user_id="555254240100", role_profile_id="555254242101")
        .set_query_params(nhs_number="9999999999")
        .build()
    )

    # Wrap in SOAP for Spine delivery
    soap_xml = wrap_in_soap(msg, to_url="https://spine.nhs.uk/Spine")
"""

from .builder import HL7v3MessageBuilder, HL7v3Message
from .types import (
    InteractionType,
    ProcessingCode,
    ProcessingModeCode,
    AckCode,
    ClassCode,
    MoodCode,
    NHSOid,
)
from .exceptions import (
    HL7BuilderError,
    ValidationError,
    TemplateError,
    SerializationError,
    SoapWrappingError,
)
from .datatypes import ii, cd, ts, st, pq, ivl_ts, ed, tel, ad, pn
from .soap_wrapper import wrap_in_soap, extract_from_soap

__all__ = [
    # Builder
    "HL7v3MessageBuilder",
    "HL7v3Message",
    # Types
    "InteractionType",
    "ProcessingCode",
    "ProcessingModeCode",
    "AckCode",
    "ClassCode",
    "MoodCode",
    "NHSOid",
    # Exceptions
    "HL7BuilderError",
    "ValidationError",
    "TemplateError",
    "SerializationError",
    "SoapWrappingError",
    # Data types
    "ii", "cd", "ts", "st", "pq", "ivl_ts", "ed", "tel", "ad", "pn",
    # SOAP
    "wrap_in_soap",
    "extract_from_soap",
]
