"""Tests for safesign_mock.library.MockPKCS11Library."""

import pytest
from safesign_mock import MockPKCS11Library, MockSlot, MockToken, TokenNotPresent


class TestLibraryInit:
    def test_default_slot_exists(self, pkcs11_library):
        assert len(pkcs11_library.get_slots()) == 1

    def test_default_token_label(self, pkcs11_library):
        t = pkcs11_library.get_token()
        assert t.label == "MockSafeSign"


class TestGetSlots:
    def test_returns_list_of_slots(self, pkcs11_library):
        slots = pkcs11_library.get_slots()
        assert all(isinstance(s, MockSlot) for s in slots)

    def test_default_has_one_slot(self, pkcs11_library):
        assert len(pkcs11_library.get_slots()) == 1


class TestGetToken:
    def test_get_token_no_label(self, pkcs11_library):
        t = pkcs11_library.get_token(token_label=None)
        assert isinstance(t, MockToken)

    def test_get_token_by_label(self, pkcs11_library):
        t = pkcs11_library.get_token(token_label="MockSafeSign")
        assert t.label == "MockSafeSign"

    def test_get_token_wrong_label_raises(self, pkcs11_library):
        with pytest.raises(TokenNotPresent):
            pkcs11_library.get_token(token_label="nonexistent")

    def test_get_token_no_tokens_raises(self):
        lib = MockPKCS11Library()
        lib._slots = [MockSlot(slot_id=0)]  # empty slot
        with pytest.raises(TokenNotPresent):
            lib.get_token()


class TestAddSlot:
    def test_add_slot_increases_count(self, pkcs11_library):
        pkcs11_library.add_slot(MockSlot(slot_id=1))
        assert len(pkcs11_library.get_slots()) == 2

    def test_added_slot_token_accessible(self, pkcs11_library):
        new_token = MockToken(label="SecondToken")
        pkcs11_library.add_slot(MockSlot(slot_id=1, token=new_token))
        t = pkcs11_library.get_token(token_label="SecondToken")
        assert t.label == "SecondToken"


class TestGetInfo:
    def test_get_info_has_library_name(self, pkcs11_library):
        assert "MockPKCS11" in pkcs11_library.get_info()["library"]

    def test_get_info_has_version(self, pkcs11_library):
        assert pkcs11_library.get_info()["version"] == "1.0.0"

    def test_get_info_has_slots_list(self, pkcs11_library):
        info = pkcs11_library.get_info()
        assert isinstance(info["slots"], list)
        assert len(info["slots"]) == 1
