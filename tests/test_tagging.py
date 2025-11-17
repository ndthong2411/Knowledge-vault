"""
Tests for auto-tagging system
"""
import pytest

from src.tagging import AutoTagger


@pytest.fixture
def tagger():
    """Create an AutoTagger instance"""
    return AutoTagger()


def test_suggest_tags(tagger):
    """Test tag suggestion"""
    title = "Introduction to Python Programming"
    content = """
    Python is a high-level programming language.
    It's widely used for web development, data science, and machine learning.
    """

    tags = tagger.suggest_tags(title, content, max_tags=5)

    assert isinstance(tags, list)
    assert len(tags) <= 5
    # Should suggest programming-related tags
    assert len(tags) > 0


def test_extract_hashtags(tagger):
    """Test extracting hashtags from text"""
    text = "This is a note about #python and #machinelearning"

    hashtags = tagger.extract_hashtags(text)

    assert "python" in hashtags
    assert "machinelearning" in hashtags


def test_merge_tags(tagger):
    """Test merging different tag sources"""
    suggested = ["python", "programming"]
    user = ["tutorial", "beginner"]
    hashtags = ["coding"]

    merged = tagger.merge_tags(suggested, user, hashtags)

    # User tags should come first
    assert "tutorial" in merged
    assert "beginner" in merged
    assert "coding" in merged


def test_validate_tags(tagger):
    """Test tag validation"""
    tags = ["python", "a", "valid-tag", "another_tag", "the", ""]

    validated = tagger.validate_tags(tags)

    assert "python" in validated
    assert "valid-tag" in validated
    # Should filter out short tags and stop words
    assert "a" not in validated
    assert "the" not in validated
    assert "" not in validated


def test_normalize_tag(tagger):
    """Test tag normalization"""
    tag1 = tagger._normalize_tag("  Python  ")
    assert tag1 == "python"

    tag2 = tagger._normalize_tag("Machine Learning")
    assert tag2 == "machine-learning"

    tag3 = tagger._normalize_tag("Web-Dev")
    assert tag3 == "web-dev"


def test_tag_deduplication(tagger):
    """Test that duplicate tags are removed"""
    tags = ["python", "Python", "PYTHON", "java"]

    validated = tagger.validate_tags(tags)

    # Should only have python once (normalized to lowercase)
    python_count = sum(1 for tag in validated if tag == "python")
    assert python_count == 1
