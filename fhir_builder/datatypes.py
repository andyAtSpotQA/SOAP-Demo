"""
FHIR R4 data type factory functions.

# FHIR_SPEC: FHIR data types use a `value` attribute pattern rather than
# text content. For example: <code value="M"/> not <code>M</code>.
# All factories return lxml.etree.Element instances in the FHIR namespace.

Each function creates a single FHIR data type element. The `tag` parameter
defaults to the standard element name but can be overridden when the same
data type appears under a different XML element name.
"""

from __future__ import annotations

from datetime import datetime, date
from lxml import etree


FHIR_NS = "http://hl7.org/fhir"
NSMAP = {None: FHIR_NS}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fhir_element(tag: str, **attribs) -> etree._Element:
    """Create a FHIR-namespaced element, ignoring None-valued attributes."""
    el = etree.SubElement(etree.Element("_tmp", nsmap=NSMAP), f"{{{FHIR_NS}}}{tag}")
    for k, v in attribs.items():
        if v is not None:
            el.set(k, str(v))
    # Detach from temporary parent
    el.getparent().remove(el)
    return el


def _fhir_sub(parent: etree._Element, tag: str, **attribs) -> etree._Element:
    """Add a FHIR-namespaced child element with attributes (skips Nones)."""
    child = etree.SubElement(parent, f"{{{FHIR_NS}}}{tag}")
    for k, v in attribs.items():
        if v is not None:
            child.set(k, str(v))
    return child


def _to_fhir_datetime(val: str | datetime | date) -> str:
    """Convert to FHIR-compatible ISO 8601 datetime string.

    # FHIR_SPEC: FHIR dates use ISO 8601: YYYY, YYYY-MM, YYYY-MM-DD,
    # or YYYY-MM-DDThh:mm:ss+zz:zz. No "T" separators on date-only values.
    """
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    if isinstance(val, date):
        return val.strftime("%Y-%m-%d")
    return str(val)


# ---------------------------------------------------------------------------
# Public data type factories
# ---------------------------------------------------------------------------

def identifier(
    system: str,
    value: str,
    use: str | None = None,
    tag: str = "identifier",
) -> etree._Element:
    """Create a FHIR Identifier element.

    # FHIR_SPEC: Identifier is a label assigned to a resource instance.
    # system is a URI that defines the namespace for the value.
    # Example: <identifier><system value="https://fhir.nhs.uk/Id/nhs-number"/>
    #          <value value="9999999999"/></identifier>
    """
    el = _fhir_element(tag)
    if use is not None:
        _fhir_sub(el, "use", value=use)
    _fhir_sub(el, "system", value=system)
    _fhir_sub(el, "value", value=value)
    return el


def human_name(
    family: str | None = None,
    given: str | list[str] | None = None,
    prefix: str | list[str] | None = None,
    suffix: str | list[str] | None = None,
    use: str | None = None,
    tag: str = "name",
) -> etree._Element:
    """Create a FHIR HumanName element.

    # FHIR_SPEC: HumanName has use, family (single), given (repeating),
    # prefix (repeating), suffix (repeating). Order matters in FHIR XML.
    """
    el = _fhir_element(tag)
    if use is not None:
        _fhir_sub(el, "use", value=use)
    if family is not None:
        _fhir_sub(el, "family", value=family)
    if given is not None:
        for g in (given if isinstance(given, list) else [given]):
            _fhir_sub(el, "given", value=g)
    if prefix is not None:
        for p in (prefix if isinstance(prefix, list) else [prefix]):
            _fhir_sub(el, "prefix", value=p)
    if suffix is not None:
        for s in (suffix if isinstance(suffix, list) else [suffix]):
            _fhir_sub(el, "suffix", value=s)
    return el


def address(
    line: str | list[str] | None = None,
    city: str | None = None,
    district: str | None = None,
    state: str | None = None,
    postal_code: str | None = None,
    country: str | None = None,
    use: str | None = None,
    type_: str | None = None,
    tag: str = "address",
) -> etree._Element:
    """Create a FHIR Address element.

    # FHIR_SPEC: Address has use, type, line (repeating), city, district,
    # state, postalCode, country. Element ordering matches the spec.
    """
    el = _fhir_element(tag)
    if use is not None:
        _fhir_sub(el, "use", value=use)
    if type_ is not None:
        _fhir_sub(el, "type", value=type_)
    if line is not None:
        for ln in (line if isinstance(line, list) else [line]):
            _fhir_sub(el, "line", value=ln)
    if city is not None:
        _fhir_sub(el, "city", value=city)
    if district is not None:
        _fhir_sub(el, "district", value=district)
    if state is not None:
        _fhir_sub(el, "state", value=state)
    if postal_code is not None:
        _fhir_sub(el, "postalCode", value=postal_code)
    if country is not None:
        _fhir_sub(el, "country", value=country)
    return el


def coding(
    system: str,
    code: str,
    display: str | None = None,
    tag: str = "coding",
) -> etree._Element:
    """Create a FHIR Coding element.

    # FHIR_SPEC: Coding is a single code from a code system.
    # Example: <coding><system value="http://snomed.info/sct"/>
    #          <code value="91936005"/><display value="Penicillin allergy"/></coding>
    """
    el = _fhir_element(tag)
    _fhir_sub(el, "system", value=system)
    _fhir_sub(el, "code", value=code)
    if display is not None:
        _fhir_sub(el, "display", value=display)
    return el


def codeable_concept(
    system: str,
    code: str,
    display: str | None = None,
    text: str | None = None,
    tag: str = "code",
) -> etree._Element:
    """Create a FHIR CodeableConcept element with a single Coding.

    # FHIR_SPEC: CodeableConcept wraps one or more Codings and an optional
    # text summary. Most NHS resources use a single SNOMED CT coding.
    """
    el = _fhir_element(tag)
    el.append(coding(system, code, display))
    if text is not None:
        _fhir_sub(el, "text", value=text)
    return el


def codeable_concept_from_codings(
    codings: list[etree._Element],
    text: str | None = None,
    tag: str = "code",
) -> etree._Element:
    """Create a CodeableConcept from multiple pre-built Coding elements.

    # FHIR_SPEC: Some resources need multiple codings (e.g. SNOMED + dm+d).
    """
    el = _fhir_element(tag)
    for c in codings:
        el.append(c)
    if text is not None:
        _fhir_sub(el, "text", value=text)
    return el


def reference(
    ref: str,
    type_: str | None = None,
    display: str | None = None,
    tag: str = "reference",
) -> etree._Element:
    """Create a FHIR Reference element.

    # FHIR_SPEC: Reference links resources together. The `reference` child
    # holds a relative URL (e.g. "Patient/123") or a URN (e.g. "urn:uuid:...").
    """
    el = _fhir_element(tag)
    _fhir_sub(el, "reference", value=ref)
    if type_ is not None:
        _fhir_sub(el, "type", value=type_)
    if display is not None:
        _fhir_sub(el, "display", value=display)
    return el


def period(
    start: str | datetime | date | None = None,
    end: str | datetime | date | None = None,
    tag: str = "period",
) -> etree._Element:
    """Create a FHIR Period element.

    # FHIR_SPEC: Period represents a start and/or end time. At least one
    # of start or end should be provided.
    """
    el = _fhir_element(tag)
    if start is not None:
        _fhir_sub(el, "start", value=_to_fhir_datetime(start))
    if end is not None:
        _fhir_sub(el, "end", value=_to_fhir_datetime(end))
    return el


def contact_point(
    system: str,
    value: str,
    use: str | None = None,
    tag: str = "telecom",
) -> etree._Element:
    """Create a FHIR ContactPoint element.

    # FHIR_SPEC: ContactPoint captures phone, email, etc. Used in
    # Patient.telecom, Organization.telecom, Practitioner.telecom.
    """
    el = _fhir_element(tag)
    _fhir_sub(el, "system", value=system)
    _fhir_sub(el, "value", value=value)
    if use is not None:
        _fhir_sub(el, "use", value=use)
    return el


def meta(
    profile: str | list[str] | None = None,
    version_id: str | None = None,
    last_updated: str | datetime | None = None,
    tag_element: str = "meta",
) -> etree._Element:
    """Create a FHIR Meta element.

    # FHIR_SPEC: Meta holds resource metadata — profile declarations,
    # version tracking, and security labels. UK Core requires profile
    # to be set for all resources.
    """
    el = _fhir_element(tag_element)
    if version_id is not None:
        _fhir_sub(el, "versionId", value=version_id)
    if last_updated is not None:
        _fhir_sub(el, "lastUpdated", value=_to_fhir_datetime(last_updated))
    if profile is not None:
        for p in (profile if isinstance(profile, list) else [profile]):
            _fhir_sub(el, "profile", value=p)
    return el
