"""
Tests for database operations
"""
import pytest
import tempfile
import os
from pathlib import Path
import numpy as np

from src.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)

    db = Database(db_path)
    yield db

    db.close()
    if db_path.exists():
        os.unlink(db_path)


def test_create_note(temp_db):
    """Test creating a note"""
    note_id = temp_db.create_note(
        title="Test Note",
        content="This is test content",
        file_path="test.md",
        tags=["test", "python"]
    )

    assert note_id > 0

    note = temp_db.get_note(note_id)
    assert note is not None
    assert note['title'] == "Test Note"
    assert note['content'] == "This is test content"
    assert len(note['tags']) == 2
    assert "test" in note['tags']


def test_update_note(temp_db):
    """Test updating a note"""
    note_id = temp_db.create_note(
        title="Original Title",
        content="Original content",
        file_path="test.md"
    )

    temp_db.update_note(
        note_id,
        title="Updated Title",
        content="Updated content",
        tags=["new", "tags"]
    )

    note = temp_db.get_note(note_id)
    assert note['title'] == "Updated Title"
    assert note['content'] == "Updated content"
    assert len(note['tags']) == 2


def test_delete_note(temp_db):
    """Test deleting a note"""
    note_id = temp_db.create_note(
        title="To Delete",
        content="Will be deleted",
        file_path="delete.md"
    )

    result = temp_db.delete_note(note_id)
    assert result is True

    note = temp_db.get_note(note_id)
    assert note is None


def test_get_all_notes(temp_db):
    """Test getting all notes"""
    temp_db.create_note("Note 1", "Content 1", "note1.md")
    temp_db.create_note("Note 2", "Content 2", "note2.md")
    temp_db.create_note("Note 3", "Content 3", "note3.md")

    notes = temp_db.get_all_notes()
    assert len(notes) == 3


def test_full_text_search(temp_db):
    """Test full-text search"""
    temp_db.create_note("Python Tutorial", "Learn Python programming", "python.md")
    temp_db.create_note("Java Guide", "Java programming basics", "java.md")

    results = temp_db.full_text_search("Python")
    assert len(results) >= 1
    assert any("Python" in note['title'] for note in results)


def test_embeddings(temp_db):
    """Test saving and retrieving embeddings"""
    note_id = temp_db.create_note("Test", "Content", "test.md")

    embedding = np.random.rand(384).astype(np.float32)
    temp_db.save_embedding(note_id, embedding)

    retrieved = temp_db.get_embedding(note_id)
    assert retrieved is not None
    assert np.allclose(embedding, retrieved)


def test_tags(temp_db):
    """Test tag operations"""
    note_id = temp_db.create_note(
        "Tagged Note",
        "Content",
        "tagged.md",
        tags=["python", "tutorial", "beginner"]
    )

    tags = temp_db.get_note_tags(note_id)
    assert len(tags) == 3
    assert "python" in tags

    all_tags = temp_db.get_all_tags()
    assert len(all_tags) >= 3


def test_search_by_tags(temp_db):
    """Test searching by tags"""
    temp_db.create_note("Note 1", "Content", "n1.md", tags=["python", "web"])
    temp_db.create_note("Note 2", "Content", "n2.md", tags=["python", "data"])
    temp_db.create_note("Note 3", "Content", "n3.md", tags=["java"])

    results = temp_db.search_by_tags(["python"])
    assert len(results) >= 2

    results = temp_db.search_by_tags(["python", "web"], match_all=True)
    assert len(results) >= 1


def test_statistics(temp_db):
    """Test getting statistics"""
    temp_db.create_note("Note 1", "Content", "n1.md", tags=["test"])
    temp_db.create_note("Note 2", "Content", "n2.md", tags=["test"])

    stats = temp_db.get_statistics()
    assert stats['total_notes'] == 2
    assert stats['total_tags'] >= 1
