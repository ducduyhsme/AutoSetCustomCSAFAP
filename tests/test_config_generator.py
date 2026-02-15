"""Tests for src.config_generator module."""

import os
import tempfile

import pytest

from src.config_generator import (
    append_command,
    append_label,
    append_main_cfg,
    append_platform_english,
    find_first_empty_slot,
    get_occupied_slots,
    read_commands_cfg,
    read_labels_cfg,
    remove_from_main_cfg,
    remove_from_platform_english,
    remove_slot_from_commands,
    remove_slot_from_labels,
)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


class TestAppendMainCfg:
    def test_creates_file_and_appends(self, tmp_dir):
        append_main_cfg(tmp_dir, "smoke", "ABC123", 1234.5, -678.9)
        path = os.path.join(tmp_dir, "main.cfg")
        assert os.path.exists(path)
        content = open(path, encoding="utf-8").read()
        assert 'alias smoke_yaw_ABC123 "yaw 1234.5 1 1"' in content
        assert 'alias smoke_pitch_ABC123 "pitch -678.9 1 1"' in content

    def test_appends_multiple(self, tmp_dir):
        append_main_cfg(tmp_dir, "smoke", "ID0001", 100.0, 200.0)
        append_main_cfg(tmp_dir, "grenade", "ID0002", 300.0, 400.0)
        content = open(os.path.join(tmp_dir, "main.cfg"), encoding="utf-8").read()
        assert "ID0001" in content
        assert "ID0002" in content


class TestAppendPlatformEnglish:
    def test_creates_and_appends(self, tmp_dir):
        append_platform_english(tmp_dir, "CFG_DUST2_SMOKE_ABC123", "T \\n Smoke")
        path = os.path.join(tmp_dir, "platform_english.txt")
        content = open(path, encoding="utf-8").read()
        assert '"CFG_DUST2_SMOKE_ABC123"' in content
        assert '"T \\n Smoke"' in content


class TestLabelsAndCommands:
    def test_read_empty(self, tmp_dir):
        result = read_labels_cfg(tmp_dir, "dust2", "T")
        assert result == {}

    def test_append_and_read_label(self, tmp_dir):
        append_label(tmp_dir, "dust2", "T", 1, 3, "CFG_DUST2_SMOKE_ABC123")
        slots = read_labels_cfg(tmp_dir, "dust2", "T")
        assert (1, 3) in slots
        assert slots[(1, 3)] == "#CFG_DUST2_SMOKE_ABC123"

    def test_append_and_read_command(self, tmp_dir):
        append_command(tmp_dir, "dust2", "T", 1, 3, "smoke", "ABC123")
        slots = read_commands_cfg(tmp_dir, "dust2", "T")
        assert (1, 3) in slots
        assert "smoke_yaw_ABC123" in slots[(1, 3)]
        assert "smoke_pitch_ABC123" in slots[(1, 3)]

    def test_get_occupied_slots(self, tmp_dir):
        append_label(tmp_dir, "mirage", "CT", 0, 1, "CFG_MIRAGE_SMOKE_X1")
        append_command(tmp_dir, "mirage", "CT", 0, 1, "smoke", "X1")
        occupied = get_occupied_slots(tmp_dir, "mirage", "CT")
        assert (0, 1) in occupied

    def test_find_first_empty_slot(self, tmp_dir):
        # With nothing occupied, first slot should be (0, 1)
        slot = find_first_empty_slot(tmp_dir, "dust2", "T")
        assert slot == (0, 1)

    def test_find_first_empty_slot_skips_occupied(self, tmp_dir):
        append_label(tmp_dir, "dust2", "T", 0, 1, "CFG_DUST2_SMOKE_X1")
        slot = find_first_empty_slot(tmp_dir, "dust2", "T")
        assert slot == (0, 2)


class TestRemoval:
    def test_remove_from_main_cfg(self, tmp_dir):
        append_main_cfg(tmp_dir, "smoke", "REMOVE", 1.0, 2.0)
        append_main_cfg(tmp_dir, "smoke", "KEEP00", 3.0, 4.0)
        remove_from_main_cfg(tmp_dir, "REMOVE")
        content = open(os.path.join(tmp_dir, "main.cfg"), encoding="utf-8").read()
        assert "REMOVE" not in content
        assert "KEEP00" in content

    def test_remove_from_platform_english(self, tmp_dir):
        append_platform_english(tmp_dir, "CFG_DUST2_SMOKE_REMOVE", "Name1")
        append_platform_english(tmp_dir, "CFG_DUST2_SMOKE_KEEP00", "Name2")
        remove_from_platform_english(tmp_dir, "CFG_DUST2_SMOKE_REMOVE")
        content = open(
            os.path.join(tmp_dir, "platform_english.txt"), encoding="utf-8"
        ).read()
        assert "REMOVE" not in content
        assert "KEEP00" in content

    def test_remove_slot_from_labels(self, tmp_dir):
        append_label(tmp_dir, "dust2", "T", 0, 1, "MSG1")
        append_label(tmp_dir, "dust2", "T", 0, 2, "MSG2")
        remove_slot_from_labels(tmp_dir, "dust2", "T", 0, 1)
        slots = read_labels_cfg(tmp_dir, "dust2", "T")
        assert (0, 1) not in slots
        assert (0, 2) in slots

    def test_remove_slot_from_commands(self, tmp_dir):
        append_command(tmp_dir, "dust2", "T", 0, 1, "smoke", "ID1")
        append_command(tmp_dir, "dust2", "T", 0, 2, "smoke", "ID2")
        remove_slot_from_commands(tmp_dir, "dust2", "T", 0, 1)
        slots = read_commands_cfg(tmp_dir, "dust2", "T")
        assert (0, 1) not in slots
        assert (0, 2) in slots
