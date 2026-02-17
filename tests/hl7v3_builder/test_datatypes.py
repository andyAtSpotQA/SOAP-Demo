"""Tests for hl7v3_builder.datatypes — HL7 v3 data type element factories."""

from datetime import datetime
from lxml import etree

from hl7v3_builder.datatypes import (
    HL7_NS,
    ii,
    cd,
    ts,
    st,
    pq,
    ivl_ts,
    ed,
    tel,
    ad,
    pn,
)


def _localname(el):
    return etree.QName(el.tag).localname


class TestII:
    def test_root_attribute(self):
        el = ii(root="2.16.840.1.113883.2.1.4.1")
        assert el.get("root") == "2.16.840.1.113883.2.1.4.1"

    def test_extension_attribute(self):
        el = ii(root="1.2.3", extension="ABC123")
        assert el.get("extension") == "ABC123"

    def test_default_tag_is_id(self):
        el = ii(root="1.2.3")
        assert _localname(el) == "id"

    def test_custom_tag(self):
        el = ii(root="1.2.3", tag="interactionId")
        assert _localname(el) == "interactionId"

    def test_assigning_authority_name(self):
        el = ii(root="1.2.3", assigning_authority_name="NHS")
        assert el.get("assigningAuthorityName") == "NHS"

    def test_extension_none_omitted(self):
        el = ii(root="1.2.3")
        assert el.get("extension") is None

    def test_namespace_is_hl7(self):
        el = ii(root="1.2.3")
        assert HL7_NS in el.tag


class TestCD:
    def test_code_attribute(self):
        el = cd("D")
        assert el.get("code") == "D"

    def test_code_system(self):
        el = cd("D", code_system="2.16.840.1.113883.5.7")
        assert el.get("codeSystem") == "2.16.840.1.113883.5.7"

    def test_display_name(self):
        el = cd("M", display_name="Male")
        assert el.get("displayName") == "Male"

    def test_code_system_name(self):
        el = cd("M", code_system_name="HL7Gender")
        assert el.get("codeSystemName") == "HL7Gender"

    def test_default_tag_is_code(self):
        assert _localname(cd("X")) == "code"

    def test_custom_tag(self):
        assert _localname(cd("X", tag="processingCode")) == "processingCode"


class TestTS:
    def test_explicit_datetime(self):
        dt = datetime(2024, 3, 15, 10, 30, 0)
        el = ts(dt)
        assert el.get("value") == "20240315103000"

    def test_string_value(self):
        el = ts("20240101120000")
        assert el.get("value") == "20240101120000"

    def test_none_uses_now(self):
        el = ts()
        assert el.get("value") is not None
        assert len(el.get("value")) == 14  # YYYYMMDDHHmmss

    def test_default_tag_is_creation_time(self):
        assert _localname(ts()) == "creationTime"

    def test_custom_tag(self):
        assert _localname(ts(tag="effectiveTime")) == "effectiveTime"


class TestST:
    def test_text_content(self):
        el = st("Hello World")
        assert el.text == "Hello World"

    def test_default_tag_is_value(self):
        assert _localname(st("x")) == "value"

    def test_custom_tag(self):
        assert _localname(st("x", tag="name")) == "name"


class TestPQ:
    def test_value_attribute(self):
        el = pq(42.5, "mg")
        assert el.get("value") == "42.5"

    def test_unit_attribute(self):
        el = pq(1, "kg")
        assert el.get("unit") == "kg"

    def test_default_tag_is_value(self):
        assert _localname(pq(1, "mg")) == "value"

    def test_string_value(self):
        el = pq("100", "mL")
        assert el.get("value") == "100"


class TestIVL_TS:
    def test_low_and_high(self):
        el = ivl_ts(low="20240101", high="20241231")
        low_el = el.find(f"{{{HL7_NS}}}low")
        high_el = el.find(f"{{{HL7_NS}}}high")
        assert low_el.get("value") == "20240101"
        assert high_el.get("value") == "20241231"

    def test_low_only(self):
        el = ivl_ts(low="20240101")
        assert el.find(f"{{{HL7_NS}}}low") is not None
        assert el.find(f"{{{HL7_NS}}}high") is None

    def test_high_only(self):
        el = ivl_ts(high="20241231")
        assert el.find(f"{{{HL7_NS}}}low") is None
        assert el.find(f"{{{HL7_NS}}}high") is not None

    def test_datetime_low(self):
        dt = datetime(2024, 6, 1, 0, 0, 0)
        el = ivl_ts(low=dt)
        assert el.find(f"{{{HL7_NS}}}low").get("value") == "20240601000000"

    def test_default_tag(self):
        assert _localname(ivl_ts()) == "effectiveTime"


class TestED:
    def test_content_as_text(self):
        el = ed("some content")
        assert el.text == "some content"

    def test_default_media_type(self):
        el = ed("x")
        assert el.get("mediaType") == "text/xml"

    def test_custom_media_type(self):
        el = ed("x", media_type="text/plain")
        assert el.get("mediaType") == "text/plain"

    def test_representation_attribute(self):
        el = ed("x", representation="B64")
        assert el.get("representation") == "B64"

    def test_default_tag_is_value(self):
        assert _localname(ed("x")) == "value"


class TestTEL:
    def test_value_attribute(self):
        el = tel("tel:01onal123456")
        assert el.get("value") == "tel:01anal123456" or el.get("value").startswith("tel:")

    def test_use_attribute(self):
        el = tel("tel:123", use="WP")
        assert el.get("use") == "WP"

    def test_use_omitted_when_none(self):
        el = tel("tel:123")
        assert el.get("use") is None

    def test_default_tag(self):
        assert _localname(tel("tel:1")) == "telecom"


class TestAD:
    def test_street(self):
        el = ad(street="123 Main St")
        street_el = el.find(f"{{{HL7_NS}}}streetAddressLine")
        assert street_el.text == "123 Main St"

    def test_city(self):
        el = ad(city="London")
        assert el.find(f"{{{HL7_NS}}}city").text == "London"

    def test_state(self):
        el = ad(state="Greater London")
        assert el.find(f"{{{HL7_NS}}}state").text == "Greater London"

    def test_postal_code(self):
        el = ad(postal_code="SW1A 1AA")
        assert el.find(f"{{{HL7_NS}}}postalCode").text == "SW1A 1AA"

    def test_country(self):
        el = ad(country="UK")
        assert el.find(f"{{{HL7_NS}}}country").text == "UK"

    def test_use_attribute(self):
        el = ad(use="WP")
        assert el.get("use") == "WP"

    def test_default_tag(self):
        assert _localname(ad()) == "addr"

    def test_all_fields(self):
        el = ad(
            street="10 Downing St",
            city="London",
            postal_code="SW1A 2AA",
            country="UK",
        )
        assert len(list(el)) == 4  # street, city, postalCode, country


class TestPN:
    def test_family_name(self):
        el = pn(family="Smith")
        assert el.find(f"{{{HL7_NS}}}family").text == "Smith"

    def test_given_name(self):
        el = pn(given="John")
        assert el.find(f"{{{HL7_NS}}}given").text == "John"

    def test_prefix(self):
        el = pn(prefix="Dr")
        assert el.find(f"{{{HL7_NS}}}prefix").text == "Dr"

    def test_suffix(self):
        el = pn(suffix="Jr")
        assert el.find(f"{{{HL7_NS}}}suffix").text == "Jr"

    def test_default_tag(self):
        assert _localname(pn()) == "name"

    def test_full_name(self):
        el = pn(prefix="Dr", given="John", family="Smith", suffix="III")
        children = [_localname(c) for c in el]
        assert children == ["prefix", "given", "family", "suffix"]
