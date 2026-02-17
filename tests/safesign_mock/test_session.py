"""Tests for safesign_mock.session.MockSession — core crypto operations."""

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from safesign_mock import (
    ObjectClass, KeyType, Mechanism, CertificateType,
    SessionClosed, ObjectNotFound, MechanismInvalid,
)


class TestGenerateKeypair:
    def test_returns_two_integer_handles(self, rw_session):
        pub_h, priv_h = rw_session.generate_keypair()
        assert isinstance(pub_h, int) and isinstance(priv_h, int)

    def test_default_label_is_default(self, rw_session):
        pub_h, _ = rw_session.generate_keypair()
        obj = rw_session._store.get(pub_h)
        assert obj["label"] == "default"

    def test_custom_label(self, rw_session):
        pub_h, _ = rw_session.generate_keypair(label="custom")
        obj = rw_session._store.get(pub_h)
        assert obj["label"] == "custom"

    def test_public_key_has_correct_class(self, rw_session):
        pub_h, _ = rw_session.generate_keypair()
        assert rw_session._store.get(pub_h)["class"] == ObjectClass.PUBLIC_KEY

    def test_private_key_has_correct_class(self, rw_session):
        _, priv_h = rw_session.generate_keypair()
        assert rw_session._store.get(priv_h)["class"] == ObjectClass.PRIVATE_KEY

    def test_key_type_is_rsa(self, rw_session):
        pub_h, priv_h = rw_session.generate_keypair()
        assert rw_session._store.get(pub_h)["key_type"] == KeyType.RSA
        assert rw_session._store.get(priv_h)["key_type"] == KeyType.RSA

    def test_non_rsa_key_type_raises_mechanism_invalid(self, rw_session):
        with pytest.raises(MechanismInvalid):
            rw_session.generate_keypair(key_type=KeyType.EC)

    def test_closed_session_raises_session_closed(self, rw_session):
        rw_session.close()
        with pytest.raises(SessionClosed):
            rw_session.generate_keypair()


class TestSign:
    def test_sign_returns_bytes(self, session_with_keypair):
        session, _, priv_h = session_with_keypair
        sig = session.sign(priv_h, b"hello")
        assert isinstance(sig, bytes)

    def test_sign_sha256_rsa_pkcs_verifiable(self, session_with_keypair):
        session, pub_h, priv_h = session_with_keypair
        data = b"test data for signing"
        sig = session.sign(priv_h, data, Mechanism.SHA256_RSA_PKCS)
        public_key = session._store.get(pub_h)["key"]
        # Should not raise
        public_key.verify(sig, data, padding.PKCS1v15(), hashes.SHA256())

    def test_sign_sha1_rsa_pkcs(self, session_with_keypair):
        session, _, priv_h = session_with_keypair
        sig = session.sign(priv_h, b"data", Mechanism.SHA1_RSA_PKCS)
        assert isinstance(sig, bytes) and len(sig) > 0

    def test_sign_invalid_handle_raises_object_not_found(self, rw_session):
        with pytest.raises(ObjectNotFound):
            rw_session.sign(999, b"data")

    def test_sign_public_key_handle_raises_object_not_found(self, session_with_keypair):
        session, pub_h, _ = session_with_keypair
        with pytest.raises(ObjectNotFound):
            session.sign(pub_h, b"data")

    def test_sign_closed_session_raises(self, session_with_keypair):
        session, _, priv_h = session_with_keypair
        session.close()
        with pytest.raises(SessionClosed):
            session.sign(priv_h, b"data")

    def test_sign_different_data_produces_different_signatures(self, session_with_keypair):
        session, _, priv_h = session_with_keypair
        sig1 = session.sign(priv_h, b"hello")
        sig2 = session.sign(priv_h, b"world")
        assert sig1 != sig2


class TestCreateSelfSignedCert:
    def test_returns_integer_handle(self, session_with_keypair):
        session, pub_h, priv_h = session_with_keypair
        cert_h = session.create_self_signed_cert(priv_h, pub_h)
        assert isinstance(cert_h, int)

    def test_certificate_is_x509(self, session_with_cert):
        session, _, _, cert_h = session_with_cert
        obj = session._store.get(cert_h)
        assert obj["certificate_type"] == CertificateType.X_509

    def test_certificate_custom_cn(self, session_with_keypair):
        session, pub_h, priv_h = session_with_keypair
        cert_h = session.create_self_signed_cert(
            priv_h, pub_h, subject_cn="Custom CN",
        )
        obj = session._store.get(cert_h)
        assert obj["subject_cn"] == "Custom CN"

    def test_certificate_default_cn(self, session_with_keypair):
        session, pub_h, priv_h = session_with_keypair
        cert_h = session.create_self_signed_cert(priv_h, pub_h)
        obj = session._store.get(cert_h)
        assert obj["subject_cn"] == "Mock SafeSign User"

    def test_invalid_key_handles_raise_object_not_found(self, rw_session):
        with pytest.raises(ObjectNotFound):
            rw_session.create_self_signed_cert(999, 998)

    def test_closed_session_raises(self, session_with_keypair):
        session, pub_h, priv_h = session_with_keypair
        session.close()
        with pytest.raises(SessionClosed):
            session.create_self_signed_cert(priv_h, pub_h)


class TestGetCertificate:
    def test_get_certificate_returns_handle_and_dict(self, session_with_cert):
        session, _, _, _ = session_with_cert
        handle, obj = session.get_certificate(label="test-key")
        assert isinstance(handle, int)
        assert isinstance(obj, dict)

    def test_get_certificate_missing_label_raises(self, rw_session):
        with pytest.raises(ObjectNotFound):
            rw_session.get_certificate(label="nonexistent")

    def test_closed_session_raises(self, session_with_cert):
        session, _, _, _ = session_with_cert
        session.close()
        with pytest.raises(SessionClosed):
            session.get_certificate()


class TestFindObjects:
    def test_find_objects_by_class(self, session_with_keypair):
        session, _, _ = session_with_keypair
        results = session.find_objects(**{"class": ObjectClass.PUBLIC_KEY})
        assert len(results) == 1

    def test_find_objects_by_label(self, session_with_keypair):
        session, _, _ = session_with_keypair
        results = session.find_objects(label="test-key")
        assert len(results) == 2  # pub + priv

    def test_find_objects_empty_result(self, rw_session):
        assert rw_session.find_objects(label="nonexistent") == []

    def test_closed_session_raises(self, rw_session):
        rw_session.close()
        with pytest.raises(SessionClosed):
            rw_session.find_objects()


class TestContextManager:
    def test_context_manager_closes_session(self, token):
        with token.open(user_pin="1234") as session:
            session.generate_keypair()
        with pytest.raises(SessionClosed):
            session.generate_keypair()

    def test_operations_fail_after_context_exit(self, token):
        session = token.open(user_pin="1234")
        session.__enter__()
        session.__exit__(None, None, None)
        with pytest.raises(SessionClosed):
            session.generate_keypair()
