"""
Tests for utility functions
"""
import pytest
from datetime import datetime, timedelta

from src.utils import (
    format_datetime,
    format_relative_time,
    truncate_text,
    validate_note_title,
    validate_note_content,
    parse_tags_input,
    calculate_read_time,
    sanitize_filename,
    score_to_percentage
)


def test_format_datetime():
    """Test datetime formatting"""
    dt = datetime(2024, 1, 15, 10, 30, 0)
    result = format_datetime(dt)
    assert "2024-01-15" in result
    assert "10:30:00" in result


def test_format_relative_time():
    """Test relative time formatting"""
    now = datetime.now()

    # Just now
    result = format_relative_time(now)
    assert result == "just now"

    # Minutes ago
    result = format_relative_time(now - timedelta(minutes=5))
    assert "minute" in result

    # Hours ago
    result = format_relative_time(now - timedelta(hours=2))
    assert "hour" in result

    # Days ago
    result = format_relative_time(now - timedelta(days=3))
    assert "day" in result


def test_truncate_text():
    """Test text truncation"""
    text = "This is a long text that needs to be truncated"

    result = truncate_text(text, max_length=20)
    assert len(result) <= 23  # 20 + "..."
    assert result.endswith("...")


def test_validate_note_title():
    """Test note title validation"""
    valid, error = validate_note_title("Valid Title")
    assert valid is True
    assert error == ""

    valid, error = validate_note_title("")
    assert valid is False

    valid, error = validate_note_title("ab")
    assert valid is False

    valid, error = validate_note_title("a" * 250)
    assert valid is False


def test_validate_note_content():
    """Test note content validation"""
    valid, error = validate_note_content("This is valid content with enough text")
    assert valid is True

    valid, error = validate_note_content("")
    assert valid is False

    valid, error = validate_note_content("short")
    assert valid is False


def test_parse_tags_input():
    """Test parsing tags from input"""
    # Comma-separated
    tags = parse_tags_input("python, java, javascript")
    assert len(tags) == 3
    assert "python" in tags

    # Space-separated
    tags = parse_tags_input("python java javascript")
    assert len(tags) == 3

    # Empty
    tags = parse_tags_input("")
    assert len(tags) == 0


def test_calculate_read_time():
    """Test reading time calculation"""
    # Short text
    text = " ".join(["word"] * 50)
    result = calculate_read_time(text, words_per_minute=200)
    assert "min" in result

    # Long text
    text = " ".join(["word"] * 5000)
    result = calculate_read_time(text, words_per_minute=200)
    assert "h" in result or "min" in result


def test_sanitize_filename():
    """Test filename sanitization"""
    result = sanitize_filename("Test: File<Name>")
    assert ":" not in result
    assert "<" not in result
    assert ">" not in result

    result = sanitize_filename("File With Spaces")
    assert "_" in result


def test_score_to_percentage():
    """Test score to percentage conversion"""
    assert score_to_percentage(0.75) == 75
    assert score_to_percentage(1.0) == 100
    assert score_to_percentage(0.0) == 0
