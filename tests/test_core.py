"""Tests for src.core module."""

import pytest

from src.core import (
    build_message_name,
    calculate_value,
    extract_yaw_pitch,
    format_lineup_name,
    generate_unique_id,
    parse_getpos,
)


class TestParseGetpos:
    def test_valid_input(self):
        raw = "setpos -123.45 678.90 12.34; setang 90.00 -45.00 0.00"
        result = parse_getpos(raw)
        assert result["setpos"] == [-123.45, 678.90, 12.34]
        assert result["setang"] == [90.00, -45.00, 0.00]

    def test_valid_input_extra_whitespace(self):
        raw = "  setpos  -1.0  2.0  3.0 ;  setang  4.0  5.0  6.0  "
        result = parse_getpos(raw)
        assert result["setpos"] == [-1.0, 2.0, 3.0]
        assert result["setang"] == [4.0, 5.0, 6.0]

    def test_invalid_input_raises(self):
        with pytest.raises(ValueError, match="Invalid getpos format"):
            parse_getpos("not a valid string")

    def test_empty_input_raises(self):
        with pytest.raises(ValueError):
            parse_getpos("")

    def test_partial_input_raises(self):
        with pytest.raises(ValueError):
            parse_getpos("setpos 1.0 2.0 3.0")


class TestExtractYawPitch:
    def test_basic(self):
        setang = [90.00, -45.00, 0.00]
        yaw_angle, pitch_angle = extract_yaw_pitch(setang)
        assert yaw_angle == -45.00
        assert pitch_angle == 90.00


class TestCalculateValue:
    def test_positive_angle(self):
        result = calculate_value(90.00)
        assert abs(result - (90.00 / 0.022)) < 0.001

    def test_negative_angle(self):
        result = calculate_value(-45.00)
        assert abs(result - (-45.00 / 0.022)) < 0.001

    def test_zero(self):
        assert calculate_value(0.0) == 0.0


class TestGenerateUniqueId:
    def test_length_and_characters(self):
        uid = generate_unique_id()
        assert len(uid) == 6
        assert uid.isalnum()
        assert uid == uid.upper()

    def test_avoids_existing(self):
        existing = {"AAAAAA", "BBBBBB"}
        uid = generate_unique_id(existing)
        assert uid not in existing

    def test_unique_across_calls(self):
        ids = {generate_unique_id() for _ in range(100)}
        # Extremely unlikely to get duplicates in 100 calls
        assert len(ids) == 100


class TestFormatLineupName:
    def test_basic(self):
        result = format_lineup_name("t smoke jungle")
        assert result == "T \\n Smoke \\n Jungle \\n  \\n  \\n  \\n  \\n "

    def test_single_word(self):
        result = format_lineup_name("dust2")
        assert result == "Dust2 \\n  \\n  \\n  \\n  \\n "

    def test_capitalizes_first_letter(self):
        result = format_lineup_name("ct mid control")
        assert result == "Ct \\n Mid \\n Control \\n  \\n  \\n  \\n  \\n "


class TestBuildMessageName:
    def test_basic(self):
        result = build_message_name("dust2", "smoke", "ABC123")
        assert result == "CFG_DUST2_SMOKE_ABC123"

    def test_lowercase_input(self):
        result = build_message_name("mirage", "grenade", "xyz789")
        assert result == "CFG_MIRAGE_GRENADE_XYZ789"
