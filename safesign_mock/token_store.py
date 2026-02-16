"""
In-memory object storage replacing smartcard EEPROM.

# REAL_SDK: On a real smartcard, keys and certificates are stored in the card's
# non-volatile memory (EEPROM/flash). The PKCS#11 middleware reads/writes
# objects via APDU commands to the card. This class replaces that with a
# plain Python dict keyed by integer handles.
"""

import threading
from .types import ObjectClass


class TokenStore:
    """Thread-safe in-memory store for PKCS#11 objects.

    Each object is a dict with at least:
      - 'class': ObjectClass enum value
      - 'label': str
      - ... type-specific fields (e.g. 'key' for keys, 'value' for certs)

    # REAL_SDK: Replaces the card's on-chip object store. In real PKCS#11,
    # C_CreateObject / C_FindObjects talk to the card over the reader.
    """

    def __init__(self):
        self._objects: dict[int, dict] = {}
        self._next_handle = 1
        self._lock = threading.Lock()

    def store(self, obj: dict) -> int:
        """Store an object and return its handle.

        # REAL_SDK: Equivalent to C_CreateObject — writes an object to the card.
        """
        with self._lock:
            handle = self._next_handle
            self._next_handle += 1
            self._objects[handle] = obj
            return handle

    def get(self, handle: int) -> dict | None:
        """Retrieve an object by handle.

        # REAL_SDK: Equivalent to C_GetAttributeValue — reads object attributes.
        """
        return self._objects.get(handle)

    def find(self, **attrs) -> list[tuple[int, dict]]:
        """Find objects matching all given attribute key-value pairs.

        # REAL_SDK: Equivalent to C_FindObjectsInit / C_FindObjects / C_FindObjectsFinal.
        """
        results = []
        for handle, obj in self._objects.items():
            if all(obj.get(k) == v for k, v in attrs.items()):
                results.append((handle, obj))
        return results

    def delete(self, handle: int) -> bool:
        """Remove an object by handle.

        # REAL_SDK: Equivalent to C_DestroyObject — erases object from card.
        """
        with self._lock:
            return self._objects.pop(handle, None) is not None

    def list_all(self) -> list[tuple[int, dict]]:
        """List all stored objects (for diagnostics).

        # REAL_SDK: No direct equivalent — you'd enumerate via C_FindObjects
        # with an empty template.
        """
        return list(self._objects.items())

    @property
    def count(self) -> int:
        return len(self._objects)
