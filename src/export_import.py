"""
Export and Import functionality for Knowledge Vault
Supports: Markdown, JSON, PDF
"""
import json
import zipfile
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import io

from src.database import Database
from src.storage import Storage


class ExportImport:
    """Handle export and import operations"""

    def __init__(self, db: Database, storage: Storage):
        self.db = db
        self.storage = storage

    # ==================== EXPORT ====================

    def export_note_markdown(self, note_id: int, output_path: str = None) -> str:
        """Export a single note as markdown"""
        note = self.db.get_note(note_id)
        if not note:
            raise ValueError(f"Note {note_id} not found")

        # Build markdown with frontmatter
        tags_str = ", ".join(note.get('tags', []))

        markdown_content = f"""---
title: {note['title']}
created: {note['created_at']}
updated: {note['updated_at']}
tags: [{tags_str}]
---

{note['content']}
"""

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

        return markdown_content

    def export_note_json(self, note_id: int) -> str:
        """Export a single note as JSON"""
        note = self.db.get_note(note_id)
        if not note:
            raise ValueError(f"Note {note_id} not found")

        # Get additional data
        links = self.db.get_note_links(note_id)
        versions = self.db.get_note_versions(note_id)

        export_data = {
            'note': {
                'id': note['id'],
                'title': note['title'],
                'content': note['content'],
                'tags': note.get('tags', []),
                'created_at': note['created_at'],
                'updated_at': note['updated_at'],
                'is_favorite': note.get('is_favorite', 0),
                'folder_id': note.get('folder_id')
            },
            'links': links,
            'versions': versions,
            'exported_at': datetime.now().isoformat()
        }

        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def export_all_notes_zip(self, output_path: str, format: str = 'markdown') -> str:
        """
        Export all notes as a ZIP file
        Format: 'markdown' or 'json'
        """
        all_notes = self.db.get_all_notes()

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Export each note
            for note in all_notes:
                if format == 'markdown':
                    content = self.export_note_markdown(note['id'])
                    filename = f"{note['id']}_{note['title'][:50]}.md"
                else:
                    content = self.export_note_json(note['id'])
                    filename = f"{note['id']}_{note['title'][:50]}.json"

                # Sanitize filename
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                zipf.writestr(f"notes/{filename}", content)

            # Export metadata
            metadata = {
                'total_notes': len(all_notes),
                'exported_at': datetime.now().isoformat(),
                'format': format,
                'version': '1.0'
            }
            zipf.writestr('metadata.json', json.dumps(metadata, indent=2))

        return output_path

    def export_folder_to_zip(self, folder_id: int, output_path: str) -> str:
        """Export all notes in a folder as ZIP"""
        notes = self.db.get_notes_in_folder(folder_id)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for note in notes:
                content = self.export_note_markdown(note['id'])
                filename = f"{note['id']}_{note['title'][:50]}.md"
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                zipf.writestr(filename, content)

        return output_path

    def export_to_obsidian_format(self, output_dir: str):
        """
        Export all notes in Obsidian-compatible format
        - Uses [[links]] syntax
        - Markdown files with frontmatter
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        all_notes = self.db.get_all_notes()

        for note in all_notes:
            # Create markdown with Obsidian frontmatter
            tags_str = "\n".join([f"  - {tag}" for tag in note.get('tags', [])])

            content = f"""---
tags:
{tags_str}
created: {note['created_at']}
updated: {note['updated_at']}
---

# {note['title']}

{note['content']}
"""

            # Save to file
            filename = f"{note['title']}.md"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
            file_path = output_path / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return str(output_path)

    # ==================== IMPORT ====================

    def import_note_markdown(self, file_path: str, tags: List[str] = None) -> int:
        """Import a markdown file as a new note"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to parse frontmatter
        title = Path(file_path).stem
        note_content = content

        # Simple frontmatter parsing
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                note_content = parts[2].strip()

                # Extract title from frontmatter
                for line in frontmatter.split('\n'):
                    if line.startswith('title:'):
                        title = line.split('title:', 1)[1].strip()
                        break

                # Extract tags from frontmatter
                if tags is None:
                    tags = []
                    in_tags = False
                    for line in frontmatter.split('\n'):
                        if line.startswith('tags:'):
                            tag_content = line.split('tags:', 1)[1].strip()
                            if tag_content:
                                # Parse inline tags
                                tags = [t.strip() for t in tag_content.strip('[]').split(',')]
                            in_tags = True
                        elif in_tags and line.strip().startswith('-'):
                            tags.append(line.strip('- ').strip())

        # Create note
        file_path_rel = self.storage.create_note_file(title, note_content, tags)
        note_id = self.db.create_note(title, note_content, file_path_rel, tags)

        return note_id

    def import_note_json(self, json_content: str) -> int:
        """Import a note from JSON"""
        data = json.loads(json_content)
        note_data = data.get('note', {})

        # Create note
        file_path = self.storage.create_note_file(
            note_data['title'],
            note_data['content'],
            note_data.get('tags', [])
        )

        note_id = self.db.create_note(
            note_data['title'],
            note_data['content'],
            file_path,
            note_data.get('tags', [])
        )

        # Set favorite status
        if note_data.get('is_favorite'):
            self.db.toggle_favorite(note_id)

        # Import versions if present
        if 'versions' in data:
            for version in data['versions']:
                self.db.save_version(
                    note_id,
                    version['title'],
                    version['content']
                )

        return note_id

    def import_from_zip(self, zip_path: str) -> Dict:
        """Import notes from a ZIP file"""
        imported_notes = []
        errors = []

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Check format from metadata
            try:
                metadata_content = zipf.read('metadata.json').decode('utf-8')
                metadata = json.loads(metadata_content)
                format_type = metadata.get('format', 'markdown')
            except:
                format_type = 'markdown'

            # Import each file
            for file_info in zipf.filelist:
                if file_info.filename == 'metadata.json':
                    continue

                if file_info.filename.startswith('notes/') or not file_info.filename.startswith('__'):
                    try:
                        content = zipf.read(file_info.filename).decode('utf-8')

                        if file_info.filename.endswith('.json'):
                            note_id = self.import_note_json(content)
                        else:
                            # Create temporary file
                            import tempfile
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp:
                                tmp.write(content)
                                tmp_path = tmp.name

                            note_id = self.import_note_markdown(tmp_path)
                            Path(tmp_path).unlink()

                        imported_notes.append(note_id)
                    except Exception as e:
                        errors.append({
                            'file': file_info.filename,
                            'error': str(e)
                        })

        return {
            'imported': len(imported_notes),
            'note_ids': imported_notes,
            'errors': errors
        }

    def import_from_obsidian_vault(self, vault_path: str) -> Dict:
        """
        Import notes from an Obsidian vault
        Handles [[wiki-links]] and frontmatter
        """
        vault = Path(vault_path)
        imported_notes = []
        errors = []

        # Find all markdown files
        md_files = list(vault.rglob('*.md'))

        for md_file in md_files:
            try:
                note_id = self.import_note_markdown(str(md_file))
                imported_notes.append(note_id)
            except Exception as e:
                errors.append({
                    'file': str(md_file),
                    'error': str(e)
                })

        # After importing, process backlinks
        from src.backlinks import BacklinksParser
        parser = BacklinksParser(self.db)

        for note_id in imported_notes:
            note = self.db.get_note(note_id)
            if note:
                parser.process_note_links(note_id, note['content'])

        return {
            'imported': len(imported_notes),
            'note_ids': imported_notes,
            'errors': errors
        }

    def import_from_notion(self, export_path: str) -> Dict:
        """
        Import notes from Notion export (ZIP file)
        Notion exports as markdown with frontmatter
        """
        # Notion exports are ZIP files with markdown
        return self.import_from_zip(export_path)
