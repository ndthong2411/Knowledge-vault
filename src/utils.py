"""
Utility functions for Knowledge Vault
"""
import re
from datetime import datetime
from typing import List, Dict, Any
import markdown


def format_datetime(dt: Any) -> str:
    """Format datetime for display"""
    if dt is None:
        return "N/A"

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt

    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    return str(dt)


def format_relative_time(dt: Any) -> str:
    """Format datetime as relative time (e.g., '2 hours ago')"""
    if dt is None:
        return "N/A"

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt

    if not isinstance(dt, datetime):
        return str(dt)

    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)].strip() + suffix


def highlight_text(text: str, query: str, max_context: int = 200) -> str:
    """
    Highlight search query in text and return context around first match
    """
    if not query or not text:
        return truncate_text(text, max_context)

    # Find first occurrence (case-insensitive)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    match = pattern.search(text)

    if not match:
        return truncate_text(text, max_context)

    start = match.start()
    end = match.end()

    # Get context around match
    context_start = max(0, start - max_context // 2)
    context_end = min(len(text), end + max_context // 2)

    context = text[context_start:context_end]

    # Add ellipsis if truncated
    if context_start > 0:
        context = "..." + context
    if context_end < len(text):
        context = context + "..."

    return context


def markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML"""
    try:
        html = markdown.markdown(
            text,
            extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
        )
        return html
    except:
        return text


def extract_summary(content: str, max_length: int = 200) -> str:
    """
    Extract a summary from note content
    Takes first paragraph or first N characters
    """
    if not content:
        return ""

    # Remove markdown formatting
    clean_text = re.sub(r'[#*_`\[\]()]', '', content)

    # Split into paragraphs
    paragraphs = [p.strip() for p in clean_text.split('\n\n') if p.strip()]

    if paragraphs:
        first_para = paragraphs[0]
        return truncate_text(first_para, max_length)

    return truncate_text(clean_text, max_length)


def validate_note_title(title: str) -> tuple[bool, str]:
    """
    Validate note title
    Returns (is_valid, error_message)
    """
    if not title:
        return False, "Title cannot be empty"

    if len(title) < 3:
        return False, "Title must be at least 3 characters"

    if len(title) > 200:
        return False, "Title must be less than 200 characters"

    return True, ""


def validate_note_content(content: str) -> tuple[bool, str]:
    """
    Validate note content
    Returns (is_valid, error_message)
    """
    if not content:
        return False, "Content cannot be empty"

    if len(content) < 10:
        return False, "Content must be at least 10 characters"

    return True, ""


def parse_tags_input(tags_input: str) -> List[str]:
    """
    Parse tags from comma-separated string or space-separated string
    """
    if not tags_input:
        return []

    # Split by comma or space
    if ',' in tags_input:
        tags = [tag.strip() for tag in tags_input.split(',')]
    else:
        tags = [tag.strip() for tag in tags_input.split()]

    # Filter out empty tags
    tags = [tag for tag in tags if tag]

    return tags


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove dangerous characters"""
    # Remove or replace dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized


def calculate_read_time(content: str, words_per_minute: int = 200) -> str:
    """
    Calculate estimated reading time for content
    """
    if not content:
        return "0 min"

    word_count = len(content.split())
    minutes = max(1, round(word_count / words_per_minute))

    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        else:
            return f"{hours}h"


def generate_note_preview(note: Dict) -> Dict:
    """
    Generate a preview dict for a note with formatted fields
    """
    return {
        'id': note.get('id'),
        'title': note.get('title', 'Untitled'),
        'summary': extract_summary(note.get('content', ''), 150),
        'tags': note.get('tags', []),
        'created_at': format_relative_time(note.get('created_at')),
        'updated_at': format_relative_time(note.get('updated_at')),
        'read_time': calculate_read_time(note.get('content', '')),
        'view_count': note.get('view_count', 0)
    }


def score_to_percentage(score: float) -> int:
    """Convert similarity score (0-1) to percentage"""
    return int(score * 100)


def format_search_score(note: Dict) -> str:
    """Format search scores for display"""
    scores = []

    if 'combined_score' in note:
        scores.append(f"Match: {score_to_percentage(note['combined_score'])}%")

    if 'keyword_score' in note and note['keyword_score'] > 0:
        scores.append(f"Keyword: {score_to_percentage(note['keyword_score'])}%")

    if 'semantic_score' in note and note['semantic_score'] > 0:
        scores.append(f"Semantic: {score_to_percentage(note['semantic_score'])}%")

    if 'similarity_score' in note:
        scores.append(f"Similarity: {score_to_percentage(note['similarity_score'])}%")

    return " | ".join(scores) if scores else ""


def get_tag_cloud_data(tags: List[Dict]) -> List[Dict]:
    """
    Prepare tag data for tag cloud visualization
    Returns list with normalized sizes
    """
    if not tags:
        return []

    max_count = max(tag['count'] for tag in tags) if tags else 1

    cloud_data = []
    for tag in tags:
        # Normalize size between 1 and 5
        size = 1 + (tag['count'] / max_count) * 4
        cloud_data.append({
            'name': tag['name'],
            'count': tag['count'],
            'size': round(size, 2)
        })

    return cloud_data
