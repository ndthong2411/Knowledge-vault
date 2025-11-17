#!/usr/bin/env python3
"""
Project validation script
Checks project structure, imports, and basic functionality
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_structure():
    """Verify project structure"""
    print("🔍 Checking project structure...")

    required_files = [
        "app.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "src/__init__.py",
        "src/database.py",
        "src/storage.py",
        "src/search_engine.py",
        "src/tagging.py",
        "src/utils.py",
    ]

    required_dirs = [
        "src",
        "tests",
        "data",
        "data/notes",
        ".streamlit",
    ]

    all_ok = True

    for file in required_files:
        filepath = project_root / file
        if filepath.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ Missing: {file}")
            all_ok = False

    for dir_path in required_dirs:
        dirpath = project_root / dir_path
        if dirpath.exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ Missing: {dir_path}/")
            all_ok = False

    return all_ok


def check_imports():
    """Test all module imports"""
    print("\n🔍 Checking module imports...")

    modules = [
        ("config", "Configuration"),
        ("src.database", "Database"),
        ("src.storage", "Storage"),
        ("src.search_engine", "SearchEngine"),
        ("src.tagging", "AutoTagger"),
        ("src.utils", "format_datetime"),
    ]

    all_ok = True

    for module_name, item in modules:
        try:
            module = __import__(module_name, fromlist=[item])
            if hasattr(module, item):
                print(f"  ✅ {module_name}.{item}")
            else:
                print(f"  ❌ {module_name}.{item} not found")
                all_ok = False
        except Exception as e:
            print(f"  ❌ {module_name}: {str(e)}")
            all_ok = False

    return all_ok


def test_database():
    """Test database operations"""
    print("\n🔍 Testing database operations...")

    try:
        from src.database import Database
        import tempfile

        # Create temp database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)

        db = Database(db_path)

        # Test create
        note_id = db.create_note("Test Note", "Test content", "test.md", ["test"])
        print(f"  ✅ Created note with ID: {note_id}")

        # Test read
        note = db.get_note(note_id)
        assert note is not None
        print(f"  ✅ Retrieved note: {note['title']}")

        # Test update
        db.update_note(note_id, title="Updated Title")
        note = db.get_note(note_id)
        assert note['title'] == "Updated Title"
        print(f"  ✅ Updated note title")

        # Test tags
        tags = db.get_all_tags()
        print(f"  ✅ Retrieved {len(tags)} tags")

        # Cleanup
        db.close()
        os.unlink(db_path)

        return True

    except Exception as e:
        print(f"  ❌ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_storage():
    """Test storage operations"""
    print("\n🔍 Testing storage operations...")

    try:
        from src.storage import Storage
        import tempfile
        import shutil

        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp())
        storage = Storage(temp_dir)

        # Test create
        file_path = storage.create_note_file("Test Note", "Test content", ["test"])
        print(f"  ✅ Created note file: {file_path}")

        # Test read
        note = storage.read_note_file(file_path)
        assert note is not None
        print(f"  ✅ Read note: {note['title']}")

        # Test update
        storage.update_note_file(file_path, title="Updated Title")
        note = storage.read_note_file(file_path)
        assert note['title'] == "Updated Title"
        print(f"  ✅ Updated note")

        # Cleanup
        shutil.rmtree(temp_dir)

        return True

    except Exception as e:
        print(f"  ❌ Storage test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_tagging():
    """Test auto-tagging"""
    print("\n🔍 Testing auto-tagging...")

    try:
        from src.tagging import AutoTagger

        tagger = AutoTagger()

        # Test tag suggestion
        tags = tagger.suggest_tags(
            "Python Programming Tutorial",
            "Learn Python programming language basics",
            max_tags=5
        )
        print(f"  ✅ Suggested {len(tags)} tags: {', '.join(tags)}")

        # Test hashtag extraction
        hashtags = tagger.extract_hashtags("This is about #python and #programming")
        print(f"  ✅ Extracted hashtags: {', '.join(hashtags)}")

        # Test validation
        validated = tagger.validate_tags(["python", "a", "test", ""])
        print(f"  ✅ Validated tags: {', '.join(validated)}")

        return True

    except Exception as e:
        print(f"  ❌ Tagging test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Test utility functions"""
    print("\n🔍 Testing utilities...")

    try:
        from src.utils import (
            format_datetime,
            truncate_text,
            validate_note_title,
            parse_tags_input
        )
        from datetime import datetime

        # Test datetime formatting
        dt = datetime.now()
        formatted = format_datetime(dt)
        print(f"  ✅ Format datetime: {formatted}")

        # Test text truncation
        text = "This is a long text"
        truncated = truncate_text(text, 10)
        print(f"  ✅ Truncate text: {truncated}")

        # Test validation
        valid, error = validate_note_title("Valid Title")
        assert valid is True
        print(f"  ✅ Title validation")

        # Test tag parsing
        tags = parse_tags_input("python, java, javascript")
        assert len(tags) == 3
        print(f"  ✅ Parse tags: {', '.join(tags)}")

        return True

    except Exception as e:
        print(f"  ❌ Utils test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("🚀 Knowledge Vault - Project Validation")
    print("=" * 60)

    results = {
        "Structure": check_structure(),
        "Imports": check_imports(),
        "Database": test_database(),
        "Storage": test_storage(),
        "Tagging": test_tagging(),
        "Utils": test_utils(),
    }

    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:15s}: {status}")

    all_passed = all(results.values())

    print("=" * 60)
    if all_passed:
        print("🎉 All validation checks passed!")
        return 0
    else:
        print("❌ Some validation checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
