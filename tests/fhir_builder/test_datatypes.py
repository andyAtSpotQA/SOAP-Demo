"""Tests for fhir_builder.datatypes — FHIR R4 data type factories."""

from datetime import datetime, date
from lxml import etree

from fhir_builder.datatypes import (
    FHIR_NS,
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


def _localname(el):
    return etree.QName(el.tag).localname


def _child(el, name):
    return el.find(f"{{{FHIR_NS}}}{name}")


def _child_val(el, name):
    child = _child(el, name)
    return child.get("value") if child is not None else None


class TestIdentifier:
    def test_system_child(self):
        el = identifier(system="https://fhir.nhs.uk/Id/nhs-number", value="9999999999")
        assert _child_val(el, "system") == "https://fhir.nhs.uk/Id/nhs-number"

    def test_value_child(self):
        el = identifier(system="https://fhir.nhs.uk/Id/nhs-number", value="9999999999")
        assert _child_val(el, "value") == "9999999999"

    def test_use_child(self):
        el = identifier(system="urn:test", value="123", use="official")
        assert _child_val(el, "use") == "official"

    def test_use_omitted_when_none(self):
        el = identifier(system="urn:test", value="123")
        assert _child(el, "use") is None

    def test_default_tag(self):
        el = identifier(system="urn:test", value="123")
        assert _localname(el) == "identifier"

    def test_custom_tag(self):
        el = identifier(system="urn:test", value="123", tag="groupIdentifier")
        assert _localname(el) == "groupIdentifier"


class TestHumanName:
    def test_family(self):
        el = human_name(family="Smith")
        assert _child_val(el, "family") == "Smith"

    def test_given_single(self):
        el = human_name(given="John")
        assert _child_val(el, "given") == "John"

    def test_given_list(self):
        el = human_name(given=["John", "James"])
        givens = el.findall(f"{{{FHIR_NS}}}given")
        assert len(givens) == 2
        assert givens[0].get("value") == "John"
        assert givens[1].get("value") == "James"

    def test_prefix_single(self):
        el = human_name(prefix="Dr")
        assert _child_val(el, "prefix") == "Dr"

    def test_suffix_single(self):
        el = human_name(suffix="III")
        assert _child_val(el, "suffix") == "III"

    def test_use(self):
        el = human_name(use="official")
        assert _child_val(el, "use") == "official"

    def test_default_tag(self):
        el = human_name()
        assert _localname(el) == "name"


class TestAddress:
    def test_line_single(self):
        el = address(line="123 Main St")
        assert _child_val(el, "line") == "123 Main St"

    def test_line_list(self):
        el = address(line=["123 Main St", "Apt 4"])
        lines = el.findall(f"{{{FHIR_NS}}}line")
        assert len(lines) == 2

    def test_city(self):
        el = address(city="London")
        assert _child_val(el, "city") == "London"

    def test_postal_code(self):
        el = address(postal_code="SW1A 1AA")
        assert _child_val(el, "postalCode") == "SW1A 1AA"

    def test_country(self):
        el = address(country="UK")
        assert _child_val(el, "country") == "UK"

    def test_use(self):
        el = address(use="home")
        assert _child_val(el, "use") == "home"

    def test_type(self):
        el = address(type_="postal")
        assert _child_val(el, "type") == "postal"

    def test_district(self):
        el = address(district="Greater London")
        assert _child_val(el, "district") == "Greater London"

    def test_state(self):
        el = address(state="England")
        assert _child_val(el, "state") == "England"

    def test_default_tag(self):
        assert _localname(address()) == "address"


class TestCoding:
    def test_system(self):
        el = coding(system="http://snomed.info/sct", code="91936005")
        assert _child_val(el, "system") == "http://snomed.info/sct"

    def test_code(self):
        el = coding(system="http://snomed.info/sct", code="91936005")
        assert _child_val(el, "code") == "91936005"

    def test_display(self):
        el = coding(system="http://snomed.info/sct", code="91936005", display="Penicillin allergy")
        assert _child_val(el, "display") == "Penicillin allergy"

    def test_display_omitted(self):
        el = coding(system="urn:test", code="X")
        assert _child(el, "display") is None

    def test_default_tag(self):
        assert _localname(coding(system="urn:test", code="X")) == "coding"


class TestCodeableConcept:
    def test_has_coding_child(self):
        el = codeable_concept(system="urn:test", code="X")
        assert _child(el, "coding") is not None

    def test_coding_system(self):
        el = codeable_concept(system="http://snomed.info/sct", code="123")
        coding_el = _child(el, "coding")
        assert _child_val(coding_el, "system") == "http://snomed.info/sct"

    def test_text(self):
        el = codeable_concept(system="urn:test", code="X", text="Some text")
        assert _child_val(el, "text") == "Some text"

    def test_text_omitted(self):
        el = codeable_concept(system="urn:test", code="X")
        assert _child(el, "text") is None

    def test_default_tag(self):
        assert _localname(codeable_concept(system="urn:test", code="X")) == "code"

    def test_custom_tag(self):
        el = codeable_concept(system="urn:test", code="X", tag="clinicalStatus")
        assert _localname(el) == "clinicalStatus"


class TestCodeableConceptFromCodings:
    def test_multiple_codings(self):
        c1 = coding(system="http://snomed.info/sct", code="123")
        c2 = coding(system="https://dmd.nhs.uk", code="456")
        el = codeable_concept_from_codings([c1, c2])
        codings = el.findall(f"{{{FHIR_NS}}}coding")
        assert len(codings) == 2

    def test_text(self):
        c1 = coding(system="urn:test", code="X")
        el = codeable_concept_from_codings([c1], text="Test")
        assert _child_val(el, "text") == "Test"

    def test_default_tag(self):
        c1 = coding(system="urn:test", code="X")
        assert _localname(codeable_concept_from_codings([c1])) == "code"


class TestReference:
    def test_reference_value(self):
        el = reference(ref="Patient/123")
        assert _child_val(el, "reference") == "Patient/123"

    def test_type(self):
        el = reference(ref="Patient/123", type_="Patient")
        assert _child_val(el, "type") == "Patient"

    def test_display(self):
        el = reference(ref="Patient/123", display="John Smith")
        assert _child_val(el, "display") == "John Smith"

    def test_default_tag(self):
        assert _localname(reference(ref="X")) == "reference"

    def test_custom_tag(self):
        el = reference(ref="X", tag="subject")
        assert _localname(el) == "subject"


class TestPeriod:
    def test_start_string(self):
        el = period(start="2024-01-01")
        assert _child_val(el, "start") == "2024-01-01"

    def test_end_string(self):
        el = period(end="2024-12-31")
        assert _child_val(el, "end") == "2024-12-31"

    def test_datetime_start(self):
        dt = datetime(2024, 6, 15, 12, 0, 0)
        el = period(start=dt)
        assert "2024-06-15" in _child_val(el, "start")

    def test_date_start(self):
        d = date(2024, 6, 15)
        el = period(start=d)
        assert _child_val(el, "start") == "2024-06-15"

    def test_default_tag(self):
        assert _localname(period()) == "period"


class TestContactPoint:
    def test_system(self):
        el = contact_point(system="phone", value="01onal123456")
        assert _child_val(el, "system") == "phone"

    def test_value(self):
        el = contact_point(system="email", value="test@example.com")
        assert _child_val(el, "value") == "test@example.com"

    def test_use(self):
        el = contact_point(system="phone", value="123", use="home")
        assert _child_val(el, "use") == "home"

    def test_use_omitted(self):
        el = contact_point(system="phone", value="123")
        assert _child(el, "use") is None

    def test_default_tag(self):
        assert _localname(contact_point(system="phone", value="123")) == "telecom"


class TestMeta:
    def test_profile_single(self):
        el = meta(profile="https://fhir.hl7.org.uk/StructureDefinition/UKCore-Patient")
        assert _child_val(el, "profile") == "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Patient"

    def test_profile_list(self):
        el = meta(profile=["profile1", "profile2"])
        profiles = el.findall(f"{{{FHIR_NS}}}profile")
        assert len(profiles) == 2

    def test_version_id(self):
        el = meta(version_id="1")
        assert _child_val(el, "versionId") == "1"

    def test_last_updated(self):
        el = meta(last_updated="2024-01-01T00:00:00+00:00")
        assert _child_val(el, "lastUpdated") == "2024-01-01T00:00:00+00:00"

    def test_default_tag(self):
        assert _localname(meta()) == "meta"
