"""
Fluent FHIR Bundle builder and immutable result class.

# FHIR_SPEC: A Bundle is a container for a collection of resources.
# Bundle types include message (inter-system messaging), transaction
# (atomic REST operations), searchset (search results), and others.
# The builder validates structural rules before producing the Bundle.

Usage:
    bundle = (
        FHIRBundleBuilder()
        .set_type(BundleType.MESSAGE)
        .add_entry(message_header_element)
        .add_entry(patient_element)
        .build()
    )
    print(bundle.to_xml())
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from lxml import etree

from .datatypes import FHIR_NS, NSMAP, _fhir_sub, meta
from .exceptions import ValidationError, SerializationError
from .types import BundleType, ResourceType


@dataclass
class _BundleEntry:
    """Internal representation of a Bundle entry before assembly."""
    resource: etree._Element
    full_url: str | None = None
    request_method: str | None = None
    request_url: str | None = None
    search_mode: str | None = None


class FHIRBundleBuilder:
    """Fluent builder for FHIR R4 Bundles.

    # FHIR_SPEC: Bundles group resources for transport. The builder
    # enforces structural constraints:
    #   - Message bundles must start with a MessageHeader entry
    #   - Transaction entries must have request method + URL
    #   - All bundles must have a type and at least one entry
    """

    def __init__(self):
        self._id: str = str(uuid.uuid4())
        self._type: BundleType | None = None
        self._timestamp: str | None = None
        self._total: int | None = None
        self._profile: str | None = None
        self._entries: list[_BundleEntry] = []

    def set_id(self, bundle_id: str) -> FHIRBundleBuilder:
        """Override the auto-generated bundle ID."""
        self._id = bundle_id
        return self

    def set_type(self, bundle_type: BundleType) -> FHIRBundleBuilder:
        """Set the Bundle type (message, transaction, searchset, etc.).

        # FHIR_SPEC: Bundle.type is required and determines structural rules.
        """
        self._type = bundle_type
        return self

    def set_timestamp(self, ts: str | datetime | None = None) -> FHIRBundleBuilder:
        """Set the Bundle timestamp. Defaults to now (UTC) if None."""
        if ts is None:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        elif isinstance(ts, datetime):
            ts = ts.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        self._timestamp = ts
        return self

    def set_total(self, total: int) -> FHIRBundleBuilder:
        """Set Bundle.total (used in searchset bundles)."""
        self._total = total
        return self

    def set_profile(self, profile_url: str) -> FHIRBundleBuilder:
        """Set a profile URL in the Bundle's meta element."""
        self._profile = profile_url
        return self

    def add_entry(
        self,
        resource: etree._Element,
        full_url: str | None = None,
        request_method: str | None = None,
        request_url: str | None = None,
        search_mode: str | None = None,
    ) -> FHIRBundleBuilder:
        """Add a resource entry to the Bundle.

        # FHIR_SPEC: Each entry has a fullUrl (unique within the bundle),
        # the resource itself, and optional request/search metadata.
        # fullUrl defaults to urn:uuid:{resource.id} if not provided.

        Args:
            resource: FHIR resource element (from resources.py factories).
            full_url: Override the auto-generated fullUrl.
            request_method: HTTP method for transaction/batch entries.
            request_url: Request URL for transaction/batch entries.
            search_mode: Search mode (match/include) for searchset entries.
        """
        self._entries.append(_BundleEntry(
            resource=resource,
            full_url=full_url,
            request_method=request_method,
            request_url=request_url,
            search_mode=search_mode,
        ))
        return self

    def validate(self) -> list[str]:
        """Validate the builder state and return any error messages.

        # FHIR_SPEC: Structural validation rules:
        # - Bundle.type is required
        # - At least one entry is required
        # - Message bundles: first entry must be MessageHeader
        # - Transaction/batch entries: request.method and request.url required
        """
        errors = []

        if self._type is None:
            errors.append("Bundle type is required")

        if not self._entries:
            errors.append("Bundle must have at least one entry")

        if self._type == BundleType.MESSAGE and self._entries:
            first_tag = etree.QName(self._entries[0].resource.tag).localname
            if first_tag != ResourceType.MESSAGE_HEADER.value:
                errors.append(
                    "Message bundle must start with a MessageHeader entry"
                )

        if self._type in (BundleType.TRANSACTION, BundleType.BATCH):
            for i, entry in enumerate(self._entries):
                if not entry.request_method or not entry.request_url:
                    errors.append(
                        f"Entry {i}: transaction/batch entries require "
                        f"request_method and request_url"
                    )

        return errors

    def build(self) -> FHIRBundle:
        """Validate and assemble the Bundle.

        Returns:
            An immutable FHIRBundle instance.

        Raises:
            ValidationError: If validation fails.
        """
        errors = self.validate()
        if errors:
            raise ValidationError("; ".join(errors))

        # Build the Bundle element
        root = etree.Element(f"{{{FHIR_NS}}}Bundle", nsmap=NSMAP)
        _fhir_sub(root, "id", value=self._id)

        if self._profile:
            root.append(meta(profile=self._profile))

        _fhir_sub(root, "type", value=self._type.value)

        if self._timestamp:
            _fhir_sub(root, "timestamp", value=self._timestamp)

        if self._total is not None:
            _fhir_sub(root, "total", value=str(self._total))

        for entry_data in self._entries:
            entry_el = _fhir_sub(root, "entry")

            # Resolve fullUrl
            full_url = entry_data.full_url
            if not full_url:
                id_el = entry_data.resource.find(f"{{{FHIR_NS}}}id")
                if id_el is not None:
                    full_url = f"urn:uuid:{id_el.get('value')}"
            if full_url:
                _fhir_sub(entry_el, "fullUrl", value=full_url)

            resource_el = _fhir_sub(entry_el, "resource")
            resource_el.append(entry_data.resource)

            if entry_data.request_method and entry_data.request_url:
                request_el = _fhir_sub(entry_el, "request")
                _fhir_sub(request_el, "method", value=entry_data.request_method)
                _fhir_sub(request_el, "url", value=entry_data.request_url)

            if entry_data.search_mode:
                search_el = _fhir_sub(entry_el, "search")
                _fhir_sub(search_el, "mode", value=entry_data.search_mode)

        return FHIRBundle(root, self._id, self._type)


class FHIRBundle:
    """Immutable result of FHIRBundleBuilder.build().

    # FHIR_SPEC: Mirrors HL7v3Message — provides serialization to XML
    # string or raw lxml Element for further processing (e.g. signing).
    """

    def __init__(
        self,
        root: etree._Element,
        bundle_id: str,
        bundle_type: BundleType,
    ):
        self._root = root
        self._bundle_id = bundle_id
        self._bundle_type = bundle_type

    @property
    def root(self) -> etree._Element:
        return self._root

    @property
    def bundle_id(self) -> str:
        return self._bundle_id

    @property
    def bundle_type(self) -> BundleType:
        return self._bundle_type

    def to_xml(self, pretty_print: bool = True) -> str:
        """Serialize the Bundle to an XML string.

        # FHIR_SPEC: FHIR XML uses UTF-8 encoding with an XML declaration.
        """
        try:
            return etree.tostring(
                self._root,
                pretty_print=pretty_print,
                xml_declaration=True,
                encoding="UTF-8",
            ).decode("utf-8")
        except Exception as e:
            raise SerializationError(f"Failed to serialize Bundle: {e}")

    def to_element(self) -> etree._Element:
        """Return the raw lxml Element (e.g. for signing or embedding)."""
        return self._root
