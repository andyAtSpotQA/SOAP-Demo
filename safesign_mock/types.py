"""
PKCS#11 type enumerations for the mock SafeSign SDK.

# REAL_SDK: These mirror the constants from the PKCS#11 spec (pkcs11.constants)
# that SafeSign's libaetpkss.so exposes. In a real integration you'd import
# them from the python-pkcs11 package: `from pkcs11 import ObjectClass, KeyType, ...`
"""

from enum import IntEnum


class ObjectClass(IntEnum):
    """PKCS#11 CKO_* object class constants."""
    # REAL_SDK: pkcs11.ObjectClass
    PUBLIC_KEY = 0x02
    PRIVATE_KEY = 0x03
    CERTIFICATE = 0x01
    SECRET_KEY = 0x04
    DATA = 0x00


class KeyType(IntEnum):
    """PKCS#11 CKK_* key type constants."""
    # REAL_SDK: pkcs11.KeyType
    RSA = 0x00
    EC = 0x03
    AES = 0x1F


class Mechanism(IntEnum):
    """PKCS#11 CKM_* mechanism constants used for signing."""
    # REAL_SDK: pkcs11.Mechanism — maps to CKM_SHA256_RSA_PKCS etc.
    SHA256_RSA_PKCS = 0x00000040
    SHA1_RSA_PKCS = 0x00000006
    RSA_PKCS = 0x00000001


class CertificateType(IntEnum):
    """PKCS#11 CKC_* certificate type constants."""
    # REAL_SDK: pkcs11.CertificateType
    X_509 = 0x00


class TokenFlag(IntEnum):
    """PKCS#11 CKF_* token information flags."""
    # REAL_SDK: pkcs11.TokenFlag
    RNG = 0x00000001
    LOGIN_REQUIRED = 0x00000004
    TOKEN_INITIALIZED = 0x00000020
    USER_PIN_INITIALIZED = 0x00000040
