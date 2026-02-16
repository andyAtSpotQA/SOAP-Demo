"""
Pre-built message templates for common NHS Spine interactions.

# HL7_SPEC: Each template sets up the correct interaction ID, trigger event,
# and structural defaults for a specific message type. The caller fills in
# variable parameters (patient identifiers, system IDs, etc.) and calls
# .build() to produce the final message.

Usage:
    builder = patient_demographics_query(
        sender_asid="SENDER-001",
        receiver_asid="RECEIVER-002",
    )
    builder.set_query_params(nhs_number="9999999999")
    msg = builder.build()
"""

from .builder import HL7v3MessageBuilder
from .types import InteractionType, ProcessingCode


def patient_demographics_query(
    sender_asid: str,
    receiver_asid: str,
    author_user_id: str = "555254240100",
    author_role_profile_id: str = "555254242101",
    processing_code: ProcessingCode = ProcessingCode.DEBUGGING,
) -> HL7v3MessageBuilder:
    """Template for PRPA_IN201305UV02 — Patient Demographics Query.

    # HL7_SPEC: PDQ is used to search for patients by demographics
    # (NHS number, name, DoB, postcode, gender). The query is sent to
    # PDS (Personal Demographics Service) on Spine.

    Returns a builder — call .set_query_params(...).build() to complete.

    Args:
        sender_asid: ASID of the sending system.
        receiver_asid: ASID of the PDS service on Spine.
        author_user_id: SDS User ID (default is a test value).
        author_role_profile_id: SDS Role Profile ID (default is a test value).
        processing_code: Defaults to DEBUGGING for test use.
    """
    return (
        HL7v3MessageBuilder()
        .set_interaction(InteractionType.PRPA_IN201305UV02)
        .set_sender(asid=sender_asid)
        .set_receiver(asid=receiver_asid)
        .set_author(
            user_id=author_user_id,
            role_profile_id=author_role_profile_id,
        )
        .set_processing_code(processing_code)
    )


def scr_query(
    sender_asid: str,
    receiver_asid: str,
    author_user_id: str = "555254240100",
    author_role_profile_id: str = "555254242101",
    nhs_number: str | None = None,
    processing_code: ProcessingCode = ProcessingCode.DEBUGGING,
) -> HL7v3MessageBuilder:
    """Template for QUPC_IN160101UK05 — Summary Care Record query.

    # HL7_SPEC: SCR query retrieves a patient's Summary Care Record
    # from the Spine SCR repository. Requires an NHS number.

    Returns a builder. If nhs_number is provided, query params are pre-set.

    Args:
        sender_asid: ASID of the sending system.
        receiver_asid: ASID of the SCR service on Spine.
        nhs_number: Patient's NHS number (optional here, can set later).
        processing_code: Defaults to DEBUGGING for test use.
    """
    builder = (
        HL7v3MessageBuilder()
        .set_interaction(InteractionType.QUPC_IN160101UK05)
        .set_sender(asid=sender_asid)
        .set_receiver(asid=receiver_asid)
        .set_author(
            user_id=author_user_id,
            role_profile_id=author_role_profile_id,
        )
        .set_processing_code(processing_code)
    )
    if nhs_number:
        builder.set_query_params(nhs_number=nhs_number)
    return builder


def gp_summary_upload(
    sender_asid: str,
    receiver_asid: str,
    author_user_id: str = "555254240100",
    author_role_profile_id: str = "555254242101",
    job_role_code: str | None = None,
    processing_code: ProcessingCode = ProcessingCode.DEBUGGING,
) -> HL7v3MessageBuilder:
    """Template for REPC_IN150016UK05 — GP Summary upload.

    # HL7_SPEC: Used to upload a GP Summary clinical document to the
    # Spine repository. The caller must provide the CDA document
    # as payload via set_payload().

    Returns a builder — call .set_payload(cda_element).build() to complete.

    Args:
        sender_asid: ASID of the GP system.
        receiver_asid: ASID of the Spine repository service.
        job_role_code: Optional SDS Job Role Code (e.g. "R0260" for GP).
        processing_code: Defaults to DEBUGGING for test use.
    """
    return (
        HL7v3MessageBuilder()
        .set_interaction(InteractionType.REPC_IN150016UK05)
        .set_sender(asid=sender_asid)
        .set_receiver(asid=receiver_asid)
        .set_author(
            user_id=author_user_id,
            role_profile_id=author_role_profile_id,
            job_role_code=job_role_code,
        )
        .set_processing_code(processing_code)
    )
