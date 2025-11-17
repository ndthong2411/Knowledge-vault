"""
Knowledge Vault v2.0 - Enhanced Smart Note-Taking System
With Backlinks, Graph View, Folders, Templates, and More!
"""
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import networkx as nx
from streamlit_option_menu import option_menu
import json
from pathlib import Path

from src.database import Database
from src.storage import Storage
from src.search_engine import SearchEngine
from src.tagging import AutoTagger
from src.backlinks import BacklinksParser
from src.export_import import ExportImport
from src.utils import (
    format_relative_time,
    truncate_text,
    generate_note_preview,
    validate_note_title,
    validate_note_content,
    parse_tags_input,
    format_search_score,
    get_tag_cloud_data,
    markdown_to_html,
    calculate_read_time
)
from config import NOTES_PER_PAGE


# ==================== PAGE CONFIGURATION ====================

st.set_page_config(
    page_title="Knowledge Vault v2.0",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE ====================

if 'db' not in st.session_state:
    st.session_state.db = Database()

if 'storage' not in st.session_state:
    st.session_state.storage = Storage()

if 'search_engine' not in st.session_state:
    st.session_state.search_engine = SearchEngine(st.session_state.db)

if 'auto_tagger' not in st.session_state:
    st.session_state.auto_tagger = AutoTagger()

if 'backlinks_parser' not in st.session_state:
    st.session_state.backlinks_parser = BacklinksParser(st.session_state.db)

if 'export_import' not in st.session_state:
    st.session_state.export_import = ExportImport(st.session_state.db, st.session_state.storage)

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

if 'selected_note_id' not in st.session_state:
    st.session_state.selected_note_id = None

if 'current_folder' not in st.session_state:
    st.session_state.current_folder = None

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False


# ==================== CUSTOM CSS ====================

def load_css():
    """Load custom CSS based on theme"""
    if st.session_state.dark_mode:
        st.markdown("""
<style>
    .main {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    .note-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #333;
        margin-bottom: 1rem;
        background-color: #2a2a2a;
    }
    .wiki-link {
        color: #64B5F6;
        text-decoration: none;
        border-bottom: 1px dashed #64B5F6;
    }
    .wiki-link:hover {
        color: #42A5F5;
    }
    .wiki-link-broken {
        color: #EF5350;
        text-decoration: line-through;
    }
    .tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        border-radius: 0.3rem;
        background-color: #388E3C;
        color: white;
        font-size: 0.8rem;
    }
    .folder-item {
        padding: 0.5rem;
        border-radius: 0.3rem;
        cursor: pointer;
        margin: 0.2rem 0;
    }
    .folder-item:hover {
        background-color: #333;
    }
</style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
<style>
    .note-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: #ffffff;
    }
    .wiki-link {
        color: #1976D2;
        text-decoration: none;
        border-bottom: 1px dashed #1976D2;
        cursor: pointer;
    }
    .wiki-link:hover {
        color: #1565C0;
    }
    .wiki-link-broken {
        color: #D32F2F;
        text-decoration: line-through;
    }
    .tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        border-radius: 0.3rem;
        background-color: #4CAF50;
        color: white;
        font-size: 0.8rem;
    }
    .search-score {
        color: #666;
        font-size: 0.9rem;
        font-style: italic;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        text-align: center;
    }
    .folder-item {
        padding: 0.5rem;
        border-radius: 0.3rem;
        cursor: pointer;
        margin: 0.2rem 0;
    }
    .folder-item:hover {
        background-color: #f0f2f6;
    }
    .backlink-box {
        padding: 0.5rem;
        border-left: 3px solid #4CAF50;
        background-color: #f5f5f5;
        margin: 0.5rem 0;
    }
</style>
        """, unsafe_allow_html=True)

load_css()


# ==================== SIDEBAR ====================

def render_sidebar():
    """Enhanced sidebar with folders and navigation"""
    with st.sidebar:
        # Header with dark mode toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("📚 Knowledge Vault")
        with col2:
            if st.button("🌓", help="Toggle Dark Mode"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                load_css()
                st.rerun()

        st.markdown("---")

        # Main Navigation
        selected = option_menu(
            menu_title=None,
            options=["Home", "Search", "Graph", "Templates", "Daily", "Statistics"],
            icons=["house", "search", "diagram-3", "file-earmark", "calendar", "bar-chart"],
            default_index=0,
        )

        # Map selection to page
        page_map = {
            "Home": "home",
            "Search": "search",
            "Graph": "graph",
            "Templates": "templates",
            "Daily": "daily_notes",
            "Statistics": "statistics"
        }

        if st.session_state.current_page != page_map.get(selected):
            st.session_state.current_page = page_map[selected]
            st.rerun()

        st.markdown("---")

        # Quick Actions
        st.subheader("Quick Actions")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New Note", use_container_width=True):
                st.session_state.current_page = "new_note"
                st.rerun()

        with col2:
            if st.button("📝 Today", use_container_width=True):
                st.session_state.current_page = "daily_notes"
                st.rerun()

        st.markdown("---")

        # Favorites
        st.subheader("⭐ Favorites")
        favorites = st.session_state.db.get_favorite_notes()

        if favorites:
            for fav in favorites[:5]:
                if st.button(f"📄 {truncate_text(fav['title'], 25)}", key=f"fav_{fav['id']}", use_container_width=True):
                    st.session_state.selected_note_id = fav['id']
                    st.session_state.current_page = "view_note"
                    st.rerun()

            if len(favorites) > 5:
                st.caption(f"... and {len(favorites) - 5} more")
        else:
            st.caption("No favorites yet")

        st.markdown("---")

        # Folders
        st.subheader("📁 Folders")

        folders = st.session_state.db.get_all_folders()

        # All Notes folder
        all_notes_count = st.session_state.db.get_notes_count()
        if st.button(f"📂 All Notes ({all_notes_count})", key="folder_all", use_container_width=True):
            st.session_state.current_folder = None
            st.session_state.current_page = "folder_view"
            st.rerun()

        # Individual folders
        for folder in folders:
            icon = folder.get('icon', '📁')
            if st.button(f"{icon} {folder['name']} ({folder['note_count']})",
                        key=f"folder_{folder['id']}",
                        use_container_width=True):
                st.session_state.current_folder = folder['id']
                st.session_state.current_page = "folder_view"
                st.rerun()

        # Manage Folders button
        if st.button("⚙️ Manage Folders", use_container_width=True):
            st.session_state.current_page = "manage_folders"
            st.rerun()

        st.markdown("---")

        # Quick Stats
        stats = st.session_state.db.get_statistics()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Notes", stats['total_notes'])
        with col2:
            st.metric("Tags", stats['total_tags'])


# ==================== HELPER FUNCTIONS ====================

def render_note_card(note: dict, show_scores: bool = False, show_folder: bool = False):
    """Render enhanced note card with backlinks preview"""
    with st.container():
        col1, col2, col3 = st.columns([0.5, 3, 1])

        with col1:
            # Favorite star
            is_favorite = note.get('is_favorite', 0) == 1
            star = "⭐" if is_favorite else "☆"
            if st.button(star, key=f"star_{note['id']}", help="Toggle favorite"):
                st.session_state.db.toggle_favorite(note['id'])
                st.rerun()

        with col2:
            # Title and metadata
            if st.button(f"📝 {note['title']}", key=f"note_{note['id']}", use_container_width=True):
                st.session_state.selected_note_id = note['id']
                st.session_state.current_page = "view_note"
                st.rerun()

            # Tags
            if note.get('tags'):
                tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in note['tags']])
                st.markdown(tags_html, unsafe_allow_html=True)

            # Summary
            preview = generate_note_preview(note)
            st.caption(preview['summary'])

            # Folder (if enabled)
            if show_folder and note.get('folder_id'):
                folders = {f['id']: f for f in st.session_state.db.get_all_folders()}
                if note['folder_id'] in folders:
                    folder = folders[note['folder_id']]
                    st.caption(f"{folder.get('icon', '📁')} {folder['name']}")

        with col3:
            st.caption(f"Updated: {preview['updated_at']}")
            st.caption(f"👁 {note.get('view_count', 0)} • ⏱ {preview['read_time']}")

            # Backlink count
            links = st.session_state.db.get_note_links(note['id'])
            backlink_count = len(links['incoming'])
            if backlink_count > 0:
                st.caption(f"🔗 {backlink_count} backlinks")

            if show_scores:
                score_text = format_search_score(note)
                if score_text:
                    st.markdown(f'<div class="search-score">{score_text}</div>', unsafe_allow_html=True)

        st.markdown("---")


# ==================== PAGE RENDERERS ====================

def render_home():
    """Enhanced home page"""
    st.title("📚 Welcome to Knowledge Vault v2.0")

    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    stats = st.session_state.db.get_statistics()

    with col1:
        st.metric("📝 Total Notes", stats['total_notes'])
    with col2:
        st.metric("🏷️ Tags", stats['total_tags'])
    with col3:
        favorites_count = len(st.session_state.db.get_favorite_notes())
        st.metric("⭐ Favorites", favorites_count)
    with col4:
        folders_count = len(st.session_state.db.get_all_folders())
        st.metric("📁 Folders", folders_count)

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📅 Recent", "⭐ Favorites", "🔗 Most Linked"])

    with tab1:
        notes = st.session_state.db.get_all_notes(limit=10, order_by="updated_at")
        if notes:
            for note in notes:
                render_note_card(note, show_folder=True)
        else:
            st.info("No notes yet. Click 'New Note' to create your first note!")

    with tab2:
        favorites = st.session_state.db.get_favorite_notes()
        if favorites:
            for note in favorites:
                render_note_card(note, show_folder=True)
        else:
            st.info("No favorites yet. Click the star ⭐ to add favorites!")

    with tab3:
        most_linked = st.session_state.backlinks_parser.get_most_linked_notes(limit=10)
        if most_linked:
            for note in most_linked:
                render_note_card(note, show_folder=True)
        else:
            st.info("No linked notes yet. Use [[Note Title]] to create links!")


def render_new_note():
    """Enhanced note creation with templates"""
    st.title("➕ Create New Note")

    # Template selection
    templates = st.session_state.db.get_all_templates()
    template_options = {f"{t.get('icon', '📄')} {t['name']}": t for t in templates}

    selected_template = st.selectbox(
        "Choose a template (optional)",
        ["None"] + list(template_options.keys())
    )

    # Load template content
    initial_content = ""
    initial_tags = []

    if selected_template != "None":
        template = template_options[selected_template]
        initial_content = template['content'].replace('{date}', datetime.now().strftime("%Y-%m-%d"))
        if template.get('tags'):
            initial_tags = [t.strip() for t in template['tags'].split(',')]

    with st.form("new_note_form"):
        title = st.text_input("Title*", placeholder="Enter note title...")

        content = st.text_area(
            "Content* (Supports Markdown and [[Wiki Links]])",
            value=initial_content,
            placeholder="Write your note here...\n\nUse [[Note Title]] to link to other notes",
            height=400
        )

        col1, col2 = st.columns(2)

        with col1:
            # Auto-suggest tags
            if title or content:
                suggested_tags = st.session_state.auto_tagger.suggest_tags(title, content)
                all_suggested = list(set(suggested_tags + initial_tags))
                st.info(f"💡 Suggested: {', '.join(all_suggested) if all_suggested else 'None'}")

        with col2:
            tags_input = st.text_input(
                "Tags (comma-separated)",
                value=", ".join(initial_tags) if initial_tags else (", ".join(suggested_tags) if (title or content) and suggested_tags else "")
            )

        # Folder selection
        folders = st.session_state.db.get_all_folders()
        folder_options = {f"{f.get('icon', '📁')} {f['name']}": f['id'] for f in folders}
        selected_folder_name = st.selectbox("Folder (optional)", ["None"] + list(folder_options.keys()))
        selected_folder_id = folder_options.get(selected_folder_name)

        col1, col2 = st.columns([1, 5])
        with col1:
            submitted = st.form_submit_button("💾 Create", use_container_width=True)
        with col2:
            st.caption("💡 Tip: Use [[Note Title]] to link to other notes. Use Ctrl+S to save quickly.")

        if submitted:
            # Validate
            title_valid, title_error = validate_note_title(title)
            content_valid, content_error = validate_note_content(content)

            if not title_valid:
                st.error(title_error)
                return

            if not content_valid:
                st.error(content_error)
                return

            try:
                # Parse tags
                tags = parse_tags_input(tags_input)
                tags = st.session_state.auto_tagger.validate_tags(tags)

                # Extract hashtags
                hashtags = st.session_state.auto_tagger.extract_hashtags(content)

                # Merge tags
                final_tags = st.session_state.auto_tagger.merge_tags([], tags, hashtags)

                # Create file
                file_path = st.session_state.storage.create_note_file(title, content, final_tags)

                # Create database entry
                note_id = st.session_state.db.create_note(title, content, file_path, final_tags)

                # Set folder
                if selected_folder_id:
                    st.session_state.db.move_note_to_folder(note_id, selected_folder_id)

                # Create embedding
                st.session_state.search_engine.encode_note(note_id, title, content)

                # Process backlinks
                st.session_state.backlinks_parser.process_note_links(note_id, content)

                # Save version
                st.session_state.db.save_version(note_id, title, content)

                st.success(f"✅ Note '{title}' created successfully!")

                # Redirect
                st.session_state.selected_note_id = note_id
                st.session_state.current_page = "view_note"
                st.rerun()

            except Exception as e:
                st.error(f"Error creating note: {str(e)}")


# I'll continue with more page renderers...
# Due to character limits, I'll create this as a complete file
