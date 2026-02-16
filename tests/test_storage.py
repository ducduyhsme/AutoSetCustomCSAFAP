"""Tests for src.storage module."""

import os
import tempfile

import pytest

from src.storage import (
    add_lineup,
    find_lineup,
    get_existing_ids,
    load_data,
    remove_lineup,
    save_data,
)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


class TestLoadSaveData:
    def test_load_missing_returns_default(self, tmp_dir):
        data = load_data(tmp_dir)
        assert "lineups" in data
        assert "settings" in data
        assert data["lineups"] == []

    def test_save_and_load_roundtrip(self, tmp_dir):
        data = load_data(tmp_dir)
        data["lineups"].append({"unique_id": "TEST01", "name": "test"})
        save_data(tmp_dir, data)

        loaded = load_data(tmp_dir)
        assert len(loaded["lineups"]) == 1
        assert loaded["lineups"][0]["unique_id"] == "TEST01"


class TestLineupOperations:
    def test_add_lineup(self):
        data = {"lineups": []}
        lineup = {"unique_id": "ID0001", "name": "Test Lineup"}
        data = add_lineup(data, lineup)
        assert len(data["lineups"]) == 1

    def test_remove_lineup(self):
        data = {"lineups": [{"unique_id": "ID0001"}, {"unique_id": "ID0002"}]}
        data = remove_lineup(data, "ID0001")
        assert len(data["lineups"]) == 1
        assert data["lineups"][0]["unique_id"] == "ID0002"

    def test_find_lineup(self):
        data = {"lineups": [{"unique_id": "ID0001", "name": "Test"}]}
        result = find_lineup(data, "ID0001")
        assert result is not None
        assert result["name"] == "Test"

    def test_find_lineup_missing(self):
        data = {"lineups": []}
        assert find_lineup(data, "NOPE") is None

    def test_get_existing_ids(self):
        data = {"lineups": [{"unique_id": "A"}, {"unique_id": "B"}]}
        ids = get_existing_ids(data)
        assert ids == {"A", "B"}
