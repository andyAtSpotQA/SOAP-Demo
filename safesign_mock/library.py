"""
Mock PKCS#11 library — entry point replacing pkcs11.lib().

# REAL_SDK: In a real SafeSign integration, the entry point is:
#   import pkcs11
#   lib = pkcs11.lib("/usr/lib/libaetpkss.so")  # or .dll on Windows
# This loads the PKCS#11 shared library provided by SafeSign.
# Our mock replaces that with a pure-Python object.
"""

from .slot import MockSlot
from .token import MockToken
from .exceptions import TokenNotPresent


class MockPKCS11Library:
    """Entry point for the mock PKCS#11 library.

    # REAL_SDK: Replaces the object returned by pkcs11.lib("/path/to/libaetpkss.so").
    # The real library calls C_Initialize on load and C_Finalize on cleanup.

    Usage (mirrors real python-pkcs11 API):
        lib = MockPKCS11Library()
        token = lib.get_token(token_label="MockSafeSign")
        session = token.open(rw=True, user_pin="1234")
    """

    def __init__(self):
        """
        # REAL_SDK: Equivalent to pkcs11.lib(path) which calls C_Initialize.
        """
        # Start with one slot containing a default token
        default_token = MockToken(label="MockSafeSign")
        self._slots = [MockSlot(slot_id=0, token=default_token)]

    def get_slots(self) -> list[MockSlot]:
        """List all available card reader slots.

        # REAL_SDK: C_GetSlotList(tokenPresent=False)
        """
        return list(self._slots)

    def get_token(self, token_label: str | None = None) -> MockToken:
        """Find a token by label (convenience method).

        # REAL_SDK: Iterates slots via C_GetSlotList(tokenPresent=True),
        # then C_GetTokenInfo on each to match the label.
        """
        for slot in self._slots:
            if slot.has_token:
                token = slot.get_token()
                if token_label is None or token.label == token_label:
                    return token
        raise TokenNotPresent(
            f"No token found with label '{token_label}'"
            if token_label
            else "No token found in any slot"
        )

    def add_slot(self, slot: MockSlot):
        """Add an additional reader slot (for testing multi-reader setups).

        # REAL_SDK: No equivalent — physical readers are detected by PC/SC.
        """
        self._slots.append(slot)

    def get_info(self) -> dict:
        """Library and slot summary.

        # REAL_SDK: C_GetInfo — returns CK_INFO with library version etc.
        """
        return {
            "library": "MockPKCS11 (SafeSign SDK simulator)",
            "version": "1.0.0",
            "slots": [s.get_info() for s in self._slots],
        }
