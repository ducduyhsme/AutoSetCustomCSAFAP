"""Config file generation for CS2 lineup configurations."""

import os


def ensure_directory(path: str) -> None:
    """Create directory tree if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


# ---------------------------------------------------------------------------
# main.cfg helpers
# ---------------------------------------------------------------------------

def append_main_cfg(
    cfg_dir: str,
    grenade: str,
    unique_id: str,
    yaw_value: float,
    pitch_value: float,
) -> None:
    """Append yaw/pitch alias lines to ``main.cfg``.

    Adds two lines::

        alias {grenade}_yaw_{id} "yaw {yaw_value} 1 1"
        alias {grenade}_pitch_{id} "pitch {pitch_value} 1 1"
    """
    ensure_directory(cfg_dir)
    path = os.path.join(cfg_dir, "main.cfg")
    grenade_lower = grenade.lower()
    lines = [
        f'alias {grenade_lower}_yaw_{unique_id} "yaw {yaw_value} 1 1"',
        f'alias {grenade_lower}_pitch_{unique_id} "pitch {pitch_value} 1 1"',
    ]
    with open(path, "a", encoding="utf-8") as fh:
        for line in lines:
            fh.write(line + "\n")


# ---------------------------------------------------------------------------
# platform_english.txt helpers
# ---------------------------------------------------------------------------

def append_platform_english(
    resource_dir: str,
    message_name: str,
    formatted_lineup_name: str,
) -> None:
    """Append a lineup entry to ``platform_english.txt``.

    Format::

        "CFG_MAP_NADE_ID"                    "Formatted Name"
    """
    ensure_directory(resource_dir)
    path = os.path.join(resource_dir, "platform_english.txt")
    entry = f'"{message_name}"                    "{formatted_lineup_name}"'
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(entry + "\n")


# ---------------------------------------------------------------------------
# labels.cfg helpers
# ---------------------------------------------------------------------------

def read_labels_cfg(cfg_dir: str, map_name: str, side: str) -> dict:
    """Read an existing labels cfg and return a dict of slot -> message_name.

    Returns ``{(tab, text): message_name, ...}``.
    """
    filename = f"{map_name.lower()}_{side.upper()}_labels.cfg"
    path = os.path.join(cfg_dir, filename)
    slots: dict = {}
    if not os.path.exists(path):
        return slots
    import re
    pattern = re.compile(
        r'cl_radial_radio_tab_(\d+)_text_(\d+)\s+"(#[^"]+)"'
    )
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            m = pattern.search(line)
            if m:
                tab = int(m.group(1))
                text = int(m.group(2))
                msg = m.group(3)
                slots[(tab, text)] = msg
    return slots


def write_labels_cfg(cfg_dir: str, map_name: str, side: str, slots: dict) -> None:
    """Write the labels cfg from a slots dict."""
    ensure_directory(cfg_dir)
    filename = f"{map_name.lower()}_{side.upper()}_labels.cfg"
    path = os.path.join(cfg_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        for (tab, text), msg in sorted(slots.items()):
            fh.write(f'cl_radial_radio_tab_{tab}_text_{text} "{msg}"\n')


def append_label(
    cfg_dir: str,
    map_name: str,
    side: str,
    tab: int,
    text: int,
    message_name: str,
) -> None:
    """Append a single label entry to the labels cfg."""
    slots = read_labels_cfg(cfg_dir, map_name, side)
    slots[(tab, text)] = f"#{message_name}"
    write_labels_cfg(cfg_dir, map_name, side, slots)


# ---------------------------------------------------------------------------
# commands.cfg helpers
# ---------------------------------------------------------------------------

def read_commands_cfg(cfg_dir: str, map_name: str, side: str) -> dict:
    """Read an existing commands cfg and return a dict of slot -> command.

    Returns ``{(tab, text): command_string, ...}``.
    """
    filename = f"{map_name.lower()}_{side.upper()}_commands.cfg"
    path = os.path.join(cfg_dir, filename)
    slots: dict = {}
    if not os.path.exists(path):
        return slots
    import re
    pattern = re.compile(
        r'cl_radial_radio_tab_(\d+)_text_(\d+)\s+(.*)'
    )
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            m = pattern.search(line)
            if m:
                tab = int(m.group(1))
                text = int(m.group(2))
                cmd = m.group(3).strip()
                slots[(tab, text)] = cmd
    return slots


def write_commands_cfg(cfg_dir: str, map_name: str, side: str, slots: dict) -> None:
    """Write the commands cfg from a slots dict."""
    ensure_directory(cfg_dir)
    filename = f"{map_name.lower()}_{side.upper()}_commands.cfg"
    path = os.path.join(cfg_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        for (tab, text), cmd in sorted(slots.items()):
            fh.write(f"cl_radial_radio_tab_{tab}_text_{text} {cmd}\n")


def append_command(
    cfg_dir: str,
    map_name: str,
    side: str,
    tab: int,
    text: int,
    grenade: str,
    unique_id: str,
) -> None:
    """Append a single command entry to the commands cfg."""
    slots = read_commands_cfg(cfg_dir, map_name, side)
    grenade_lower = grenade.lower()
    cmd = (
        f'cmd";{grenade_lower}_yaw_{unique_id};'
        f'{grenade_lower}_pitch_{unique_id};'
    )
    slots[(tab, text)] = cmd
    write_commands_cfg(cfg_dir, map_name, side, slots)


# ---------------------------------------------------------------------------
# Deletion helpers
# ---------------------------------------------------------------------------

def remove_from_main_cfg(cfg_dir: str, unique_id: str) -> None:
    """Remove alias lines containing *unique_id* from ``main.cfg``."""
    path = os.path.join(cfg_dir, "main.cfg")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    with open(path, "w", encoding="utf-8") as fh:
        for line in lines:
            if unique_id not in line:
                fh.write(line)


def remove_from_platform_english(resource_dir: str, message_name: str) -> None:
    """Remove the entry for *message_name* from ``platform_english.txt``."""
    path = os.path.join(resource_dir, "platform_english.txt")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    with open(path, "w", encoding="utf-8") as fh:
        for line in lines:
            if message_name not in line:
                fh.write(line)


def remove_slot_from_labels(
    cfg_dir: str, map_name: str, side: str, tab: int, text: int
) -> None:
    """Remove a specific slot from the labels cfg."""
    slots = read_labels_cfg(cfg_dir, map_name, side)
    slots.pop((tab, text), None)
    write_labels_cfg(cfg_dir, map_name, side, slots)


def remove_slot_from_commands(
    cfg_dir: str, map_name: str, side: str, tab: int, text: int
) -> None:
    """Remove a specific slot from the commands cfg."""
    slots = read_commands_cfg(cfg_dir, map_name, side)
    slots.pop((tab, text), None)
    write_commands_cfg(cfg_dir, map_name, side, slots)


# ---------------------------------------------------------------------------
# Occupied slot detection
# ---------------------------------------------------------------------------

def get_occupied_slots(cfg_dir: str, map_name: str, side: str) -> set:
    """Return the set of ``(tab, text)`` tuples already in use."""
    labels = read_labels_cfg(cfg_dir, map_name, side)
    commands = read_commands_cfg(cfg_dir, map_name, side)
    return set(labels.keys()) | set(commands.keys())


def find_first_empty_slot(cfg_dir: str, map_name: str, side: str):
    """Find the first empty ``(tab, text)`` slot.

    Returns ``(tab, text)`` or ``None`` if all slots are occupied.
    """
    from src.constants import RADIO_TAB_MIN, RADIO_TAB_MAX, RADIO_TEXT_MIN, RADIO_TEXT_MAX
    occupied = get_occupied_slots(cfg_dir, map_name, side)
    for tab in range(RADIO_TAB_MIN, RADIO_TAB_MAX + 1):
        for text in range(RADIO_TEXT_MIN, RADIO_TEXT_MAX + 1):
            if (tab, text) not in occupied:
                return (tab, text)
    return None
