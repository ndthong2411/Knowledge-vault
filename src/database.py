"""
Database operations for Knowledge Vault
Handles SQLite database with FTS5 for full-text search and vector storage for semantic search
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np

from config import DB_PATH


class Database:
    """Database manager for Knowledge Vault"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def _initialize_db(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                file_path TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                view_count INTEGER DEFAULT 0
            )
        """)

        # Create tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create note_tags junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (note_id, tag_id)
            )
        """)

        # Create embeddings table for semantic search
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                note_id INTEGER PRIMARY KEY,
                embedding BLOB NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
            )
        """)

        # Create FTS5 virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
                title,
                content,
                content='notes',
                content_rowid='id'
            )
        """)

        # Create triggers to keep FTS in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
                INSERT INTO notes_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
                DELETE FROM notes_fts WHERE rowid = old.id;
            END
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
                UPDATE notes_fts
                SET title = new.title, content = new.content
                WHERE rowid = new.id;
            END
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_created ON notes(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(updated_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")

        conn.commit()

    def create_note(self, title: str, content: str, file_path: str, tags: List[str] = None) -> int:
        """Create a new note"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Insert note
            cursor.execute("""
                INSERT INTO notes (title, content, file_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (title, content, file_path, datetime.now(), datetime.now()))

            note_id = cursor.lastrowid

            # Add tags if provided
            if tags:
                self._add_tags_to_note(note_id, tags, cursor)

            conn.commit()
            return note_id
        except Exception as e:
            conn.rollback()
            raise e

    def get_note(self, note_id: int) -> Optional[Dict]:
        """Get a note by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()

        if not row:
            return None

        note = dict(row)
        note['tags'] = self.get_note_tags(note_id)

        # Increment view count
        cursor.execute("UPDATE notes SET view_count = view_count + 1 WHERE id = ?", (note_id,))
        conn.commit()

        return note

    def get_note_by_path(self, file_path: str) -> Optional[Dict]:
        """Get a note by file path"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM notes WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()

        if not row:
            return None

        note = dict(row)
        note['tags'] = self.get_note_tags(note['id'])

        return note

    def update_note(self, note_id: int, title: str = None, content: str = None,
                   tags: List[str] = None) -> bool:
        """Update a note"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build update query dynamically
            updates = []
            params = []

            if title is not None:
                updates.append("title = ?")
                params.append(title)

            if content is not None:
                updates.append("content = ?")
                params.append(content)

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now())
                params.append(note_id)

                query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)

            # Update tags if provided
            if tags is not None:
                # Remove old tags
                cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
                # Add new tags
                self._add_tags_to_note(note_id, tags, cursor)

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e

    def delete_note(self, note_id: int) -> bool:
        """Delete a note"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e

    def get_all_notes(self, limit: int = None, offset: int = 0,
                     order_by: str = "updated_at", order_dir: str = "DESC") -> List[Dict]:
        """Get all notes with pagination"""
        conn = self._get_connection()
        cursor = conn.cursor()

        valid_orders = ["created_at", "updated_at", "title", "view_count"]
        if order_by not in valid_orders:
            order_by = "updated_at"

        order_dir = "DESC" if order_dir.upper() == "DESC" else "ASC"

        query = f"SELECT * FROM notes ORDER BY {order_by} {order_dir}"

        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"

        cursor.execute(query)
        notes = [dict(row) for row in cursor.fetchall()]

        # Add tags to each note
        for note in notes:
            note['tags'] = self.get_note_tags(note['id'])

        return notes

    def get_notes_count(self) -> int:
        """Get total number of notes"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notes")
        return cursor.fetchone()[0]

    def full_text_search(self, query: str, limit: int = 50) -> List[Dict]:
        """Full-text search using FTS5"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Use FTS5 MATCH for full-text search
        cursor.execute("""
            SELECT n.*, rank
            FROM notes n
            JOIN notes_fts ON n.id = notes_fts.rowid
            WHERE notes_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))

        notes = [dict(row) for row in cursor.fetchall()]

        # Add tags to each note
        for note in notes:
            note['tags'] = self.get_note_tags(note['id'])

        return notes

    def save_embedding(self, note_id: int, embedding: np.ndarray):
        """Save note embedding for semantic search"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Convert numpy array to bytes
        embedding_bytes = embedding.tobytes()

        cursor.execute("""
            INSERT OR REPLACE INTO embeddings (note_id, embedding)
            VALUES (?, ?)
        """, (note_id, embedding_bytes))

        conn.commit()

    def get_embedding(self, note_id: int) -> Optional[np.ndarray]:
        """Get note embedding"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT embedding FROM embeddings WHERE note_id = ?", (note_id,))
        row = cursor.fetchone()

        if not row:
            return None

        # Convert bytes back to numpy array
        from config import EMBEDDING_DIM
        return np.frombuffer(row[0], dtype=np.float32).reshape(EMBEDDING_DIM)

    def get_all_embeddings(self) -> List[Tuple[int, np.ndarray]]:
        """Get all embeddings for semantic search"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT note_id, embedding FROM embeddings")

        from config import EMBEDDING_DIM
        embeddings = []
        for row in cursor.fetchall():
            note_id = row[0]
            embedding = np.frombuffer(row[1], dtype=np.float32).reshape(EMBEDDING_DIM)
            embeddings.append((note_id, embedding))

        return embeddings

    def _add_tags_to_note(self, note_id: int, tags: List[str], cursor):
        """Helper method to add tags to a note"""
        for tag_name in tags:
            tag_name = tag_name.strip().lower()
            if not tag_name:
                continue

            # Insert tag if not exists
            cursor.execute("""
                INSERT OR IGNORE INTO tags (name) VALUES (?)
            """, (tag_name,))

            # Get tag id
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = cursor.fetchone()[0]

            # Link tag to note
            cursor.execute("""
                INSERT OR IGNORE INTO note_tags (note_id, tag_id)
                VALUES (?, ?)
            """, (note_id, tag_id))

    def get_note_tags(self, note_id: int) -> List[str]:
        """Get tags for a note"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.name
            FROM tags t
            JOIN note_tags nt ON t.id = nt.tag_id
            WHERE nt.note_id = ?
            ORDER BY t.name
        """, (note_id,))

        return [row[0] for row in cursor.fetchall()]

    def get_all_tags(self) -> List[Dict]:
        """Get all tags with usage count"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.name, COUNT(nt.note_id) as count
            FROM tags t
            LEFT JOIN note_tags nt ON t.id = nt.tag_id
            GROUP BY t.id, t.name
            ORDER BY count DESC, t.name
        """)

        return [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]

    def search_by_tags(self, tags: List[str], match_all: bool = False) -> List[Dict]:
        """Search notes by tags"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if not tags:
            return []

        tags = [tag.strip().lower() for tag in tags]

        if match_all:
            # Match all tags (AND)
            placeholders = ','.join('?' * len(tags))
            cursor.execute(f"""
                SELECT n.*, COUNT(DISTINCT t.id) as matched_tags
                FROM notes n
                JOIN note_tags nt ON n.id = nt.note_id
                JOIN tags t ON nt.tag_id = t.id
                WHERE t.name IN ({placeholders})
                GROUP BY n.id
                HAVING matched_tags = ?
                ORDER BY n.updated_at DESC
            """, tags + [len(tags)])
        else:
            # Match any tag (OR)
            placeholders = ','.join('?' * len(tags))
            cursor.execute(f"""
                SELECT DISTINCT n.*
                FROM notes n
                JOIN note_tags nt ON n.id = nt.note_id
                JOIN tags t ON nt.tag_id = t.id
                WHERE t.name IN ({placeholders})
                ORDER BY n.updated_at DESC
            """, tags)

        notes = [dict(row) for row in cursor.fetchall()]

        # Add tags to each note
        for note in notes:
            note['tags'] = self.get_note_tags(note['id'])

        return notes

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        # Total notes
        cursor.execute("SELECT COUNT(*) FROM notes")
        stats['total_notes'] = cursor.fetchone()[0]

        # Total tags
        cursor.execute("SELECT COUNT(*) FROM tags")
        stats['total_tags'] = cursor.fetchone()[0]

        # Notes with embeddings
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        stats['notes_with_embeddings'] = cursor.fetchone()[0]

        # Most viewed notes
        cursor.execute("""
            SELECT id, title, view_count
            FROM notes
            ORDER BY view_count DESC
            LIMIT 5
        """)
        stats['most_viewed'] = [dict(row) for row in cursor.fetchall()]

        # Recent notes
        cursor.execute("""
            SELECT id, title, created_at
            FROM notes
            ORDER BY created_at DESC
            LIMIT 5
        """)
        stats['recent_notes'] = [dict(row) for row in cursor.fetchall()]

        return stats

    # ==================== FOLDERS ====================

    def create_folder(self, name: str, parent_id: int = None, color: str = '#4CAF50', icon: str = '📁') -> int:
        """Create a new folder"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO folders (name, parent_id, color, icon)
            VALUES (?, ?, ?, ?)
        """, (name, parent_id, color, icon))

        conn.commit()
        return cursor.lastrowid

    def get_all_folders(self) -> List[Dict]:
        """Get all folders with note counts"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT f.*, COUNT(n.id) as note_count
            FROM folders f
            LEFT JOIN notes n ON f.id = n.folder_id
            GROUP BY f.id
            ORDER BY f.name
        """)

        return [dict(row) for row in cursor.fetchall()]

    def move_note_to_folder(self, note_id: int, folder_id: int = None) -> bool:
        """Move a note to a folder"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE notes SET folder_id = ? WHERE id = ?", (folder_id, note_id))
        conn.commit()
        return True

    def get_notes_in_folder(self, folder_id: int = None) -> List[Dict]:
        """Get all notes in a folder (None = no folder)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if folder_id is None:
            cursor.execute("SELECT * FROM notes WHERE folder_id IS NULL ORDER BY updated_at DESC")
        else:
            cursor.execute("SELECT * FROM notes WHERE folder_id = ? ORDER BY updated_at DESC", (folder_id,))

        notes = [dict(row) for row in cursor.fetchall()]

        for note in notes:
            note['tags'] = self.get_note_tags(note['id'])

        return notes

    def delete_folder(self, folder_id: int) -> bool:
        """Delete a folder (notes will be moved to no folder)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Move notes to no folder
        cursor.execute("UPDATE notes SET folder_id = NULL WHERE folder_id = ?", (folder_id,))

        # Delete folder
        cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))

        conn.commit()
        return True

    # ==================== BACKLINKS ====================

    def add_note_link(self, source_note_id: int, target_note_id: int, link_text: str = None) -> bool:
        """Add a link between notes"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR IGNORE INTO note_links (source_note_id, target_note_id, link_text)
                VALUES (?, ?, ?)
            """, (source_note_id, target_note_id, link_text))
            conn.commit()
            return True
        except:
            return False

    def get_note_links(self, note_id: int) -> Dict:
        """Get all links for a note (outgoing and incoming)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Outgoing links (this note links to others)
        cursor.execute("""
            SELECT nl.*, n.title, n.id
            FROM note_links nl
            JOIN notes n ON nl.target_note_id = n.id
            WHERE nl.source_note_id = ?
        """, (note_id,))
        outgoing = [dict(row) for row in cursor.fetchall()]

        # Incoming links (backlinks - others link to this note)
        cursor.execute("""
            SELECT nl.*, n.title, n.id
            FROM note_links nl
            JOIN notes n ON nl.source_note_id = n.id
            WHERE nl.target_note_id = ?
        """, (note_id,))
        incoming = [dict(row) for row in cursor.fetchall()]

        return {
            'outgoing': outgoing,
            'incoming': incoming
        }

    def remove_note_link(self, source_note_id: int, target_note_id: int) -> bool:
        """Remove a link between notes"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM note_links WHERE source_note_id = ? AND target_note_id = ?
        """, (source_note_id, target_note_id))

        conn.commit()
        return True

    def get_graph_data(self) -> Dict:
        """Get all notes and links for graph visualization"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get all notes
        cursor.execute("SELECT id, title FROM notes")
        nodes = [{'id': row[0], 'title': row[1]} for row in cursor.fetchall()]

        # Get all links
        cursor.execute("SELECT source_note_id, target_note_id FROM note_links")
        links = [{'source': row[0], 'target': row[1]} for row in cursor.fetchall()]

        return {'nodes': nodes, 'links': links}

    # ==================== FAVORITES ====================

    def toggle_favorite(self, note_id: int) -> bool:
        """Toggle favorite status of a note"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT is_favorite FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()

        if row is None:
            return False

        new_status = 0 if row[0] == 1 else 1
        cursor.execute("UPDATE notes SET is_favorite = ? WHERE id = ?", (new_status, note_id))
        conn.commit()

        return True

    def get_favorite_notes(self) -> List[Dict]:
        """Get all favorite notes"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM notes WHERE is_favorite = 1 ORDER BY updated_at DESC")
        notes = [dict(row) for row in cursor.fetchall()]

        for note in notes:
            note['tags'] = self.get_note_tags(note['id'])

        return notes

    # ==================== VERSION HISTORY ====================

    def save_version(self, note_id: int, title: str, content: str) -> int:
        """Save a version of a note"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get current version number
        cursor.execute("""
            SELECT MAX(version_number) FROM note_versions WHERE note_id = ?
        """, (note_id,))
        row = cursor.fetchone()
        next_version = (row[0] or 0) + 1

        # Save version
        cursor.execute("""
            INSERT INTO note_versions (note_id, title, content, version_number)
            VALUES (?, ?, ?, ?)
        """, (note_id, title, content, next_version))

        conn.commit()
        return cursor.lastrowid

    def get_note_versions(self, note_id: int) -> List[Dict]:
        """Get all versions of a note"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM note_versions
            WHERE note_id = ?
            ORDER BY version_number DESC
        """, (note_id,))

        return [dict(row) for row in cursor.fetchall()]

    def restore_version(self, note_id: int, version_id: int) -> bool:
        """Restore a note to a previous version"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get version
        cursor.execute("SELECT title, content FROM note_versions WHERE id = ?", (version_id,))
        row = cursor.fetchone()

        if not row:
            return False

        # Update note
        cursor.execute("""
            UPDATE notes SET title = ?, content = ?, updated_at = ?
            WHERE id = ?
        """, (row[0], row[1], datetime.now(), note_id))

        conn.commit()
        return True

    # ==================== TEMPLATES ====================

    def get_all_templates(self) -> List[Dict]:
        """Get all note templates"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM templates ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def get_template(self, template_id: int) -> Optional[Dict]:
        """Get a specific template"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()

        return dict(row) if row else None

    def create_template(self, name: str, content: str, description: str = None,
                       tags: str = '', icon: str = '📄') -> int:
        """Create a new template"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO templates (name, description, content, tags, icon)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, content, tags, icon))

        conn.commit()
        return cursor.lastrowid

    def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        conn.commit()

        return cursor.rowcount > 0

    # ==================== DAILY NOTES ====================

    def get_or_create_daily_note(self, date: str = None) -> Dict:
        """Get or create daily note for a specific date"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        title = f"Daily Note - {date}"

        # Check if exists
        cursor.execute("""
            SELECT * FROM notes WHERE title = ? AND is_daily_note = 1
        """, (title,))
        row = cursor.fetchone()

        if row:
            note = dict(row)
            note['tags'] = self.get_note_tags(note['id'])
            return note

        # Create new daily note
        content = f"""# {title}

## Tasks
- [ ]

## Notes


## Reflections


"""
        file_path = f"data/notes/daily-{date}.md"

        note_id = self.create_note(title, content, file_path, ['daily'])

        # Mark as daily note
        cursor.execute("UPDATE notes SET is_daily_note = 1 WHERE id = ?", (note_id,))
        conn.commit()

        return self.get_note(note_id)

    def get_all_daily_notes(self, limit: int = 30) -> List[Dict]:
        """Get recent daily notes"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM notes WHERE is_daily_note = 1
            ORDER BY created_at DESC LIMIT ?
        """, (limit,))

        notes = [dict(row) for row in cursor.fetchall()]

        for note in notes:
            note['tags'] = self.get_note_tags(note['id'])

        return notes

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
