"""
Mock SafeSign SDK — a software simulation of PKCS#11 smartcard operations.

Provides the same object model as a real SafeSign/PKCS#11 integration:
  Library -> Slot -> Token -> Session -> crypto ops

All cryptography is real (RSA via `cryptography` lib); only key *storage*
is mocked (in-memory instead of smartcard hardware).

Usage:
    from safesign_mock import MockPKCS11Library

    lib = MockPKCS11Library()
    token = lib.get_token()
    session = token.open(rw=True, user_pin="1234")
    pub_h, priv_h = session.generate_keypair(label="mykey")
    sig = session.sign(priv_h, b"hello world")
"""

from .library import MockPKCS11Library
from .token import MockToken
from .session import MockSession
from .slot import MockSlot
from .token_store import TokenStore
from .types import ObjectClass, KeyType, Mechanism, CertificateType, TokenFlag
from .exceptions import (
    PKCS11Error,
    PinIncorrect,
    PinLocked,
    SessionClosed,
    TokenNotPresent,
    ObjectNotFound,
    MechanismInvalid,
    UserNotLoggedIn,
)

__all__ = [
    "MockPKCS11Library",
    "MockToken",
    "MockSession",
    "MockSlot",
    "TokenStore",
    "ObjectClass",
    "KeyType",
    "Mechanism",
    "CertificateType",
    "TokenFlag",
    "PKCS11Error",
    "PinIncorrect",
    "PinLocked",
    "SessionClosed",
    "TokenNotPresent",
    "ObjectNotFound",
    "MechanismInvalid",
    "UserNotLoggedIn",
]
