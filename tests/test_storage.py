"""
Tests for storage operations
"""
import pytest
import tempfile
import shutil
from pathlib import Path

from src.storage import Storage


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    storage = Storage(temp_dir)
    yield storage

    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def test_create_note_file(temp_storage):
    """Test creating a note file"""
    file_path = temp_storage.create_note_file(
        title="Test Note",
        content="This is test content",
        tags=["test", "python"]
    )

    assert file_path is not None
    full_path = Path(file_path)
    assert full_path.exists() or (temp_storage.notes_dir.parent / file_path).exists()


def test_read_note_file(temp_storage):
    """Test reading a note file"""
    file_path = temp_storage.create_note_file(
        title="Read Test",
        content="Content to read",
        tags=["test"]
    )

    note = temp_storage.read_note_file(file_path)
    assert note is not None
    assert note['title'] == "Read Test"
    assert note['content'] == "Content to read"
    assert "test" in note['tags']


def test_update_note_file(temp_storage):
    """Test updating a note file"""
    file_path = temp_storage.create_note_file(
        title="Original",
        content="Original content",
        tags=["old"]
    )

    result = temp_storage.update_note_file(
        file_path,
        title="Updated",
        content="Updated content",
        tags=["new"]
    )

    assert result is True

    note = temp_storage.read_note_file(file_path)
    assert note['title'] == "Updated"
    assert note['content'] == "Updated content"


def test_delete_note_file(temp_storage):
    """Test deleting a note file"""
    file_path = temp_storage.create_note_file(
        title="To Delete",
        content="Will be deleted",
        tags=[]
    )

    result = temp_storage.delete_note_file(file_path)
    assert result is True

    note = temp_storage.read_note_file(file_path)
    assert note is None


def test_get_all_note_files(temp_storage):
    """Test getting all note files"""
    temp_storage.create_note_file("Note 1", "Content 1", [])
    temp_storage.create_note_file("Note 2", "Content 2", [])
    temp_storage.create_note_file("Note 3", "Content 3", [])

    files = temp_storage.get_all_note_files()
    assert len(files) == 3


def test_filename_generation(temp_storage):
    """Test that filenames are generated correctly"""
    file_path = temp_storage.create_note_file(
        title="Test With Special Characters!@#$",
        content="Content",
        tags=[]
    )

    # Should not contain special characters
    assert "@" not in file_path
    assert "#" not in file_path
    assert "$" not in file_path


def test_storage_stats(temp_storage):
    """Test getting storage statistics"""
    temp_storage.create_note_file("Note 1", "Content 1", [])
    temp_storage.create_note_file("Note 2", "Content 2", [])

    stats = temp_storage.get_storage_stats()
    assert stats['total_files'] == 2
    assert stats['total_size_bytes'] > 0
