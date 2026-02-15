"""Core logic for parsing getpos output and calculating yaw/pitch values."""

import random
import re
import string

from src.constants import SENSITIVITY_MULTIPLIER

# Characters used for generating unique IDs
_ID_CHARS = string.ascii_uppercase + string.digits
_ID_LENGTH = 6


def parse_getpos(raw: str) -> dict:
    """Parse a CS2 ``getpos`` console output and return setpos/setang values.

    Expected format example::

        setpos -123.45 678.90 12.34; setang 90.00 -45.00 0.00

    Returns a dict with keys ``setpos`` (list of 3 floats) and ``setang``
    (list of 3 floats: pitch, yaw, roll).

    Raises ``ValueError`` on invalid input.
    """
    raw = raw.strip()
    pattern = (
        r"setpos\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*;\s*"
        r"setang\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)"
    )
    match = re.search(pattern, raw)
    if not match:
        raise ValueError(
            "Invalid getpos format. Expected: "
            "'setpos X Y Z; setang PITCH YAW ROLL'"
        )
    values = [float(match.group(i)) for i in range(1, 7)]
    return {
        "setpos": values[0:3],
        "setang": values[3:6],  # pitch, yaw, roll
    }


def extract_yaw_pitch(setang: list) -> tuple:
    """Extract yaw_angle and pitch_angle from setang values.

    ``setang`` is ``[pitch, yaw, roll]`` as output by CS2.

    Returns ``(yaw_angle, pitch_angle)``.
    """
    pitch_angle = setang[0]
    yaw_angle = setang[1]
    return yaw_angle, pitch_angle


def calculate_value(angle: float) -> float:
    """Calculate the mouse movement value from an angle.

    Formula: value = angle / (sensitivity * 0.022).
    Since sensitivity is always 1.0, this simplifies to angle / 0.022.
    """
    return angle / SENSITIVITY_MULTIPLIER


def generate_unique_id(existing_ids: set | None = None) -> str:
    """Generate a random 6-character uppercase alphanumeric ID.

    Ensures the generated ID does not collide with any ID in *existing_ids*.
    """
    if existing_ids is None:
        existing_ids = set()
    while True:
        new_id = "".join(random.choices(_ID_CHARS, k=_ID_LENGTH))
        if new_id not in existing_ids:
            return new_id


def format_lineup_name(raw_name: str) -> str:
    """Format a lineup name for ``platform_english.txt``.

    Each word has its first letter capitalised. Words are separated by
    ``\\n``. The string always ends with ``\\n  \\n  \\n  \\n  \\n``.

    Example input:  ``"t smoke jungle"``
    Example output: ``"T \\n Smoke \\n Jungle \\n  \\n  \\n  \\n  \\n "``
    """
    words = raw_name.strip().split()
    capitalized = [w.capitalize() for w in words]
    name_part = " \\n ".join(capitalized)
    return name_part + " \\n  \\n  \\n  \\n  \\n "


def build_message_name(map_name: str, grenade: str, unique_id: str) -> str:
    """Build the message name used across config files.

    Format: ``CFG_{MAP}_{GRENADE}_{ID}``
    """
    return f"CFG_{map_name.upper()}_{grenade.upper()}_{unique_id.upper()}"
