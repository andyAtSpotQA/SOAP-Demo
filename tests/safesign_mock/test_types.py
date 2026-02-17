"""Tests for safesign_mock.types — PKCS#11 enumerations."""

from safesign_mock import ObjectClass, KeyType, Mechanism, CertificateType, TokenFlag


class TestObjectClass:
    def test_public_key_value(self):
        assert ObjectClass.PUBLIC_KEY == 0x02

    def test_private_key_value(self):
        assert ObjectClass.PRIVATE_KEY == 0x03

    def test_certificate_value(self):
        assert ObjectClass.CERTIFICATE == 0x01

    def test_secret_key_value(self):
        assert ObjectClass.SECRET_KEY == 0x04

    def test_data_value(self):
        assert ObjectClass.DATA == 0x00

    def test_is_int(self):
        assert isinstance(ObjectClass.PUBLIC_KEY, int)


class TestKeyType:
    def test_rsa_value(self):
        assert KeyType.RSA == 0x00

    def test_ec_value(self):
        assert KeyType.EC == 0x03

    def test_aes_value(self):
        assert KeyType.AES == 0x1F


class TestMechanism:
    def test_sha256_rsa_pkcs_value(self):
        assert Mechanism.SHA256_RSA_PKCS == 0x00000040

    def test_sha1_rsa_pkcs_value(self):
        assert Mechanism.SHA1_RSA_PKCS == 0x00000006

    def test_rsa_pkcs_value(self):
        assert Mechanism.RSA_PKCS == 0x00000001


class TestCertificateType:
    def test_x509_value(self):
        assert CertificateType.X_509 == 0x00


class TestTokenFlag:
    def test_rng_value(self):
        assert TokenFlag.RNG == 0x00000001

    def test_login_required_value(self):
        assert TokenFlag.LOGIN_REQUIRED == 0x00000004

    def test_token_initialized_value(self):
        assert TokenFlag.TOKEN_INITIALIZED == 0x00000020

    def test_user_pin_initialized_value(self):
        assert TokenFlag.USER_PIN_INITIALIZED == 0x00000040
