"""Tests for safesign_mock.exceptions — PKCS#11 exception hierarchy."""

from safesign_mock import (
    PKCS11Error, PinIncorrect, PinLocked, SessionClosed,
    TokenNotPresent, ObjectNotFound, MechanismInvalid, UserNotLoggedIn,
)


class TestExceptionInstantiation:
    def test_pkcs11error_instantiates(self):
        e = PKCS11Error("test")
        assert str(e) == "test"

    def test_pin_incorrect_instantiates(self):
        e = PinIncorrect("wrong pin")
        assert "wrong pin" in str(e)

    def test_pin_locked_instantiates(self):
        e = PinLocked("locked")
        assert "locked" in str(e)

    def test_session_closed_instantiates(self):
        e = SessionClosed("closed")
        assert str(e) == "closed"

    def test_token_not_present_instantiates(self):
        e = TokenNotPresent("no card")
        assert str(e) == "no card"

    def test_object_not_found_instantiates(self):
        e = ObjectNotFound("missing")
        assert str(e) == "missing"

    def test_mechanism_invalid_instantiates(self):
        e = MechanismInvalid("bad mech")
        assert str(e) == "bad mech"

    def test_user_not_logged_in_instantiates(self):
        e = UserNotLoggedIn("no login")
        assert str(e) == "no login"


class TestExceptionInheritance:
    def test_pin_incorrect_is_pkcs11error(self):
        assert issubclass(PinIncorrect, PKCS11Error)

    def test_pin_locked_is_pkcs11error(self):
        assert issubclass(PinLocked, PKCS11Error)

    def test_session_closed_is_pkcs11error(self):
        assert issubclass(SessionClosed, PKCS11Error)

    def test_token_not_present_is_pkcs11error(self):
        assert issubclass(TokenNotPresent, PKCS11Error)

    def test_object_not_found_is_pkcs11error(self):
        assert issubclass(ObjectNotFound, PKCS11Error)

    def test_mechanism_invalid_is_pkcs11error(self):
        assert issubclass(MechanismInvalid, PKCS11Error)

    def test_user_not_logged_in_is_pkcs11error(self):
        assert issubclass(UserNotLoggedIn, PKCS11Error)

    def test_pkcs11error_is_exception(self):
        assert issubclass(PKCS11Error, Exception)
