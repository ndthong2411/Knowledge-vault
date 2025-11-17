"""
File storage operations for Knowledge Vault
Handles markdown file creation, reading, updating, and deletion
"""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import frontmatter

from config import NOTES_DIR


class Storage:
    """File storage manager for notes"""

    def __init__(self, notes_dir: Path = NOTES_DIR):
        self.notes_dir = notes_dir
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def create_note_file(self, title: str, content: str, tags: List[str] = None) -> str:
        """
        Create a markdown file for a note with frontmatter metadata
        Returns the file path
        """
        # Generate filename from title
        filename = self._generate_filename(title)
        file_path = self.notes_dir / filename

        # Ensure unique filename
        counter = 1
        while file_path.exists():
            name_without_ext = filename.rsplit('.', 1)[0]
            file_path = self.notes_dir / f"{name_without_ext}_{counter}.md"
            counter += 1

        # Create frontmatter
        metadata = {
            'title': title,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tags': tags or []
        }

        # Create post with frontmatter
        post = frontmatter.Post(content, **metadata)

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

        return str(file_path.relative_to(self.notes_dir.parent))

    def read_note_file(self, file_path: str) -> Optional[Dict]:
        """
        Read a markdown file and return its content and metadata
        """
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = self.notes_dir.parent / file_path

        if not full_path.exists():
            return None

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            return {
                'title': post.get('title', ''),
                'content': post.content,
                'tags': post.get('tags', []),
                'created_at': post.get('created_at'),
                'updated_at': post.get('updated_at'),
                'file_path': str(full_path.relative_to(self.notes_dir.parent))
            }
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def update_note_file(self, file_path: str, title: str = None,
                        content: str = None, tags: List[str] = None) -> bool:
        """
        Update a markdown file
        """
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = self.notes_dir.parent / file_path

        if not full_path.exists():
            return False

        try:
            # Read existing file
            with open(full_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            # Update fields
            if title is not None:
                post['title'] = title
            if content is not None:
                post.content = content
            if tags is not None:
                post['tags'] = tags

            post['updated_at'] = datetime.now().isoformat()

            # Write back
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))

            return True
        except Exception as e:
            print(f"Error updating file {file_path}: {e}")
            return False

    def delete_note_file(self, file_path: str) -> bool:
        """
        Delete a markdown file
        """
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = self.notes_dir.parent / file_path

        if not full_path.exists():
            return False

        try:
            full_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    def get_all_note_files(self) -> List[str]:
        """
        Get all markdown files in the notes directory
        """
        md_files = []
        for file_path in self.notes_dir.rglob('*.md'):
            if file_path.name != '.gitkeep':
                md_files.append(str(file_path.relative_to(self.notes_dir.parent)))
        return sorted(md_files)

    def _generate_filename(self, title: str) -> str:
        """
        Generate a safe filename from note title
        """
        # Remove special characters and replace spaces with hyphens
        filename = re.sub(r'[^\w\s-]', '', title.lower())
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = filename.strip('-')

        # Limit length
        if len(filename) > 50:
            filename = filename[:50]

        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename}_{timestamp}.md"

        return filename

    def import_note_from_file(self, source_path: str) -> Optional[str]:
        """
        Import a note from an external markdown file
        """
        source = Path(source_path)
        if not source.exists():
            return None

        try:
            # Read source file
            with open(source, 'r', encoding='utf-8') as f:
                try:
                    post = frontmatter.load(f)
                    title = post.get('title', source.stem)
                    content = post.content
                    tags = post.get('tags', [])
                except:
                    # If no frontmatter, use entire content
                    f.seek(0)
                    content = f.read()
                    title = source.stem
                    tags = []

            # Create new note
            return self.create_note_file(title, content, tags)
        except Exception as e:
            print(f"Error importing file {source_path}: {e}")
            return None

    def export_note_to_file(self, file_path: str, destination: str) -> bool:
        """
        Export a note to an external location
        """
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = self.notes_dir.parent / file_path

        if not full_path.exists():
            return False

        try:
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            import shutil
            shutil.copy2(full_path, dest_path)
            return True
        except Exception as e:
            print(f"Error exporting file {file_path}: {e}")
            return False

    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics
        """
        total_files = 0
        total_size = 0

        for file_path in self.notes_dir.rglob('*.md'):
            if file_path.name != '.gitkeep':
                total_files += 1
                total_size += file_path.stat().st_size

        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
