"""JSON-based persistence for lineup data."""

import json
import os


_DEFAULT_DATA = {
    "lineups": [],
    "settings": {
        "cs2_path": "",
        "sensitivity": 1.0,
    },
}


def _data_path(storage_dir: str) -> str:
    return os.path.join(storage_dir, "lineups.json")


def load_data(storage_dir: str) -> dict:
    """Load stored lineup data from disk.  Returns default structure if missing."""
    path = _data_path(storage_dir)
    if not os.path.exists(path):
        return json.loads(json.dumps(_DEFAULT_DATA))  # deep copy
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_data(storage_dir: str, data: dict) -> None:
    """Persist lineup data to disk."""
    os.makedirs(storage_dir, exist_ok=True)
    path = _data_path(storage_dir)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def get_existing_ids(data: dict) -> set:
    """Return set of all unique IDs already in use."""
    return {lineup["unique_id"] for lineup in data.get("lineups", [])}


def add_lineup(data: dict, lineup: dict) -> dict:
    """Add a lineup entry to the data structure and return updated data."""
    data.setdefault("lineups", []).append(lineup)
    return data


def remove_lineup(data: dict, unique_id: str) -> dict:
    """Remove a lineup by its unique ID and return updated data."""
    data["lineups"] = [
        lu for lu in data.get("lineups", []) if lu.get("unique_id") != unique_id
    ]
    return data


def find_lineup(data: dict, unique_id: str):
    """Find and return a lineup by unique ID, or ``None``."""
    for lu in data.get("lineups", []):
        if lu.get("unique_id") == unique_id:
            return lu
    return None
