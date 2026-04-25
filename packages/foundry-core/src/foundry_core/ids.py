"""ID helpers. Foundry uses UUIDv7 strings for public-facing IDs."""

from __future__ import annotations

import time
import uuid
from secrets import token_bytes


def uuid7() -> str:
    """Generate a UUIDv7 (time-ordered, lexicographically sortable).

    Python's stdlib doesn't ship uuid7 until a later release. We implement
    RFC 9562 §5.7 manually so IDs remain sortable even without a DB dependency.
    """

    ts_ms = int(time.time() * 1000)
    rand = token_bytes(10)
    b = bytearray(16)
    b[0] = (ts_ms >> 40) & 0xFF
    b[1] = (ts_ms >> 32) & 0xFF
    b[2] = (ts_ms >> 24) & 0xFF
    b[3] = (ts_ms >> 16) & 0xFF
    b[4] = (ts_ms >> 8) & 0xFF
    b[5] = ts_ms & 0xFF
    b[6] = 0x70 | (rand[0] & 0x0F)
    b[7] = rand[1]
    b[8] = 0x80 | (rand[2] & 0x3F)
    b[9:16] = rand[3:10]
    return str(uuid.UUID(bytes=bytes(b)))
