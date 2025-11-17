"""
Knowledge Vault - Smart Note-Taking and Knowledge Management System
Main Streamlit Application
"""
import streamlit as st
from datetime import datetime

from src.database import Database
from src.storage import Storage
from src.search_engine import SearchEngine
from src.tagging import AutoTagger
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


# Page configuration
st.set_page_config(
    page_title="Knowledge Vault",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .note-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: #ffffff;
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
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()

if 'storage' not in st.session_state:
    st.session_state.storage = Storage()

if 'search_engine' not in st.session_state:
    st.session_state.search_engine = SearchEngine(st.session_state.db)

if 'auto_tagger' not in st.session_state:
    st.session_state.auto_tagger = AutoTagger()

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

if 'selected_note_id' not in st.session_state:
    st.session_state.selected_note_id = None


def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.title("📚 Knowledge Vault")
        st.markdown("---")

        # Navigation
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.session_state.selected_note_id = None
            st.rerun()

        if st.button("➕ New Note", use_container_width=True):
            st.session_state.current_page = "new_note"
            st.rerun()

        if st.button("🔍 Search", use_container_width=True):
            st.session_state.current_page = "search"
            st.rerun()

        if st.button("🏷️ Browse Tags", use_container_width=True):
            st.session_state.current_page = "tags"
            st.rerun()

        if st.button("📊 Statistics", use_container_width=True):
            st.session_state.current_page = "statistics"
            st.rerun()

        st.markdown("---")

        # Quick stats
        stats = st.session_state.db.get_statistics()
        st.metric("Total Notes", stats['total_notes'])
        st.metric("Total Tags", stats['total_tags'])


def render_home():
    """Render home page with recent notes"""
    st.title("📚 Welcome to Knowledge Vault")
    st.markdown("Your smart note-taking and knowledge management system")

    st.markdown("---")

    # Get recent notes
    notes = st.session_state.db.get_all_notes(limit=NOTES_PER_PAGE, order_by="updated_at")

    if not notes:
        st.info("No notes yet. Click 'New Note' to create your first note!")
        return

    st.subheader(f"Recent Notes ({len(notes)})")

    for note in notes:
        render_note_card(note)


def render_note_card(note: dict, show_scores: bool = False):
    """Render a note card"""
    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
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

        with col2:
            st.caption(f"Updated: {preview['updated_at']}")
            st.caption(f"👁 {note.get('view_count', 0)} views")
            st.caption(f"⏱ {preview['read_time']}")

            if show_scores:
                score_text = format_search_score(note)
                if score_text:
                    st.markdown(f'<div class="search-score">{score_text}</div>', unsafe_allow_html=True)

        st.markdown("---")


def render_new_note():
    """Render new note creation page"""
    st.title("➕ Create New Note")

    with st.form("new_note_form"):
        title = st.text_input("Title*", placeholder="Enter note title...")

        content = st.text_area(
            "Content*",
            placeholder="Write your note here... (Markdown supported)",
            height=300
        )

        col1, col2 = st.columns(2)

        with col1:
            # Auto-suggest tags
            if title or content:
                suggested_tags = st.session_state.auto_tagger.suggest_tags(title, content)
                st.info(f"Suggested tags: {', '.join(suggested_tags) if suggested_tags else 'None'}")

        with col2:
            tags_input = st.text_input(
                "Tags (comma-separated)",
                placeholder="tag1, tag2, tag3...",
                value=", ".join(suggested_tags) if (title or content) else ""
            )

        submitted = st.form_submit_button("Create Note", use_container_width=True)

        if submitted:
            # Validate inputs
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

                # Extract hashtags from content
                hashtags = st.session_state.auto_tagger.extract_hashtags(content)

                # Merge all tags
                final_tags = st.session_state.auto_tagger.merge_tags([], tags, hashtags)

                # Create file
                file_path = st.session_state.storage.create_note_file(title, content, final_tags)

                # Create database entry
                note_id = st.session_state.db.create_note(title, content, file_path, final_tags)

                # Create embedding for semantic search
                st.session_state.search_engine.encode_note(note_id, title, content)

                st.success(f"✅ Note '{title}' created successfully!")

                # Redirect to view note
                st.session_state.selected_note_id = note_id
                st.session_state.current_page = "view_note"
                st.rerun()

            except Exception as e:
                st.error(f"Error creating note: {str(e)}")


def render_view_note():
    """Render note viewing/editing page"""
    note_id = st.session_state.selected_note_id

    if not note_id:
        st.error("No note selected")
        return

    note = st.session_state.db.get_note(note_id)

    if not note:
        st.error("Note not found")
        return

    # Header with actions
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.title(note['title'])

    with col2:
        if st.button("✏️ Edit", use_container_width=True):
            st.session_state.current_page = "edit_note"
            st.rerun()

    with col3:
        if st.button("🗑️ Delete", use_container_width=True, type="secondary"):
            if st.session_state.db.delete_note(note_id):
                st.session_state.storage.delete_note_file(note['file_path'])
                st.success("Note deleted!")
                st.session_state.current_page = "home"
                st.session_state.selected_note_id = None
                st.rerun()

    # Metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.caption(f"Created: {format_relative_time(note['created_at'])}")
    with col2:
        st.caption(f"Updated: {format_relative_time(note['updated_at'])}")
    with col3:
        st.caption(f"Views: {note['view_count']}")
    with col4:
        st.caption(f"Read time: {calculate_read_time(note['content'])}")

    # Tags
    if note.get('tags'):
        tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in note['tags']])
        st.markdown(tags_html, unsafe_allow_html=True)

    st.markdown("---")

    # Content
    st.markdown(note['content'])

    st.markdown("---")

    # Similar notes
    st.subheader("📎 Similar Notes")
    similar_notes = st.session_state.search_engine.find_similar_notes(note_id, limit=5)

    if similar_notes:
        for similar_note in similar_notes:
            render_note_card(similar_note, show_scores=True)
    else:
        st.info("No similar notes found")


def render_edit_note():
    """Render note editing page"""
    note_id = st.session_state.selected_note_id

    if not note_id:
        st.error("No note selected")
        return

    note = st.session_state.db.get_note(note_id)

    if not note:
        st.error("Note not found")
        return

    st.title(f"✏️ Edit: {note['title']}")

    with st.form("edit_note_form"):
        title = st.text_input("Title*", value=note['title'])

        content = st.text_area("Content*", value=note['content'], height=300)

        tags_input = st.text_input(
            "Tags (comma-separated)",
            value=", ".join(note.get('tags', []))
        )

        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)

        if cancelled:
            st.session_state.current_page = "view_note"
            st.rerun()

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

                # Update database
                st.session_state.db.update_note(note_id, title, content, tags)

                # Update file
                st.session_state.storage.update_note_file(note['file_path'], title, content, tags)

                # Update embedding
                st.session_state.search_engine.encode_note(note_id, title, content)

                st.success("✅ Note updated successfully!")

                st.session_state.current_page = "view_note"
                st.rerun()

            except Exception as e:
                st.error(f"Error updating note: {str(e)}")


def render_search():
    """Render search page"""
    st.title("🔍 Search Notes")

    # Search form
    col1, col2 = st.columns([3, 1])

    with col1:
        query = st.text_input("Search query", placeholder="Enter keywords or describe what you're looking for...")

    with col2:
        search_mode = st.selectbox(
            "Search mode",
            ["hybrid", "keyword", "semantic"],
            format_func=lambda x: {
                "hybrid": "🔀 Hybrid (Best)",
                "keyword": "🔑 Keyword",
                "semantic": "🧠 Semantic"
            }[x]
        )

    # Advanced filters
    with st.expander("Advanced Filters"):
        tags_filter = st.text_input("Filter by tags (comma-separated)", placeholder="tag1, tag2...")

    if query:
        # Parse tag filter
        tags = parse_tags_input(tags_filter) if tags_filter else None

        # Perform search
        with st.spinner("Searching..."):
            results = st.session_state.search_engine.search(
                query,
                search_mode=search_mode,
                tags=tags
            )

        # Display results
        if results:
            st.success(f"Found {len(results)} results")

            for note in results:
                render_note_card(note, show_scores=True)
        else:
            st.info("No results found. Try different keywords or search mode.")
    else:
        st.info("Enter a search query to find notes")


def render_tags():
    """Render tags browsing page"""
    st.title("🏷️ Browse Tags")

    all_tags = st.session_state.db.get_all_tags()

    if not all_tags:
        st.info("No tags yet. Create notes with tags to see them here.")
        return

    # Tag cloud visualization
    st.subheader("Tag Cloud")
    tag_cloud_data = get_tag_cloud_data(all_tags)

    # Display tags as buttons with sizes
    cols = st.columns(5)
    for idx, tag_data in enumerate(tag_cloud_data[:20]):  # Show top 20 tags
        col_idx = idx % 5
        with cols[col_idx]:
            if st.button(
                f"{tag_data['name']} ({tag_data['count']})",
                key=f"tag_{tag_data['name']}",
                use_container_width=True
            ):
                # Search notes by this tag
                notes = st.session_state.db.search_by_tags([tag_data['name']])
                st.session_state.tag_filter_notes = notes
                st.rerun()

    st.markdown("---")

    # Display filtered notes if tag was clicked
    if hasattr(st.session_state, 'tag_filter_notes'):
        st.subheader("Notes with selected tag")
        for note in st.session_state.tag_filter_notes:
            render_note_card(note)


def render_statistics():
    """Render statistics page"""
    st.title("📊 Statistics")

    stats = st.session_state.db.get_statistics()
    storage_stats = st.session_state.storage.get_storage_stats()

    # Overview stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'<div class="stat-box"><h2>{stats["total_notes"]}</h2><p>Total Notes</p></div>',
                   unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="stat-box"><h2>{stats["total_tags"]}</h2><p>Total Tags</p></div>',
                   unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="stat-box"><h2>{stats["notes_with_embeddings"]}</h2><p>Indexed Notes</p></div>',
                   unsafe_allow_html=True)

    with col4:
        st.markdown(f'<div class="stat-box"><h2>{storage_stats["total_size_mb"]} MB</h2><p>Storage Used</p></div>',
                   unsafe_allow_html=True)

    st.markdown("---")

    # Most viewed notes
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👁️ Most Viewed Notes")
        if stats['most_viewed']:
            for note in stats['most_viewed']:
                st.write(f"**{note['title']}** - {note['view_count']} views")
        else:
            st.info("No data yet")

    with col2:
        st.subheader("🆕 Recent Notes")
        if stats['recent_notes']:
            for note in stats['recent_notes']:
                st.write(f"**{note['title']}** - {format_relative_time(note['created_at'])}")
        else:
            st.info("No data yet")

    st.markdown("---")

    # Reindex button
    st.subheader("🔄 Maintenance")
    if st.button("Reindex All Notes for Semantic Search"):
        with st.spinner("Reindexing... This may take a while."):
            st.session_state.search_engine.reindex_all_notes()
        st.success("Reindexing complete!")


def main():
    """Main application entry point"""
    render_sidebar()

    # Route to appropriate page
    page = st.session_state.current_page

    if page == "home":
        render_home()
    elif page == "new_note":
        render_new_note()
    elif page == "view_note":
        render_view_note()
    elif page == "edit_note":
        render_edit_note()
    elif page == "search":
        render_search()
    elif page == "tags":
        render_tags()
    elif page == "statistics":
        render_statistics()
    else:
        render_home()


if __name__ == "__main__":
    main()
