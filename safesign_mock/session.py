"""
Mock PKCS#11 session — core crypto operations.

# REAL_SDK: A PKCS#11 session (C_OpenSession) is the context for all
# cryptographic operations on a token. On a real SafeSign card, key generation
# happens on-chip and private keys never leave the card. Here we use the
# `cryptography` library to do the same operations in software.
"""

import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.x509 import (
    CertificateBuilder,
    NameAttribute,
    random_serial_number,
)
from cryptography.x509.oid import NameOID

from .types import ObjectClass, KeyType, Mechanism, CertificateType
from .exceptions import (
    SessionClosed,
    ObjectNotFound,
    MechanismInvalid,
    UserNotLoggedIn,
)
from .token_store import TokenStore


# Map our Mechanism enum to cryptography padding/hash combos
_MECHANISM_MAP = {
    Mechanism.SHA256_RSA_PKCS: (hashes.SHA256(), False),
    Mechanism.SHA1_RSA_PKCS: (hashes.SHA1(), False),
    Mechanism.RSA_PKCS: (None, True),  # raw PKCS1v15 — data is pre-hashed
}


class MockSession:
    """A mock PKCS#11 session providing real RSA crypto with in-memory keys.

    # REAL_SDK: Replaces the session object returned by Token.open() in
    # python-pkcs11. Real sessions send APDU commands to the card for every
    # crypto op; this mock does the math in software instead.
    """

    def __init__(self, store: TokenStore, rw: bool = True):
        """
        # REAL_SDK: C_OpenSession(slotID, flags) — opens a session to the token.
        The `rw` flag maps to CKF_RW_SESSION.
        """
        self._store = store
        self._rw = rw
        self._open = True

    def _check_open(self):
        if not self._open:
            raise SessionClosed("Session has been closed")

    def close(self):
        """Close this session.

        # REAL_SDK: C_CloseSession(hSession)
        """
        self._open = False

    def generate_keypair(
        self,
        key_type: KeyType = KeyType.RSA,
        key_size: int = 2048,
        label: str = "default",
    ) -> tuple[int, int]:
        """Generate an RSA key pair, store both halves, return (pub_handle, priv_handle).

        # REAL_SDK: C_GenerateKeyPair(hSession, mechanism, pubTemplate, privTemplate)
        # On a real SafeSign card this generates the key ON the card — the private
        # key never leaves the secure element. Here we generate in software.
        """
        self._check_open()

        if key_type != KeyType.RSA:
            raise MechanismInvalid(f"Key type {key_type} not supported in mock")

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        public_key = private_key.public_key()

        pub_handle = self._store.store({
            "class": ObjectClass.PUBLIC_KEY,
            "key_type": KeyType.RSA,
            "label": label,
            "key": public_key,
        })

        priv_handle = self._store.store({
            "class": ObjectClass.PRIVATE_KEY,
            "key_type": KeyType.RSA,
            "label": label,
            "key": private_key,
        })

        return pub_handle, priv_handle

    def sign(
        self,
        private_key_handle: int,
        data: bytes,
        mechanism: Mechanism = Mechanism.SHA256_RSA_PKCS,
    ) -> bytes:
        """Sign data using a private key stored in the token.

        # REAL_SDK: C_SignInit(hSession, mechanism, hKey) + C_Sign(hSession, data)
        # On a real card the data is sent to the card and the signature comes back;
        # the private key bits never leave the secure element.
        """
        self._check_open()

        obj = self._store.get(private_key_handle)
        if obj is None or obj["class"] != ObjectClass.PRIVATE_KEY:
            raise ObjectNotFound(f"Private key handle {private_key_handle} not found")

        if mechanism not in _MECHANISM_MAP:
            raise MechanismInvalid(f"Mechanism {mechanism} not supported")

        hash_algo, is_raw = _MECHANISM_MAP[mechanism]
        private_key = obj["key"]

        if is_raw:
            # Raw PKCS1v15 — caller already hashed the data
            signature = private_key.sign(data, padding.PKCS1v15(), utils.Prehashed(hashes.SHA256()))
        else:
            signature = private_key.sign(data, padding.PKCS1v15(), hash_algo)

        return signature

    def create_self_signed_cert(
        self,
        private_key_handle: int,
        public_key_handle: int,
        subject_cn: str = "Mock SafeSign User",
        validity_days: int = 365,
        label: str = "default",
    ) -> int:
        """Create a self-signed X.509 certificate and store it on the token.

        # REAL_SDK: In real PKI, you'd generate a CSR (PKCS#10) on the card,
        # send it to a CA, and import the issued certificate back via
        # C_CreateObject. This convenience method creates a self-signed cert
        # for demo/testing purposes.
        """
        self._check_open()

        priv_obj = self._store.get(private_key_handle)
        pub_obj = self._store.get(public_key_handle)
        if priv_obj is None or pub_obj is None:
            raise ObjectNotFound("Key pair not found")

        private_key = priv_obj["key"]
        public_key = pub_obj["key"]

        now = datetime.datetime.now(datetime.timezone.utc)
        subject = issuer = [
            NameAttribute(NameOID.COMMON_NAME, subject_cn),
            NameAttribute(NameOID.ORGANIZATION_NAME, "Mock SafeSign Demo"),
            NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ]

        from cryptography.x509 import Name
        cert = (
            CertificateBuilder()
            .subject_name(Name(subject))
            .issuer_name(Name(issuer))
            .public_key(public_key)
            .serial_number(random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=validity_days))
            .sign(private_key, hashes.SHA256())
        )

        cert_handle = self._store.store({
            "class": ObjectClass.CERTIFICATE,
            "certificate_type": CertificateType.X_509,
            "label": label,
            "value": cert,
            "subject_cn": subject_cn,
        })

        return cert_handle

    def get_certificate(self, label: str = "default"):
        """Find a certificate by label.

        # REAL_SDK: C_FindObjects with CKA_CLASS=CKO_CERTIFICATE template.
        """
        self._check_open()
        results = self._store.find(**{"class": ObjectClass.CERTIFICATE, "label": label})
        if not results:
            raise ObjectNotFound(f"Certificate with label '{label}' not found")
        return results[0]  # (handle, obj_dict)

    def find_objects(self, **attrs) -> list[tuple[int, dict]]:
        """Generic object search.

        # REAL_SDK: C_FindObjectsInit/C_FindObjects/C_FindObjectsFinal
        """
        self._check_open()
        return self._store.find(**attrs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
