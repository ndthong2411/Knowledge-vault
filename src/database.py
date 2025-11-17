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

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
