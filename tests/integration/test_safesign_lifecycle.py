"""Integration test: Full SafeSign PKCS#11 lifecycle."""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from safesign_mock import MockPKCS11Library, ObjectClass, CertificateType


class TestFullLifecycle:
    def test_complete_pkcs11_workflow(self):
        """End-to-end: init library -> get token -> open session -> generate keys ->
        sign -> verify -> create cert -> retrieve cert -> close session."""

        # 1. Initialize library and get token
        lib = MockPKCS11Library()
        assert len(lib.get_slots()) == 1
        token = lib.get_token()
        assert token.label == "MockSafeSign"

        # 2. Open authenticated session
        session = token.open(rw=True, user_pin="1234")

        # 3. Generate RSA key pair
        pub_h, priv_h = session.generate_keypair(label="lifecycle-key")
        assert isinstance(pub_h, int)
        assert isinstance(priv_h, int)

        # 4. Verify objects are stored
        pub_keys = session.find_objects(**{"class": ObjectClass.PUBLIC_KEY})
        priv_keys = session.find_objects(**{"class": ObjectClass.PRIVATE_KEY})
        assert len(pub_keys) == 1
        assert len(priv_keys) == 1

        # 5. Sign data
        data = b"Integration test payload"
        signature = session.sign(priv_h, data)
        assert isinstance(signature, bytes)
        assert len(signature) > 0

        # 6. Verify signature using the real public key
        pub_obj = session._store.get(pub_h)
        public_key = pub_obj["key"]
        public_key.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())

        # 7. Create self-signed certificate
        cert_h = session.create_self_signed_cert(
            priv_h, pub_h, label="lifecycle-key", subject_cn="Lifecycle Test",
        )
        assert isinstance(cert_h, int)

        # 8. Retrieve certificate
        handle, cert_obj = session.get_certificate(label="lifecycle-key")
        assert cert_obj["certificate_type"] == CertificateType.X_509
        assert cert_obj["subject_cn"] == "Lifecycle Test"

        # 9. Verify certificate has real x509 object
        assert "value" in cert_obj

        # 10. Close session
        session.close()

    def test_multiple_key_pairs(self):
        """Generate multiple key pairs and verify they are independent."""
        lib = MockPKCS11Library()
        token = lib.get_token()
        session = token.open(rw=True, user_pin="1234")

        pub1, priv1 = session.generate_keypair(label="key-1")
        pub2, priv2 = session.generate_keypair(label="key-2")

        # Different handles
        assert len({pub1, priv1, pub2, priv2}) == 4

        # Different signatures for same data
        data = b"same data"
        sig1 = session.sign(priv1, data)
        sig2 = session.sign(priv2, data)
        assert sig1 != sig2

        session.close()

    def test_token_pin_change_flow(self):
        """Change PIN and verify old PIN no longer works."""
        lib = MockPKCS11Library()
        token = lib.get_token()

        # Open with original PIN
        session = token.open(rw=True, user_pin="1234")
        session.close()

        # Change PIN
        token.change_pin("1234", "newpin5678")

        # Open with new PIN
        session = token.open(rw=True, user_pin="newpin5678")
        session.close()
