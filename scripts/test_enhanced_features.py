#!/usr/bin/env python3
"""
Test script for enhanced features
Tests backlinks, folders, templates, etc.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database
from src.storage import Storage
from src.backlinks import BacklinksParser
from src.export_import import ExportImport
from scripts.migrate_db import migrate_database

def test_enhanced_features():
    """Test all enhanced features"""
    print("=" * 60)
    print("🧪 Testing Enhanced Features")
    print("=" * 60)

    # 1. Run migration
    print("\n1️⃣ Running database migration...")
    try:
        migrate_database()
        print("✅ Migration completed")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

    # 2. Test database
    print("\n2️⃣ Testing database...")
    try:
        db = Database()
        print("✅ Database initialized")

        # Test folders
        folders = db.get_all_folders()
        print(f"✅ Found {len(folders)} default folders")

        # Test templates
        templates = db.get_all_templates()
        print(f"✅ Found {len(templates)} default templates")

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. Test creating a note with backlinks
    print("\n3️⃣ Testing backlinks...")
    try:
        storage = Storage()

        # Create first note
        note1_id = db.create_note(
            "Python Basics",
            "Introduction to Python programming",
            "test/python-basics.md",
            ["python", "programming"]
        )
        print(f"✅ Created note 1: ID={note1_id}")

        # Create second note with backlink
        note2_id = db.create_note(
            "Machine Learning",
            "ML uses [[Python Basics]] for implementation",
            "test/ml.md",
            ["python", "ml"]
        )
        print(f"✅ Created note 2: ID={note2_id}")

        # Process backlinks
        parser = BacklinksParser(db)
        result = parser.process_note_links(note2_id, "ML uses [[Python Basics]] for implementation")
        print(f"✅ Processed backlinks: {result['found']}")

        # Get links
        links = db.get_note_links(note1_id)
        print(f"✅ Note 1 has {len(links['incoming'])} backlinks")

    except Exception as e:
        print(f"❌ Backlinks test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 4. Test folders
    print("\n4️⃣ Testing folders...")
    try:
        # Create custom folder
        folder_id = db.create_folder("Test Folder", icon="🧪", color="#FF5722")
        print(f"✅ Created folder: ID={folder_id}")

        # Move note to folder
        db.move_note_to_folder(note1_id, folder_id)
        print(f"✅ Moved note to folder")

        # Get notes in folder
        notes_in_folder = db.get_notes_in_folder(folder_id)
        print(f"✅ Folder has {len(notes_in_folder)} notes")

    except Exception as e:
        print(f"❌ Folders test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 5. Test favorites
    print("\n5️⃣ Testing favorites...")
    try:
        db.toggle_favorite(note1_id)
        print(f"✅ Toggled favorite")

        favorites = db.get_favorite_notes()
        print(f"✅ Found {len(favorites)} favorites")

    except Exception as e:
        print(f"❌ Favorites test failed: {e}")
        return False

    # 6. Test version history
    print("\n6️⃣ Testing version history...")
    try:
        version_id = db.save_version(note1_id, "Python Basics", "Updated content v1")
        print(f"✅ Saved version: ID={version_id}")

        versions = db.get_note_versions(note1_id)
        print(f"✅ Note has {len(versions)} versions")

    except Exception as e:
        print(f"❌ Version history test failed: {e}")
        return False

    # 7. Test daily notes
    print("\n7️⃣ Testing daily notes...")
    try:
        daily_note = db.get_or_create_daily_note()
        print(f"✅ Daily note: {daily_note['title']}")

        daily_notes = db.get_all_daily_notes(limit=10)
        print(f"✅ Found {len(daily_notes)} daily notes")

    except Exception as e:
        print(f"❌ Daily notes test failed: {e}")
        return False

    # 8. Test export/import
    print("\n8️⃣ Testing export/import...")
    try:
        exporter = ExportImport(db, storage)

        # Export to markdown
        md_content = exporter.export_note_markdown(note1_id)
        print(f"✅ Exported to markdown ({len(md_content)} bytes)")

        # Export to JSON
        json_content = exporter.export_note_json(note1_id)
        print(f"✅ Exported to JSON ({len(json_content)} bytes)")

    except Exception as e:
        print(f"❌ Export/import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 9. Test graph data
    print("\n9️⃣ Testing graph data...")
    try:
        graph_data = db.get_graph_data()
        print(f"✅ Graph has {len(graph_data['nodes'])} nodes, {len(graph_data['links'])} links")

    except Exception as e:
        print(f"❌ Graph data test failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)

    # Print summary
    print("\n📊 Summary:")
    print(f"  - Folders: {len(db.get_all_folders())}")
    print(f"  - Templates: {len(db.get_all_templates())}")
    print(f"  - Notes: {db.get_notes_count()}")
    print(f"  - Favorites: {len(db.get_favorite_notes())}")
    print(f"  - Daily Notes: {len(db.get_all_daily_notes())}")

    db.close()
    return True


if __name__ == "__main__":
    success = test_enhanced_features()
    sys.exit(0 if success else 1)
