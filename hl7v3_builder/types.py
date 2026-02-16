"""
HL7 v3 type enumerations for the message builder.

# HL7_SPEC: These mirror constants from the HL7 v3 Normative Edition and
# NHS Spine Message Implementation Guides (MIM). In a real integration
# you'd validate these against the published ITK/Spine specifications.
"""

from enum import Enum


class InteractionType(str, Enum):
    """HL7 v3 interaction identifiers used by NHS Spine.

    # HL7_SPEC: Each interaction ID maps to a specific message pattern
    # defined in the NHS Message Implementation Manual (MIM).
    # Format: DOMAIN_INNNNNNNVERSION (e.g. PRPA_IN201305UV02).
    """
    # Patient Demographics Query (PDQ)
    PRPA_IN201305UV02 = "PRPA_IN201305UV02"
    # Patient Demographics Query Response
    PRPA_IN201306UV02 = "PRPA_IN201306UV02"
    # Summary Care Record Query
    QUPC_IN160101UK05 = "QUPC_IN160101UK05"
    # GP Summary Upload
    REPC_IN150016UK05 = "REPC_IN150016UK05"
    # PDS Personal Demographics Service - Retrieval Query
    QUPA_IN040000UK32 = "QUPA_IN040000UK32"
    # PDS Personal Demographics Service - Trace Query
    QUPA_IN020000UK31 = "QUPA_IN020000UK31"


class ProcessingCode(str, Enum):
    """HL7 v3 processingCode values.

    # HL7_SPEC: Indicates whether the message is part of production,
    # training, or debugging traffic. Set via <processingCode code="X"/>.
    # See HL7 v3 vocabulary domain ProcessingID.
    """
    PRODUCTION = "P"
    TRAINING = "T"
    DEBUGGING = "D"


class ProcessingModeCode(str, Enum):
    """HL7 v3 processingModeCode values.

    # HL7_SPEC: Indicates the processing mode — current processing,
    # initial load, or restore from archive.
    # See HL7 v3 vocabulary domain ProcessingMode.
    """
    CURRENT = "T"
    INITIAL_LOAD = "I"
    RESTORE = "R"


class AckCode(str, Enum):
    """HL7 v3 acceptAckCode / applicationAckCode values.

    # HL7_SPEC: Controls whether the receiver must send an acknowledgement.
    # See HL7 v3 vocabulary domain AcknowledgementCondition.
    """
    ALWAYS = "AL"
    NEVER = "NE"
    ERROR_ONLY = "ER"


class ClassCode(str, Enum):
    """Common HL7 v3 classCode attribute values.

    # HL7_SPEC: Structural attribute on RIM Act/Entity/Role classes.
    # Determines which specialization of the base class is represented.
    """
    CONTROL_ACT = "CACT"
    PATIENT = "PAT"
    PERSON = "PSN"
    ORGANIZATION = "ORG"
    DEVICE = "DEV"
    ASSIGNED = "ASSIGNED"
    AGENT = "AGNT"


class MoodCode(str, Enum):
    """Common HL7 v3 moodCode attribute values.

    # HL7_SPEC: Indicates the mode of an Act — whether it is an event
    # that happened, a request, an intent, etc.
    """
    EVENT = "EVN"
    REQUEST = "RQO"
    DEFINITION = "DEF"
    INTENT = "INT"


class NHSOid(str, Enum):
    """Common NHS OIDs used in Spine messages.

    # HL7_SPEC: Object Identifiers from the NHS OID registry. These are
    # used in Instance Identifier (II) root attributes to identify the
    # assigning authority for various identifier types.
    """
    # Patient identifier — NHS Number
    NHS_NUMBER = "2.16.840.1.113883.2.1.4.1"
    # Spine interaction ID namespace
    SPINE_INTERACTION = "2.16.840.1.113883.2.1.3.2.4.12"
    # Spine message ID namespace
    SPINE_MESSAGE_ID = "2.16.840.1.113883.2.1.3.2.4.17"
    # GP practice ODS code namespace
    GP_ODS_CODE = "2.16.840.1.113883.2.1.3.2.4.19.1"
    # SDS User ID
    SDS_USER_ID = "1.2.826.0.1285.0.2.0.65"
    # SDS Role Profile ID
    SDS_ROLE_PROFILE = "1.2.826.0.1285.0.2.0.67"
    # SDS Job Role Code
    SDS_JOB_ROLE = "1.2.826.0.1285.0.2.1.104"
    # SNOMED CT
    SNOMED_CT = "2.16.840.1.113883.2.1.3.2.4.15"
    # Spine Accredited System Identifier (ASID)
    SPINE_ASID = "1.2.826.0.1285.0.2.0.107"
    # Spine URL service namespace
    SPINE_URL = "2.16.840.1.113883.2.1.3.2.4.18.16"
    # HL7 v3 processing code vocabulary
    PROCESSING_ID = "2.16.840.1.113883.5.7"
    # HL7 v3 processing mode vocabulary
    PROCESSING_MODE = "2.16.840.1.113883.5.101"
    # HL7 v3 acknowledgement condition vocabulary
    ACK_CONDITION = "2.16.840.1.113883.5.8"
