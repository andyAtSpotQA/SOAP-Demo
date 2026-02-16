"""
Mock PKCS#11 slot — card reader simulation.

# REAL_SDK: A slot represents a physical card reader. Each slot may or may
# not have a token (card) inserted. SafeSign's middleware enumerates slots
# via C_GetSlotList. This mock always has exactly one slot with a token present.
"""

from .exceptions import TokenNotPresent
from .token import MockToken


class MockSlot:
    """Simulates a single smartcard reader slot.

    # REAL_SDK: Replaces python-pkcs11 Slot objects returned by lib.get_slots().
    # Real slot info comes from C_GetSlotInfo.
    """

    def __init__(self, slot_id: int = 0, token: MockToken | None = None):
        """
        # REAL_SDK: Slot IDs are assigned by the PKCS#11 middleware based on
        # detected readers (USB, built-in, etc.).
        """
        self.slot_id = slot_id
        self._token = token

    def get_token(self) -> MockToken:
        """Get the token (card) in this slot.

        # REAL_SDK: Accesses token info via C_GetTokenInfo(slotID).
        # Raises TokenNotPresent if no card is inserted.
        """
        if self._token is None:
            raise TokenNotPresent("No token in slot — insert a smartcard")
        return self._token

    def insert_token(self, token: MockToken):
        """Simulate inserting a card into the reader.

        # REAL_SDK: No API equivalent — this is a physical action. The
        # middleware detects insertion via PC/SC events.
        """
        self._token = token

    def remove_token(self):
        """Simulate removing the card.

        # REAL_SDK: Physical card removal. Triggers CKR_DEVICE_REMOVED
        # for any open sessions.
        """
        self._token = None

    @property
    def has_token(self) -> bool:
        return self._token is not None

    def get_info(self) -> dict:
        """Return slot metadata.

        # REAL_SDK: C_GetSlotInfo(slotID) — returns CK_SLOT_INFO struct.
        """
        return {
            "slot_id": self.slot_id,
            "description": "Mock SafeSign Virtual Reader",
            "has_token": self.has_token,
        }
