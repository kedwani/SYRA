"""
Emergency data utilities - encode/decode embedded emergency data in URLs.
This allows critical info to be displayed even without server access.
"""

import json
import base64
import urllib.parse
from typing import Optional


def encode_emergency_data(
    public_id: str,
    blood_type: str,
    allergies: str = "",
    emergency_notes: str = "",
    medications: list = None,
) -> str:
    """
    Encode critical emergency data into a compact URL-safe string.

    Format: blood_type|allergies|emergency_notes|medication1;medication2

    This data is embedded in the QR code URL so basic emergency info
    can be displayed even if the server is slow or down.
    """
    if medications is None:
        medications = []

    # Create compact pipe-separated data
    parts = [
        public_id[:8],  # Short ID for verification
        blood_type or "Unknown",
        allergies[:100] if allergies else "None",  # Limit length
        emergency_notes[:100] if emergency_notes else "None",
        (
            ";".join([m[:30] for m in medications[:3]]) if medications else ""
        ),  # Max 3 meds, 30 chars each
    ]

    # Encode as base64 for URL safety
    data_str = "|".join(parts)
    encoded = base64.urlsafe_b64encode(data_str.encode("utf-8")).decode("utf-8")

    return encoded


def decode_emergency_data(encoded: str) -> Optional[dict]:
    """
    Decode emergency data from URL parameter.
    Returns dict with embedded data or None if invalid.
    """
    try:
        decoded = base64.urlsafe_b64decode(encoded.encode("utf-8")).decode("utf-8")
        parts = decoded.split("|")

        if len(parts) < 3:
            return None

        return {
            "short_id": parts[0],
            "blood_type": parts[1],
            "allergies": parts[2],
            "emergency_notes": parts[3] if len(parts) > 3 else "",
            "medications": parts[4].split(";") if len(parts) > 4 and parts[4] else [],
        }
    except Exception:
        return None


def build_emergency_url(
    public_id: str,
    base_url: str,
    blood_type: str,
    allergies: str = "",
    emergency_notes: str = "",
    medications: list = None,
) -> str:
    """
    Build the full emergency URL with embedded critical data.
    This URL will work even if the server is slow.
    """
    encoded = encode_emergency_data(
        public_id, blood_type, allergies, emergency_notes, medications
    )

    # Build URL with embedded data as query param
    return f"{base_url}/emergency/{public_id}/?d={urllib.parse.quote(encoded)}"
