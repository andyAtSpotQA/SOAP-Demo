"""Tests for safesign_mock.token.MockToken — PIN management and sessions."""

import pytest
from safesign_mock import MockToken, MockSession, TokenStore, PinIncorrect, PinLocked


class TestTokenInit:
    def test_default_label(self):
        t = MockToken()
        assert t.label == "MockSafeSign"

    def test_custom_label(self):
        t = MockToken(label="MyCard")
        assert t.label == "MyCard"

    def test_default_pin_retries(self, token):
        assert token.pin_retries_left == 3

    def test_not_locked_initially(self, token):
        assert token.is_locked is False


class TestOpen:
    def test_open_with_correct_pin(self, token):
        session = token.open(rw=True, user_pin="1234")
        assert isinstance(session, MockSession)

    def test_open_without_pin(self, token):
        session = token.open(user_pin=None)
        assert isinstance(session, MockSession)

    def test_open_with_wrong_pin_raises_pin_incorrect(self, token):
        with pytest.raises(PinIncorrect):
            token.open(user_pin="wrong")

    def test_open_rw_false(self, token):
        session = token.open(rw=False, user_pin="1234")
        assert isinstance(session, MockSession)


class TestPinRetry:
    def test_wrong_pin_decrements_retries(self, token):
        with pytest.raises(PinIncorrect):
            token.open(user_pin="bad")
        assert token.pin_retries_left == 2

    def test_two_wrong_attempts_leaves_one_retry(self, token):
        for _ in range(2):
            with pytest.raises(PinIncorrect):
                token.open(user_pin="bad")
        assert token.pin_retries_left == 1

    def test_three_wrong_pins_lock_token(self, token):
        for _ in range(2):
            with pytest.raises(PinIncorrect):
                token.open(user_pin="bad")
        with pytest.raises(PinLocked):
            token.open(user_pin="bad")
        assert token.is_locked is True

    def test_correct_pin_resets_retries(self, token):
        with pytest.raises(PinIncorrect):
            token.open(user_pin="bad")
        assert token.pin_retries_left == 2
        token.open(user_pin="1234")
        assert token.pin_retries_left == 3

    def test_locked_token_rejects_correct_pin(self, token):
        for _ in range(2):
            with pytest.raises(PinIncorrect):
                token.open(user_pin="bad")
        with pytest.raises(PinLocked):
            token.open(user_pin="bad")
        with pytest.raises(PinLocked):
            token.open(user_pin="1234")


class TestChangePin:
    def test_change_pin_success(self, token):
        token.change_pin("1234", "newpin")
        session = token.open(user_pin="newpin")
        assert isinstance(session, MockSession)

    def test_change_pin_wrong_old_pin(self, token):
        with pytest.raises(PinIncorrect):
            token.change_pin("wrong", "newpin")

    def test_change_pin_short_new_pin(self, token):
        with pytest.raises(ValueError, match="at least 4"):
            token.change_pin("1234", "12")

    def test_change_pin_exactly_four_chars(self, token):
        token.change_pin("1234", "abcd")
        token.open(user_pin="abcd")


class TestGetInfo:
    def test_get_info_contains_label(self, token):
        info = token.get_info()
        assert info["label"] == "TestToken"

    def test_get_info_contains_retries(self, token):
        assert "pin_retries_left" in token.get_info()

    def test_get_info_contains_locked_status(self, token):
        assert token.get_info()["is_locked"] is False

    def test_get_info_contains_object_count(self, token):
        assert token.get_info()["objects_stored"] == 0


class TestStoreProperty:
    def test_store_returns_token_store_instance(self, token):
        assert isinstance(token.store, TokenStore)
