"""
PKCS#11 exception hierarchy for the mock SafeSign SDK.

# REAL_SDK: These mirror exceptions from python-pkcs11 (pkcs11.exceptions).
# In a real SafeSign integration, the PKCS#11 middleware raises these when
# the smartcard/reader reports an error condition.
"""


class PKCS11Error(Exception):
    """Base exception for all PKCS#11 errors.

    # REAL_SDK: pkcs11.exceptions.PKCS11Error
    """


class PinIncorrect(PKCS11Error):
    """Wrong PIN supplied during login.

    # REAL_SDK: pkcs11.exceptions.PinIncorrect (CKR_PIN_INCORRECT)
    """


class PinLocked(PKCS11Error):
    """PIN retry counter exhausted — token is locked.

    # REAL_SDK: pkcs11.exceptions.PinLocked (CKR_PIN_LOCKED)
    """


class SessionClosed(PKCS11Error):
    """Operation attempted on a closed session.

    # REAL_SDK: pkcs11.exceptions.SessionClosed (CKR_SESSION_CLOSED)
    """


class TokenNotPresent(PKCS11Error):
    """No smartcard inserted in the reader slot.

    # REAL_SDK: pkcs11.exceptions.TokenNotPresent (CKR_TOKEN_NOT_PRESENT)
    """


class ObjectNotFound(PKCS11Error):
    """Requested object (key, cert) not found on the token.

    # REAL_SDK: maps to CKR_OBJECT_HANDLE_INVALID or empty search results
    """


class MechanismInvalid(PKCS11Error):
    """Unsupported or invalid signing mechanism requested.

    # REAL_SDK: pkcs11.exceptions.MechanismInvalid (CKR_MECHANISM_INVALID)
    """


class UserNotLoggedIn(PKCS11Error):
    """Crypto operation attempted without prior PIN login.

    # REAL_SDK: pkcs11.exceptions.UserNotLoggedIn (CKR_USER_NOT_LOGGED_IN)
    """
