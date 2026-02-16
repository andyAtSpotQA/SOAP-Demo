"""
Mock PKCS#11 token — PIN management and session factory.

# REAL_SDK: A PKCS#11 token represents the smartcard itself. The token
# manages the user PIN (and optional SO PIN), enforces retry limits, and
# creates sessions for crypto operations. On a real SafeSign card, PIN
# verification happens on-chip via APDU VERIFY commands.
"""

from .exceptions import PinIncorrect, PinLocked, UserNotLoggedIn
from .session import MockSession
from .token_store import TokenStore


class MockToken:
    """Simulates a PKCS#11 token (smartcard) with PIN auth.

    # REAL_SDK: Replaces the Token object from python-pkcs11.
    # Real token attributes come from C_GetTokenInfo.
    """

    DEFAULT_PIN = "1234"
    MAX_PIN_RETRIES = 3

    def __init__(self, label: str = "MockSafeSign", pin: str | None = None):
        """
        # REAL_SDK: Token info is read from the card via C_GetTokenInfo.
        # The label is set during card initialization (typically by the CA).
        """
        self.label = label
        self._pin = pin or self.DEFAULT_PIN
        self._pin_retries_left = self.MAX_PIN_RETRIES
        self._locked = False
        self._store = TokenStore()

    def open(self, rw: bool = True, user_pin: str | None = None) -> MockSession:
        """Authenticate with PIN and open a session.

        # REAL_SDK: C_OpenSession + C_Login(CKU_USER, pin).
        # On a real card, PIN verification happens in the card's secure CPU.
        # Three consecutive failures lock the card (requiring SO PIN or re-init).
        """
        if user_pin is not None:
            self._verify_pin(user_pin)
        return MockSession(self._store, rw=rw)

    def _verify_pin(self, pin: str):
        """Verify the user PIN, decrementing retry counter on failure.

        # REAL_SDK: Maps to the VERIFY APDU command sent to the card.
        """
        if self._locked:
            raise PinLocked("Token is locked — PIN retry counter exhausted")

        if pin != self._pin:
            self._pin_retries_left -= 1
            if self._pin_retries_left <= 0:
                self._locked = True
                raise PinLocked(
                    "Token is now locked — too many incorrect PIN attempts"
                )
            raise PinIncorrect(
                f"Incorrect PIN ({self._pin_retries_left} retries left)"
            )

        # Successful auth resets the counter
        self._pin_retries_left = self.MAX_PIN_RETRIES

    def change_pin(self, old_pin: str, new_pin: str):
        """Change the user PIN.

        # REAL_SDK: C_SetPIN(hSession, oldPin, newPin) — runs on-card.
        """
        self._verify_pin(old_pin)
        if len(new_pin) < 4:
            raise ValueError("PIN must be at least 4 characters")
        self._pin = new_pin

    @property
    def pin_retries_left(self) -> int:
        return self._pin_retries_left

    @property
    def is_locked(self) -> bool:
        return self._locked

    @property
    def store(self) -> TokenStore:
        return self._store

    def get_info(self) -> dict:
        """Return token metadata.

        # REAL_SDK: C_GetTokenInfo(slotID) — returns CK_TOKEN_INFO struct.
        """
        return {
            "label": self.label,
            "pin_retries_left": self._pin_retries_left,
            "is_locked": self._locked,
            "objects_stored": self._store.count,
        }
