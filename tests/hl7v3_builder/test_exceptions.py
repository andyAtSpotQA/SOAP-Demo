"""Tests for hl7v3_builder.exceptions — exception hierarchy."""

import pytest
from hl7v3_builder.exceptions import (
    HL7BuilderError,
    ValidationError,
    TemplateError,
    SerializationError,
    SoapWrappingError,
)


class TestHL7BuilderError:
    def test_is_base_exception(self):
        assert issubclass(HL7BuilderError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(HL7BuilderError):
            raise HL7BuilderError("test")


class TestValidationError:
    def test_inherits_from_base(self):
        assert issubclass(ValidationError, HL7BuilderError)

    def test_has_field_attribute(self):
        err = ValidationError("bad", field="interaction")
        assert err.field == "interaction"

    def test_field_defaults_to_none(self):
        err = ValidationError("bad")
        assert err.field is None

    def test_message_preserved(self):
        err = ValidationError("missing required field")
        assert "missing required field" in str(err)


class TestTemplateError:
    def test_inherits_from_base(self):
        assert issubclass(TemplateError, HL7BuilderError)

    def test_can_be_raised(self):
        with pytest.raises(TemplateError):
            raise TemplateError("template not found")


class TestSerializationError:
    def test_inherits_from_base(self):
        assert issubclass(SerializationError, HL7BuilderError)

    def test_can_be_raised(self):
        with pytest.raises(SerializationError):
            raise SerializationError("xml error")


class TestSoapWrappingError:
    def test_inherits_from_base(self):
        assert issubclass(SoapWrappingError, HL7BuilderError)

    def test_can_be_raised(self):
        with pytest.raises(SoapWrappingError):
            raise SoapWrappingError("missing to_url")
