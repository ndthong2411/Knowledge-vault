"""
Backlinks system for Knowledge Vault
Handles [[wiki-style]] links between notes
"""
import re
from typing import List, Dict, Tuple, Set
from src.database import Database


class BacklinksParser:
    """Parse and manage backlinks between notes"""

    def __init__(self, db: Database):
        self.db = db
        # Pattern for [[Note Title]] or [[note-id]]
        self.link_pattern = re.compile(r'\[\[([^\]]+)\]\]')

    def parse_links(self, content: str) -> List[str]:
        """
        Extract all [[links]] from content
        Returns list of link texts
        """
        matches = self.link_pattern.findall(content)
        return [match.strip() for match in matches]

    def process_note_links(self, note_id: int, content: str) -> Dict:
        """
        Process all links in a note's content
        Creates bidirectional links in database
        Returns dict with found and missing links
        """
        link_texts = self.parse_links(content)

        if not link_texts:
            return {'found': [], 'missing': []}

        # Get all notes for matching
        all_notes = self.db.get_all_notes()
        note_map = {note['title'].lower(): note for note in all_notes}

        # Also support note IDs as links
        note_id_map = {str(note['id']): note for note in all_notes}

        found_links = []
        missing_links = []

        for link_text in link_texts:
            # Try to match by title (case-insensitive)
            target_note = note_map.get(link_text.lower())

            # Try to match by ID
            if not target_note:
                target_note = note_id_map.get(link_text)

            if target_note and target_note['id'] != note_id:
                # Create link in database
                self.db.add_note_link(note_id, target_note['id'], link_text)
                found_links.append({
                    'text': link_text,
                    'target_id': target_note['id'],
                    'target_title': target_note['title']
                })
            else:
                missing_links.append(link_text)

        return {
            'found': found_links,
            'missing': missing_links
        }

    def render_content_with_links(self, content: str, note_id: int = None) -> str:
        """
        Convert [[links]] to clickable HTML links
        Returns HTML with links rendered
        """
        all_notes = self.db.get_all_notes()
        note_map = {note['title'].lower(): note for note in all_notes}
        note_id_map = {str(note['id']): note for note in all_notes}

        def replace_link(match):
            link_text = match.group(1).strip()

            # Try to find note
            target_note = note_map.get(link_text.lower())
            if not target_note:
                target_note = note_id_map.get(link_text)

            if target_note:
                # Create clickable link
                return f'<a href="#" class="wiki-link" data-note-id="{target_note["id"]}">{link_text}</a>'
            else:
                # Broken link
                return f'<span class="wiki-link-broken" title="Note not found">{link_text}</span>'

        return self.link_pattern.sub(replace_link, content)

    def get_orphan_notes(self) -> List[Dict]:
        """
        Get notes that have no incoming or outgoing links
        """
        all_notes = self.db.get_all_notes()
        orphans = []

        for note in all_notes:
            links = self.db.get_note_links(note['id'])
            if not links['incoming'] and not links['outgoing']:
                orphans.append(note)

        return orphans

    def get_most_linked_notes(self, limit: int = 10) -> List[Dict]:
        """
        Get notes with the most backlinks (most referenced)
        """
        all_notes = self.db.get_all_notes()

        notes_with_counts = []
        for note in all_notes:
            links = self.db.get_note_links(note['id'])
            backlink_count = len(links['incoming'])
            notes_with_counts.append({
                **note,
                'backlink_count': backlink_count
            })

        # Sort by backlink count
        notes_with_counts.sort(key=lambda x: x['backlink_count'], reverse=True)

        return notes_with_counts[:limit]

    def suggest_links(self, content: str, current_note_id: int = None, limit: int = 5) -> List[Dict]:
        """
        Suggest notes that might be relevant to link based on content
        Uses keyword matching
        """
        # Extract important words (simple approach)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [word for word, _ in top_keywords]

        # Find notes containing these keywords
        all_notes = self.db.get_all_notes()
        suggestions = []

        for note in all_notes:
            if current_note_id and note['id'] == current_note_id:
                continue

            # Count matching keywords in note
            note_text = (note['title'] + ' ' + note['content']).lower()
            matches = sum(1 for keyword in keywords if keyword in note_text)

            if matches > 0:
                suggestions.append({
                    'note': note,
                    'relevance': matches
                })

        # Sort by relevance
        suggestions.sort(key=lambda x: x['relevance'], reverse=True)

        return [s['note'] for s in suggestions[:limit]]

    def create_link_at_cursor(self, content: str, cursor_position: int, note_title: str) -> str:
        """
        Insert a [[link]] at cursor position
        """
        link = f"[[{note_title}]]"
        new_content = content[:cursor_position] + link + content[cursor_position:]
        return new_content

    def get_broken_links(self) -> List[Dict]:
        """
        Find all notes with broken [[links]] (links to non-existent notes)
        """
        all_notes = self.db.get_all_notes()
        broken_links_notes = []

        for note in all_notes:
            result = self.process_note_links(note['id'], note['content'])
            if result['missing']:
                broken_links_notes.append({
                    'note': note,
                    'broken_links': result['missing']
                })

        return broken_links_notes

    def bulk_update_links(self):
        """
        Update all links for all notes
        Useful when notes are renamed or reorganized
        """
        all_notes = self.db.get_all_notes()

        updated_count = 0
        for note in all_notes:
            # Clear existing links from this note
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM note_links WHERE source_note_id = ?", (note['id'],))
            conn.commit()

            # Reprocess links
            self.process_note_links(note['id'], note['content'])
            updated_count += 1

        return updated_count
