"""Tests for safesign_mock.slot.MockSlot."""

import pytest
from safesign_mock import MockSlot, MockToken, TokenNotPresent


class TestSlotInit:
    def test_slot_id(self, empty_slot):
        assert empty_slot.slot_id == 99

    def test_has_token_when_empty(self, empty_slot):
        assert empty_slot.has_token is False

    def test_has_token_when_populated(self, slot_with_token):
        assert slot_with_token.has_token is True


class TestGetToken:
    def test_get_token_success(self, slot_with_token):
        t = slot_with_token.get_token()
        assert isinstance(t, MockToken)

    def test_get_token_empty_slot_raises(self, empty_slot):
        with pytest.raises(TokenNotPresent):
            empty_slot.get_token()


class TestInsertRemove:
    def test_insert_token(self, empty_slot, token):
        empty_slot.insert_token(token)
        assert empty_slot.has_token is True
        assert empty_slot.get_token() is token

    def test_remove_token(self, slot_with_token):
        slot_with_token.remove_token()
        assert slot_with_token.has_token is False

    def test_remove_then_get_raises(self, slot_with_token):
        slot_with_token.remove_token()
        with pytest.raises(TokenNotPresent):
            slot_with_token.get_token()


class TestGetInfo:
    def test_get_info_slot_id(self, empty_slot):
        assert empty_slot.get_info()["slot_id"] == 99

    def test_get_info_description(self, empty_slot):
        assert "description" in empty_slot.get_info()

    def test_get_info_has_token_field(self, slot_with_token):
        assert slot_with_token.get_info()["has_token"] is True
