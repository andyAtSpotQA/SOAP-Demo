"""
Core HL7 v3 message builder with fluent API.

# HL7_SPEC: HL7 v3 messages have a three-layer structure:
#   1. Transmission Wrapper — message metadata (ID, time, interaction, sender/receiver)
#   2. Control Act Wrapper — trigger event, author, query parameters
#   3. Payload — the actual clinical/administrative content
#
# This builder constructs all three layers and assembles them into a
# valid HL7 v3 XML document. Element ordering follows the HL7 v3 schema.

Usage:
    msg = (
        HL7v3MessageBuilder()
        .set_interaction(InteractionType.PRPA_IN201305UV02)
        .set_sender(asid="SENDER-001")
        .set_receiver(asid="RECEIVER-002")
        .set_author(user_id="555254240100", role_profile_id="555254242101")
        .set_query_params(nhs_number="9999999999")
        .build()
    )
    xml_string = msg.to_xml()
"""

from __future__ import annotations

import uuid
from datetime import datetime
from lxml import etree

from .types import (
    InteractionType,
    ProcessingCode,
    ProcessingModeCode,
    AckCode,
    NHSOid,
)
from .exceptions import ValidationError, SerializationError
from .datatypes import HL7_NS, HL7_NSMAP, ii, cd, ts
from . import elements


class HL7v3MessageBuilder:
    """Fluent builder for HL7 v3 messages targeting NHS Spine APIs.

    # HL7_SPEC: Constructs the complete three-layer HL7 v3 message structure.
    # Methods can be called in any order; build() validates and assembles.
    # Defaults are set for test automation: ProcessingCode.DEBUGGING,
    # AckCode.NEVER, auto-generated message ID and timestamp.
    """

    def __init__(self):
        self._message_id: str | None = None
        self._creation_time: datetime | None = None
        self._interaction: InteractionType | str | None = None
        self._processing_code: ProcessingCode = ProcessingCode.DEBUGGING
        self._processing_mode: ProcessingModeCode = ProcessingModeCode.CURRENT
        self._accept_ack: AckCode = AckCode.NEVER
        self._sender_asid: str | None = None
        self._receiver_asid: str | None = None
        self._author_user_id: str | None = None
        self._author_role_profile_id: str | None = None
        self._author_job_role_code: str | None = None
        self._trigger_event_code: str | None = None
        self._trigger_event_code_system: str | None = None
        self._payload: etree._Element | None = None
        self._query_params: dict | None = None
        self._raw_control_act_content: list[etree._Element] = []

    # --- Transmission Wrapper methods ---

    def set_message_id(self, message_id: str) -> HL7v3MessageBuilder:
        """Set a specific message ID. Auto-generated UUID if not set.

        # HL7_SPEC: <id root="2.16.840.1.113883.2.1.3.2.4.17" extension="..."/>
        # Globally unique message identifier.
        """
        self._message_id = message_id
        return self

    def set_creation_time(self, dt: datetime) -> HL7v3MessageBuilder:
        """Set the message creation time. Defaults to now() if not set.

        # HL7_SPEC: <creationTime value="YYYYMMDDHHmmss"/>
        """
        self._creation_time = dt
        return self

    def set_interaction(self, interaction: InteractionType | str) -> HL7v3MessageBuilder:
        """Set the HL7 v3 interaction type (required).

        # HL7_SPEC: Determines the root element name and the
        # <interactionId> element value. Each interaction ID maps to
        # a specific message pattern in the NHS MIM.
        """
        self._interaction = interaction
        return self

    def set_processing_code(self, code: ProcessingCode) -> HL7v3MessageBuilder:
        """Set the processing code. Defaults to DEBUGGING for test use.

        # HL7_SPEC: <processingCode code="D"/>
        # P=Production, T=Training, D=Debugging.
        """
        self._processing_code = code
        return self

    def set_processing_mode(self, mode: ProcessingModeCode) -> HL7v3MessageBuilder:
        """Set the processing mode code. Defaults to CURRENT.

        # HL7_SPEC: <processingModeCode code="T"/>
        # T=current processing, I=initial load, R=restore.
        """
        self._processing_mode = mode
        return self

    def set_accept_ack(self, ack: AckCode) -> HL7v3MessageBuilder:
        """Set the accept acknowledgement code. Defaults to NEVER.

        # HL7_SPEC: <acceptAckCode code="NE"/>
        # NE=never, AL=always, ER=error only.
        """
        self._accept_ack = ack
        return self

    def set_sender(self, asid: str) -> HL7v3MessageBuilder:
        """Set the sender's Accredited System ID (required).

        # HL7_SPEC: Populates <communicationFunctionSnd> with the ASID
        # of the sending system registered on Spine.
        """
        self._sender_asid = asid
        return self

    def set_receiver(self, asid: str) -> HL7v3MessageBuilder:
        """Set the receiver's Accredited System ID (required).

        # HL7_SPEC: Populates <communicationFunctionRcv> with the ASID
        # of the target system on Spine.
        """
        self._receiver_asid = asid
        return self

    # --- Control Act Wrapper methods ---

    def set_author(
        self,
        user_id: str,
        role_profile_id: str,
        job_role_code: str | None = None,
    ) -> HL7v3MessageBuilder:
        """Set the author of the control act.

        # HL7_SPEC: The author is the person/system making the request.
        # NHS Spine requires an SDS User ID and SDS Role Profile ID.
        # Optionally an SDS Job Role Code for RBAC.
        """
        self._author_user_id = user_id
        self._author_role_profile_id = role_profile_id
        self._author_job_role_code = job_role_code
        return self

    def set_trigger_event(
        self,
        code: str,
        code_system: str | None = None,
    ) -> HL7v3MessageBuilder:
        """Set the control act trigger event code.

        # HL7_SPEC: <code code="PRPA_TE201305UV02" codeSystem="..."/>
        # on the ControlActEvent element. If not set, the builder leaves
        # the code element out (some interactions don't require it).
        """
        self._trigger_event_code = code
        self._trigger_event_code_system = code_system
        return self

    def set_query_params(
        self,
        nhs_number: str | None = None,
        family_name: str | None = None,
        given_name: str | None = None,
        date_of_birth: str | None = None,
        postcode: str | None = None,
        gender: str | None = None,
    ) -> HL7v3MessageBuilder:
        """Set query-by-parameter values (for query interactions like PDQ).

        # HL7_SPEC: <queryByParameter> contains the search criteria.
        # Used by PRPA_IN201305UV02 and similar query interactions.
        """
        self._query_params = {
            k: v for k, v in {
                "nhs_number": nhs_number,
                "family_name": family_name,
                "given_name": given_name,
                "date_of_birth": date_of_birth,
                "postcode": postcode,
                "gender": gender,
            }.items() if v is not None
        }
        return self

    def add_control_act_content(self, element: etree._Element) -> HL7v3MessageBuilder:
        """Add arbitrary content inside the control act wrapper.

        # HL7_SPEC: Escape hatch for interaction-specific elements that
        # don't fit the standard query/payload pattern.
        """
        self._raw_control_act_content.append(element)
        return self

    # --- Payload ---

    def set_payload(self, payload: etree._Element) -> HL7v3MessageBuilder:
        """Set the clinical/admin payload element.

        # HL7_SPEC: The payload (e.g. clinical document, patient record)
        # goes inside the control act wrapper's <subject> element.
        """
        self._payload = payload
        return self

    # --- Build ---

    def validate(self) -> list[str]:
        """Check for required fields. Returns error messages (empty = valid).

        # HL7_SPEC: Structural validation only — checks that mandatory
        # builder fields are set, not full HL7 v3 schema validation.
        """
        errors = []
        if self._interaction is None:
            errors.append("interaction type is required (call set_interaction())")
        if self._sender_asid is None:
            errors.append("sender ASID is required (call set_sender())")
        if self._receiver_asid is None:
            errors.append("receiver ASID is required (call set_receiver())")
        return errors

    def build(self) -> HL7v3Message:
        """Assemble and validate the complete HL7 v3 message.

        # HL7_SPEC: Builds the three-layer structure:
        #   Layer 1: Transmission wrapper (root element + metadata)
        #   Layer 2: ControlActEvent (author, trigger, content)
        #   Layer 3: Payload (subject or queryByParameter)
        # Elements are appended in the order mandated by the HL7 v3 schema.

        Raises:
            ValidationError: If required fields are missing.

        Returns:
            HL7v3Message: The assembled message, ready for serialization.
        """
        errors = self.validate()
        if errors:
            raise ValidationError(
                f"Message validation failed: {'; '.join(errors)}",
                field=errors[0].split()[0],
            )

        message_id = self._message_id or str(uuid.uuid4()).upper()
        creation_time = self._creation_time or datetime.utcnow()
        interaction_str = (
            self._interaction.value
            if isinstance(self._interaction, InteractionType)
            else self._interaction
        )

        # --- Layer 1: Transmission Wrapper (root element) ---
        root = etree.Element(
            f"{{{HL7_NS}}}{interaction_str}",
            ITSVersion="XML_1.0",
            nsmap={None: HL7_NS},
        )

        # Message ID
        root.append(ii(
            root=NHSOid.SPINE_MESSAGE_ID.value,
            extension=message_id,
        ))

        # Creation time
        root.append(ts(creation_time))

        # Version code
        root.append(cd("V3NPfIT4.2.00", tag="versionCode"))

        # Interaction ID
        root.append(ii(
            root=NHSOid.SPINE_INTERACTION.value,
            extension=interaction_str,
            tag="interactionId",
        ))

        # Processing code
        root.append(cd(
            self._processing_code.value,
            code_system=NHSOid.PROCESSING_ID.value,
            tag="processingCode",
        ))

        # Processing mode code
        root.append(cd(
            self._processing_mode.value,
            code_system=NHSOid.PROCESSING_MODE.value,
            tag="processingModeCode",
        ))

        # Accept ack code
        root.append(cd(
            self._accept_ack.value,
            code_system=NHSOid.ACK_CONDITION.value,
            tag="acceptAckCode",
        ))

        # Sender
        root.append(elements.communication_function_snd(
            device_id=message_id,
            asid=self._sender_asid,
        ))

        # Receiver
        root.append(elements.communication_function_rcv(
            device_id=message_id,
            asid=self._receiver_asid,
        ))

        # --- Layer 2: Control Act Wrapper ---
        control_act = etree.SubElement(
            root,
            f"{{{HL7_NS}}}ControlActEvent",
            classCode="CACT",
            moodCode="EVN",
        )

        # Trigger event code
        if self._trigger_event_code:
            control_act.append(elements.trigger_event(
                self._trigger_event_code,
                self._trigger_event_code_system,
            ))

        # Author
        if self._author_user_id:
            control_act.append(elements.author(
                user_id=self._author_user_id,
                role_profile_id=self._author_role_profile_id,
                sds_job_role_code=self._author_job_role_code,
            ))

        # Extra content
        for extra in self._raw_control_act_content:
            control_act.append(extra)

        # --- Layer 3: Payload ---
        if self._payload is not None:
            subject = etree.SubElement(control_act, f"{{{HL7_NS}}}subject")
            subject.append(self._payload)

        # Query parameters
        if self._query_params:
            control_act.append(elements.query_by_parameter(**self._query_params))

        return HL7v3Message(root, message_id, interaction_str)


class HL7v3Message:
    """An assembled HL7 v3 message ready for serialization or SOAP wrapping.

    # HL7_SPEC: Immutable wrapper around the built lxml Element tree.
    # Provides serialization to XML string and access to the raw Element.
    """

    def __init__(self, root: etree._Element, message_id: str, interaction: str):
        self._root = root
        self._message_id = message_id
        self._interaction = interaction

    @property
    def root(self) -> etree._Element:
        """The root lxml Element of the HL7 v3 message."""
        return self._root

    @property
    def message_id(self) -> str:
        """The unique message identifier."""
        return self._message_id

    @property
    def interaction(self) -> str:
        """The interaction type string (e.g. 'PRPA_IN201305UV02')."""
        return self._interaction

    def to_xml(
        self,
        pretty_print: bool = True,
        xml_declaration: bool = True,
    ) -> str:
        """Serialize to an XML string.

        # HL7_SPEC: Returns UTF-8 encoded XML with optional declaration.
        """
        try:
            return etree.tostring(
                self._root,
                pretty_print=pretty_print,
                xml_declaration=xml_declaration,
                encoding="UTF-8",
            ).decode("utf-8")
        except Exception as e:
            raise SerializationError(f"Failed to serialize HL7 v3 message: {e}")

    def to_element(self) -> etree._Element:
        """Return the raw lxml Element for further manipulation or SOAP wrapping."""
        return self._root
