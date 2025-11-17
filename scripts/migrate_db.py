"""
Database migration to add new features:
- Folders/Collections
- Backlinks
- Favorites
- Version History
- Templates
"""
import sqlite3
from pathlib import Path
from config import DB_PATH


def migrate_database(db_path: Path = DB_PATH):
    """Run database migrations"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("🔄 Running database migrations...")

    # 1. Add columns to notes table
    try:
        cursor.execute("ALTER TABLE notes ADD COLUMN is_favorite INTEGER DEFAULT 0")
        print("  ✅ Added is_favorite column to notes")
    except sqlite3.OperationalError:
        print("  ⏭️  is_favorite column already exists")

    try:
        cursor.execute("ALTER TABLE notes ADD COLUMN is_daily_note INTEGER DEFAULT 0")
        print("  ✅ Added is_daily_note column to notes")
    except sqlite3.OperationalError:
        print("  ⏭️  is_daily_note column already exists")

    try:
        cursor.execute("ALTER TABLE notes ADD COLUMN folder_id INTEGER")
        print("  ✅ Added folder_id column to notes")
    except sqlite3.OperationalError:
        print("  ⏭️  folder_id column already exists")

    # 2. Create folders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            color TEXT DEFAULT '#4CAF50',
            icon TEXT DEFAULT '📁',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
        )
    """)
    print("  ✅ Created folders table")

    # 3. Create note_links table for backlinks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_note_id INTEGER NOT NULL,
            target_note_id INTEGER NOT NULL,
            link_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY (target_note_id) REFERENCES notes(id) ON DELETE CASCADE,
            UNIQUE(source_note_id, target_note_id)
        )
    """)
    print("  ✅ Created note_links table for backlinks")

    # 4. Create note_versions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            version_number INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
    """)
    print("  ✅ Created note_versions table")

    # 5. Create templates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            content TEXT NOT NULL,
            tags TEXT,
            icon TEXT DEFAULT '📄',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✅ Created templates table")

    # 6. Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_folder ON notes(folder_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_favorite ON notes(is_favorite)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_daily ON notes(is_daily_note)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_source ON note_links(source_note_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_target ON note_links(target_note_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_versions_note ON note_versions(note_id)")
    print("  ✅ Created indexes")

    # 7. Insert default templates
    default_templates = [
        {
            'name': 'Blank Note',
            'description': 'Empty note with no formatting',
            'content': '',
            'tags': '',
            'icon': '📄'
        },
        {
            'name': 'Meeting Notes',
            'description': 'Template for meeting notes',
            'content': '''# Meeting Notes - {date}

## Attendees
-

## Agenda
1.

## Discussion
-

## Action Items
- [ ]

## Next Meeting
- Date:
- Topics:
''',
            'tags': 'meeting,work',
            'icon': '📋'
        },
        {
            'name': 'Book Review',
            'description': 'Template for book reviews',
            'content': '''# Book Review: [Book Title]

## Information
- **Author**:
- **Genre**:
- **Pages**:
- **Rating**: ⭐⭐⭐⭐⭐

## Summary


## Key Takeaways
1.
2.
3.

## Favorite Quotes
>

## My Thoughts


## Would I Recommend?

''',
            'tags': 'book,review',
            'icon': '📚'
        },
        {
            'name': 'Project Plan',
            'description': 'Template for project planning',
            'content': '''# Project: [Project Name]

## Overview


## Goals
1.
2.
3.

## Timeline
- Start Date:
- End Date:
- Milestones:
  - [ ]

## Resources Needed
-

## Risks & Challenges
-

## Success Criteria
-

## Notes

''',
            'tags': 'project,planning',
            'icon': '🎯'
        },
        {
            'name': 'Learning Notes',
            'description': 'Template for learning and study notes',
            'content': '''# Learning: [Topic]

## Date: {date}

## What I'm Learning


## Key Concepts
1.
2.
3.

## Examples


## Questions
-

## Resources
-

## Next Steps
- [ ]

''',
            'tags': 'learning,education',
            'icon': '🎓'
        },
        {
            'name': 'Daily Journal',
            'description': 'Template for daily journaling',
            'content': '''# Daily Journal - {date}

## 🌅 Morning
**Mood**:
**Goals for today**:
- [ ]
- [ ]

## 💭 Thoughts & Events


## ✅ Accomplishments
-

## 📚 What I Learned


## 🌙 Evening Reflection
**Mood**:
**Grateful for**:

## Tomorrow
- [ ]

''',
            'tags': 'journal,daily',
            'icon': '📓'
        }
    ]

    for template in default_templates:
        cursor.execute("""
            INSERT OR IGNORE INTO templates (name, description, content, tags, icon)
            VALUES (?, ?, ?, ?, ?)
        """, (template['name'], template['description'], template['content'],
              template['tags'], template['icon']))

    print(f"  ✅ Inserted {len(default_templates)} default templates")

    # 8. Create default folders
    default_folders = [
        {'name': 'Personal', 'icon': '👤', 'color': '#2196F3'},
        {'name': 'Work', 'icon': '💼', 'color': '#FF9800'},
        {'name': 'Projects', 'icon': '🎯', 'color': '#9C27B0'},
        {'name': 'Learning', 'icon': '🎓', 'color': '#4CAF50'},
        {'name': 'Archive', 'icon': '📦', 'color': '#757575'},
    ]

    for folder in default_folders:
        cursor.execute("""
            INSERT OR IGNORE INTO folders (name, icon, color)
            VALUES (?, ?, ?)
        """, (folder['name'], folder['icon'], folder['color']))

    print(f"  ✅ Inserted {len(default_folders)} default folders")

    conn.commit()
    conn.close()

    print("✅ Database migration completed!")


if __name__ == "__main__":
    migrate_database()
