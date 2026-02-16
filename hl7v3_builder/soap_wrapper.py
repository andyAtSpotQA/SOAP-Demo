"""
SOAP 1.1 envelope and WS-Addressing header wrapping for HL7 v3 messages.

# HL7_SPEC: NHS Spine requires all HL7 v3 messages to be wrapped in a
# SOAP 1.1 envelope with WS-Addressing (WSA) headers. The SOAP body
# contains the HL7 v3 message, while WSA headers carry routing info:
#   <soap:Envelope>
#     <soap:Header>
#       <wsa:MessageID>uuid:...</wsa:MessageID>
#       <wsa:Action>urn:nhs:names:services:INTERACTION_ID</wsa:Action>
#       <wsa:To>https://spine-endpoint/...</wsa:To>
#       <wsa:From><wsa:Address>...</wsa:Address></wsa:From>
#     </soap:Header>
#     <soap:Body>
#       <!-- HL7 v3 message -->
#     </soap:Body>
#   </soap:Envelope>
"""

import uuid
from lxml import etree
from .builder import HL7v3Message
from .exceptions import SoapWrappingError


SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
WSA_NS = "http://www.w3.org/2005/08/addressing"
HL7_NS = "urn:hl7-org:v3"

NSMAP = {
    "soap": SOAP_NS,
    "wsa": WSA_NS,
    "hl7": HL7_NS,
}


def wrap_in_soap(
    message: HL7v3Message,
    to_url: str,
    from_url: str | None = None,
    wsa_action: str | None = None,
    wsa_message_id: str | None = None,
) -> str:
    """Wrap an HL7v3Message in a SOAP 1.1 envelope with WS-Addressing headers.

    # HL7_SPEC: The SOAP envelope is the transport wrapper for NHS Spine
    # messages. The WS-A Action header identifies the interaction type,
    # and the To header specifies the target Spine service endpoint.

    Args:
        message: The built HL7v3Message to wrap.
        to_url: Target endpoint URL (wsa:To).
        from_url: Sender's URL (wsa:From). Optional.
        wsa_action: Override WS-A action. Defaults to
                    "urn:nhs:names:services:{interaction_id}".
        wsa_message_id: Override WS-A message ID. Defaults to new UUID.

    Returns:
        XML string of the complete SOAP envelope.

    Raises:
        SoapWrappingError: If required parameters are missing.
    """
    if not to_url:
        raise SoapWrappingError("'to_url' is required for SOAP wrapping")

    action = wsa_action or f"urn:nhs:names:services:{message.interaction}"
    msg_id = wsa_message_id or f"uuid:{uuid.uuid4()}"

    # Build envelope
    envelope = etree.Element(f"{{{SOAP_NS}}}Envelope", nsmap=NSMAP)

    # Header with WS-Addressing
    header = etree.SubElement(envelope, f"{{{SOAP_NS}}}Header")
    etree.SubElement(header, f"{{{WSA_NS}}}MessageID").text = msg_id
    etree.SubElement(header, f"{{{WSA_NS}}}Action").text = action
    etree.SubElement(header, f"{{{WSA_NS}}}To").text = to_url

    if from_url:
        from_el = etree.SubElement(header, f"{{{WSA_NS}}}From")
        etree.SubElement(from_el, f"{{{WSA_NS}}}Address").text = from_url

    # Body with HL7 v3 message
    body = etree.SubElement(envelope, f"{{{SOAP_NS}}}Body")
    body.append(message.to_element())

    return etree.tostring(
        envelope,
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    ).decode("utf-8")


def extract_from_soap(soap_xml: str | bytes) -> etree._Element:
    """Extract the HL7 v3 payload from a SOAP envelope.

    # HL7_SPEC: Useful for parsing Spine responses. Extracts the first
    # child element of soap:Body, which is the HL7 v3 response message.

    Args:
        soap_xml: The SOAP envelope XML string or bytes.

    Returns:
        The first child element of the SOAP body.

    Raises:
        SoapWrappingError: If the SOAP structure is invalid or empty.
    """
    if isinstance(soap_xml, str):
        soap_xml = soap_xml.encode("utf-8")

    try:
        root = etree.fromstring(soap_xml)
    except etree.XMLSyntaxError as e:
        raise SoapWrappingError(f"Invalid XML: {e}")

    body = root.find(f"{{{SOAP_NS}}}Body")
    if body is None:
        raise SoapWrappingError("No soap:Body element found in envelope")

    if len(body) == 0:
        raise SoapWrappingError("soap:Body is empty — no payload found")

    return body[0]
