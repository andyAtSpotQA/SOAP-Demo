"""
HL7 v3 data type element factories.

# HL7_SPEC: HL7 v3 defines abstract data types (ISO 21090) that map to
# specific XML structures. Each function here creates one data type element.
# See HL7 v3 Data Types Abstract Specification Release 2.

All functions return lxml.etree.Element instances in the HL7 v3 namespace.
The `tag` parameter controls the XML element name (e.g. "id", "code",
"creationTime") so the same data type factory can be reused across contexts.
"""

from datetime import datetime
from lxml import etree


# HL7 v3 primary namespace
HL7_NS = "urn:hl7-org:v3"
HL7_NSMAP = {None: HL7_NS}


def _hl7_element(tag: str, nsmap: dict | None = None, **attribs) -> etree._Element:
    """Create an element in the HL7 v3 namespace.

    Internal helper — all public functions delegate here.
    """
    clean = {k: v for k, v in attribs.items() if v is not None}
    return etree.Element(f"{{{HL7_NS}}}{tag}", nsmap=nsmap, **clean)


def ii(
    root: str,
    extension: str | None = None,
    *,
    tag: str = "id",
    assigning_authority_name: str | None = None,
) -> etree._Element:
    """Create an HL7 v3 Instance Identifier (II) element.

    # HL7_SPEC: II data type — root is an OID identifying the assigning
    # authority, extension is the identifier value within that namespace.
    # Together they form a globally unique identifier.
    # See: HL7 v3 Data Types §4.4 Instance Identifier.

    Args:
        root: OID of the assigning authority.
        extension: Identifier value (optional for UUID-only roots).
        tag: XML element name. Defaults to "id".
        assigning_authority_name: Human-readable authority name.

    Returns:
        Element like: <id root="2.16.840..." extension="12345"/>
    """
    return _hl7_element(
        tag,
        root=root,
        extension=extension,
        assigningAuthorityName=assigning_authority_name,
    )


def cd(
    code: str,
    code_system: str | None = None,
    *,
    display_name: str | None = None,
    code_system_name: str | None = None,
    tag: str = "code",
) -> etree._Element:
    """Create an HL7 v3 Concept Descriptor (CD) element.

    # HL7_SPEC: CD data type — represents a coded concept with its
    # code system. Used for classification codes, vocabulary bindings.
    # See: HL7 v3 Data Types §4.1 Concept Descriptor.

    Args:
        code: The code value.
        code_system: OID identifying the coding system.
        display_name: Human-readable display name.
        code_system_name: Name of the coding system.
        tag: XML element name. Defaults to "code".
    """
    return _hl7_element(
        tag,
        code=code,
        codeSystem=code_system,
        displayName=display_name,
        codeSystemName=code_system_name,
    )


def ts(
    value: datetime | str | None = None,
    *,
    tag: str = "creationTime",
) -> etree._Element:
    """Create an HL7 v3 Timestamp (TS) element.

    # HL7_SPEC: TS data type — value in YYYYMMDDHHmmss format.
    # Variable precision is supported (YYYY, YYYYMM, YYYYMMDD, etc.).
    # If no value is given, uses the current UTC time.
    # See: HL7 v3 Data Types §4.3 Point in Time.

    Args:
        value: datetime object, HL7 timestamp string, or None for now.
        tag: XML element name. Defaults to "creationTime".
    """
    if value is None:
        value = datetime.utcnow()
    if isinstance(value, datetime):
        value = value.strftime("%Y%m%d%H%M%S")
    return _hl7_element(tag, value=value)


def st(value: str, *, tag: str = "value") -> etree._Element:
    """Create an HL7 v3 String (ST) element.

    # HL7_SPEC: ST data type — plain character string.
    # See: HL7 v3 Data Types §4.2 Character String.
    """
    el = _hl7_element(tag)
    el.text = value
    return el


def pq(
    value: float | str,
    unit: str,
    *,
    tag: str = "value",
) -> etree._Element:
    """Create an HL7 v3 Physical Quantity (PQ) element.

    # HL7_SPEC: PQ data type — a dimensioned quantity with UCUM unit.
    # See: HL7 v3 Data Types §4.5 Physical Quantity.
    """
    return _hl7_element(tag, value=str(value), unit=unit)


def ivl_ts(
    low: datetime | str | None = None,
    high: datetime | str | None = None,
    *,
    tag: str = "effectiveTime",
) -> etree._Element:
    """Create an HL7 v3 Interval of Timestamps (IVL_TS) element.

    # HL7_SPEC: IVL_TS data type — a time interval with optional
    # low and high bounds. At least one bound should be provided.
    # See: HL7 v3 Data Types §4.6 Interval.
    """
    el = _hl7_element(tag)
    if low is not None:
        if isinstance(low, datetime):
            low = low.strftime("%Y%m%d%H%M%S")
        etree.SubElement(el, f"{{{HL7_NS}}}low", value=low)
    if high is not None:
        if isinstance(high, datetime):
            high = high.strftime("%Y%m%d%H%M%S")
        etree.SubElement(el, f"{{{HL7_NS}}}high", value=high)
    return el


def ed(
    content: str,
    *,
    media_type: str = "text/xml",
    representation: str | None = None,
    tag: str = "value",
) -> etree._Element:
    """Create an HL7 v3 Encapsulated Data (ED) element.

    # HL7_SPEC: ED data type — binary or text data with a media type.
    # See: HL7 v3 Data Types §4.7 Encapsulated Data.
    """
    el = _hl7_element(tag, mediaType=media_type, representation=representation)
    el.text = content
    return el


def tel(
    value: str,
    *,
    use: str | None = None,
    tag: str = "telecom",
) -> etree._Element:
    """Create an HL7 v3 Telecommunication Address (TEL) element.

    # HL7_SPEC: TEL data type — a URL-style address (tel:, mailto:, etc.).
    # The `use` attribute indicates purpose (WP=work, HP=home, etc.).
    # See: HL7 v3 Data Types §4.8 Telecommunication Address.
    """
    return _hl7_element(tag, value=value, use=use)


def ad(
    *,
    street: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postal_code: str | None = None,
    country: str | None = None,
    use: str | None = None,
    tag: str = "addr",
) -> etree._Element:
    """Create an HL7 v3 Address (AD) element.

    # HL7_SPEC: AD data type — a postal address with typed components.
    # See: HL7 v3 Data Types §4.9 Postal Address.
    """
    el = _hl7_element(tag, use=use)
    if street is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}streetAddressLine")
        sub.text = street
    if city is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}city")
        sub.text = city
    if state is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}state")
        sub.text = state
    if postal_code is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}postalCode")
        sub.text = postal_code
    if country is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}country")
        sub.text = country
    return el


def pn(
    *,
    family: str | None = None,
    given: str | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
    tag: str = "name",
) -> etree._Element:
    """Create an HL7 v3 Person Name (PN) element.

    # HL7_SPEC: PN data type — a structured person name with components.
    # See: HL7 v3 Data Types §4.10 Entity Name.
    """
    el = _hl7_element(tag)
    if prefix is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}prefix")
        sub.text = prefix
    if given is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}given")
        sub.text = given
    if family is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}family")
        sub.text = family
    if suffix is not None:
        sub = etree.SubElement(el, f"{{{HL7_NS}}}suffix")
        sub.text = suffix
    return el
