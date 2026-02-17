"""Tests for fhir_builder.builder — FHIRBundleBuilder and FHIRBundle."""

import pytest
from lxml import etree

from fhir_builder.builder import FHIRBundleBuilder, FHIRBundle
from fhir_builder.datatypes import FHIR_NS
from fhir_builder.resources import patient, message_header
from fhir_builder.types import BundleType
from fhir_builder.exceptions import ValidationError


def _child(el, name):
    return el.find(f"{{{FHIR_NS}}}{name}")


def _child_val(el, name):
    child = _child(el, name)
    return child.get("value") if child is not None else None


class TestBuilderValidation:
    def test_missing_type_fails(self, fhir_patient_element):
        b = FHIRBundleBuilder().add_entry(fhir_patient_element)
        errors = b.validate()
        assert any("type" in e.lower() for e in errors)

    def test_no_entries_fails(self):
        b = FHIRBundleBuilder().set_type(BundleType.SEARCHSET)
        errors = b.validate()
        assert any("entry" in e.lower() for e in errors)

    def test_valid_searchset_no_errors(self, fhir_searchset_builder):
        assert fhir_searchset_builder.validate() == []

    def test_build_raises_on_invalid(self):
        with pytest.raises(ValidationError):
            FHIRBundleBuilder().build()

    def test_message_must_start_with_message_header(self, fhir_patient_element):
        b = (
            FHIRBundleBuilder()
            .set_type(BundleType.MESSAGE)
            .add_entry(fhir_patient_element)
        )
        errors = b.validate()
        assert any("MessageHeader" in e for e in errors)

    def test_message_with_header_first_valid(self, fhir_message_header_element):
        b = (
            FHIRBundleBuilder()
            .set_type(BundleType.MESSAGE)
            .add_entry(fhir_message_header_element)
        )
        assert b.validate() == []

    def test_transaction_missing_request_method(self, fhir_patient_element):
        b = (
            FHIRBundleBuilder()
            .set_type(BundleType.TRANSACTION)
            .add_entry(fhir_patient_element)
        )
        errors = b.validate()
        assert any("request_method" in e for e in errors)

    def test_transaction_with_request_valid(self, fhir_patient_element):
        b = (
            FHIRBundleBuilder()
            .set_type(BundleType.TRANSACTION)
            .add_entry(fhir_patient_element, request_method="POST", request_url="Patient")
        )
        assert b.validate() == []


class TestBuilderBuild:
    def test_returns_fhir_bundle(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        assert isinstance(bundle, FHIRBundle)

    def test_root_element_is_bundle(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        assert etree.QName(bundle.root.tag).localname == "Bundle"

    def test_bundle_id(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        assert bundle.bundle_id is not None

    def test_custom_bundle_id(self, fhir_patient_element):
        bundle = (
            FHIRBundleBuilder()
            .set_id("custom-id")
            .set_type(BundleType.SEARCHSET)
            .add_entry(fhir_patient_element)
            .build()
        )
        assert bundle.bundle_id == "custom-id"

    def test_bundle_type_property(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        assert bundle.bundle_type == BundleType.SEARCHSET

    def test_type_element(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        assert _child_val(bundle.root, "type") == "searchset"

    def test_timestamp_element(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        ts = _child_val(bundle.root, "timestamp")
        assert ts is not None

    def test_total_element(self, fhir_patient_element):
        bundle = (
            FHIRBundleBuilder()
            .set_type(BundleType.SEARCHSET)
            .set_total(5)
            .add_entry(fhir_patient_element)
            .build()
        )
        assert _child_val(bundle.root, "total") == "5"

    def test_profile_element(self, fhir_patient_element):
        bundle = (
            FHIRBundleBuilder()
            .set_type(BundleType.SEARCHSET)
            .set_profile("https://fhir.hl7.org.uk/StructureDefinition/UKCore-Bundle")
            .add_entry(fhir_patient_element)
            .build()
        )
        meta_el = _child(bundle.root, "meta")
        assert meta_el is not None


class TestBundleEntries:
    def test_entry_count(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 1

    def test_entry_has_full_url(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        entry = _child(bundle.root, "entry")
        full_url = _child_val(entry, "fullUrl")
        assert full_url is not None
        assert full_url.startswith("urn:uuid:")

    def test_custom_full_url(self, fhir_patient_element):
        bundle = (
            FHIRBundleBuilder()
            .set_type(BundleType.SEARCHSET)
            .add_entry(fhir_patient_element, full_url="https://test.com/Patient/1")
            .build()
        )
        entry = _child(bundle.root, "entry")
        assert _child_val(entry, "fullUrl") == "https://test.com/Patient/1"

    def test_entry_has_resource(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        entry = _child(bundle.root, "entry")
        resource = _child(entry, "resource")
        assert resource is not None
        assert len(resource) > 0

    def test_search_mode(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        entry = _child(bundle.root, "entry")
        search = _child(entry, "search")
        assert _child_val(search, "mode") == "match"

    def test_transaction_request(self, fhir_patient_element):
        bundle = (
            FHIRBundleBuilder()
            .set_type(BundleType.TRANSACTION)
            .add_entry(fhir_patient_element, request_method="POST", request_url="Patient")
            .build()
        )
        entry = _child(bundle.root, "entry")
        request = _child(entry, "request")
        assert _child_val(request, "method") == "POST"
        assert _child_val(request, "url") == "Patient"

    def test_multiple_entries(self, fhir_patient_element, fhir_message_header_element):
        bundle = (
            FHIRBundleBuilder()
            .set_type(BundleType.MESSAGE)
            .add_entry(fhir_message_header_element)
            .add_entry(fhir_patient_element)
            .build()
        )
        entries = bundle.root.findall(f"{{{FHIR_NS}}}entry")
        assert len(entries) == 2


class TestFHIRBundle:
    def test_to_xml_returns_string(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        xml = bundle.to_xml()
        assert isinstance(xml, str)

    def test_to_xml_has_declaration(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        assert bundle.to_xml().startswith("<?xml")

    def test_to_element_returns_element(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        assert isinstance(bundle.to_element(), etree._Element)

    def test_root_property(self, fhir_searchset_builder):
        bundle = fhir_searchset_builder.build()
        assert bundle.root is bundle.to_element()


class TestFluentChaining:
    def test_all_setters_return_builder(self, fhir_patient_element):
        b = FHIRBundleBuilder()
        assert isinstance(b.set_id("X"), FHIRBundleBuilder)
        assert isinstance(b.set_type(BundleType.SEARCHSET), FHIRBundleBuilder)
        assert isinstance(b.set_timestamp(), FHIRBundleBuilder)
        assert isinstance(b.set_total(1), FHIRBundleBuilder)
        assert isinstance(b.set_profile("http://example.com"), FHIRBundleBuilder)
        assert isinstance(b.add_entry(fhir_patient_element), FHIRBundleBuilder)
