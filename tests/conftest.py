"""Root-level fixtures shared across all test modules."""

import pytest
from safesign_mock import MockPKCS11Library, MockToken, MockSlot, TokenStore


# ---------- SafeSign Mock Fixtures ----------

@pytest.fixture
def token_store():
    """Fresh empty TokenStore for each test."""
    return TokenStore()


@pytest.fixture
def token():
    """Fresh MockToken with default PIN '1234'."""
    return MockToken(label="TestToken")


@pytest.fixture
def rw_session(token):
    """Opened read-write session on a fresh token (PIN authenticated)."""
    return token.open(rw=True, user_pin="1234")


@pytest.fixture
def session_with_keypair(rw_session):
    """Session with a pre-generated RSA 2048 keypair. Returns (session, pub_h, priv_h)."""
    pub_h, priv_h = rw_session.generate_keypair(label="test-key")
    return rw_session, pub_h, priv_h


@pytest.fixture
def session_with_cert(session_with_keypair):
    """Session with keypair AND self-signed cert. Returns (session, pub_h, priv_h, cert_h)."""
    session, pub_h, priv_h = session_with_keypair
    cert_h = session.create_self_signed_cert(priv_h, pub_h, label="test-key")
    return session, pub_h, priv_h, cert_h


@pytest.fixture
def pkcs11_library():
    """Fresh MockPKCS11Library instance."""
    return MockPKCS11Library()


@pytest.fixture
def empty_slot():
    """MockSlot with no token inserted."""
    return MockSlot(slot_id=99)


@pytest.fixture
def slot_with_token(token):
    """MockSlot with a token inserted."""
    return MockSlot(slot_id=0, token=token)


# ---------- Signing Service (Flask test client) ----------

@pytest.fixture
def signing_app():
    """Flask app with bootstrap completed (key pair + cert generated)."""
    import signing_service
    signing_service.lib = MockPKCS11Library()
    signing_service.token = signing_service.lib.get_token()
    signing_service._bootstrap()
    signing_service.app.config["TESTING"] = True
    return signing_service.app


@pytest.fixture
def client(signing_app):
    """Flask test client for signing_service."""
    return signing_app.test_client()


# ---------- HL7 v3 Builder Fixtures ----------

@pytest.fixture
def hl7_builder():
    """A minimally configured HL7v3MessageBuilder (interaction + sender + receiver)."""
    from hl7v3_builder import HL7v3MessageBuilder, InteractionType
    return (
        HL7v3MessageBuilder()
        .set_interaction(InteractionType.PRPA_IN201305UV02)
        .set_sender(asid="TEST-SENDER")
        .set_receiver(asid="TEST-RECEIVER")
    )


@pytest.fixture
def hl7_message(hl7_builder):
    """A built HL7v3Message from the minimal builder."""
    return hl7_builder.build()


# ---------- FHIR Builder Fixtures ----------

@pytest.fixture
def fhir_patient_element():
    """A pre-built FHIR Patient resource element."""
    from fhir_builder.resources import patient
    return patient(
        nhs_number="9999999999",
        family_name="Smith",
        given_name="John",
        birth_date="1980-01-15",
        gender="male",
    )


@pytest.fixture
def fhir_message_header_element():
    """A pre-built FHIR MessageHeader resource element."""
    from fhir_builder.resources import message_header
    return message_header(
        event_system="https://fhir.nhs.uk/MessageEvent",
        event_code="prescription-order",
        source_endpoint="https://test-system.nhs.uk",
    )


@pytest.fixture
def fhir_searchset_builder(fhir_patient_element):
    """A FHIRBundleBuilder configured as searchset with one Patient entry."""
    from fhir_builder import FHIRBundleBuilder, BundleType
    return (
        FHIRBundleBuilder()
        .set_type(BundleType.SEARCHSET)
        .set_timestamp()
        .add_entry(fhir_patient_element, search_mode="match")
    )
