"""Tests for fhir_builder.exceptions — exception hierarchy."""

import pytest
from fhir_builder.exceptions import (
    FHIRBuilderError,
    ValidationError,
    TemplateError,
    SerializationError,
)


class TestFHIRBuilderError:
    def test_is_base_exception(self):
        assert issubclass(FHIRBuilderError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(FHIRBuilderError):
            raise FHIRBuilderError("test")


class TestValidationError:
    def test_inherits_from_base(self):
        assert issubclass(ValidationError, FHIRBuilderError)

    def test_has_field_attribute(self):
        err = ValidationError("bad", field="type")
        assert err.field == "type"

    def test_field_defaults_to_none(self):
        err = ValidationError("bad")
        assert err.field is None

    def test_field_in_message(self):
        err = ValidationError("missing", field="entries")
        assert "entries" in str(err)

    def test_message_without_field(self):
        err = ValidationError("something wrong")
        assert "something wrong" in str(err)


class TestTemplateError:
    def test_inherits_from_base(self):
        assert issubclass(TemplateError, FHIRBuilderError)

    def test_can_be_raised(self):
        with pytest.raises(TemplateError):
            raise TemplateError("template error")


class TestSerializationError:
    def test_inherits_from_base(self):
        assert issubclass(SerializationError, FHIRBuilderError)

    def test_can_be_raised(self):
        with pytest.raises(SerializationError):
            raise SerializationError("xml error")
