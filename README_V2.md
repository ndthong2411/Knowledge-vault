# 📚 Knowledge Vault v2.0

**The Ultimate Smart Note-Taking and Knowledge Management System**

A comprehensive personal knowledge management system with AI-powered search, bidirectional linking, graph visualization, and advanced organization features.

[![CI/CD Pipeline](https://github.com/ndthong2411/Knowledge-vault/actions/workflows/ci.yml/badge.svg)](https://github.com/ndthong2411/Knowledge-vault/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⭐ What's New in v2.0

### 🆕 Major Features Added

1. **🔗 Backlinks & Bidirectional Linking**
   - Wiki-style `[[Note Title]]` linking
   - Automatic bidirectional link detection
   - Backlink panel showing all references
   - Broken link detection

2. **🌐 Graph Visualization**
   - Interactive network graph of all notes
   - Visual representation of note connections
   - Click to navigate between linked notes
   - Color-coded by tags/folders

3. **📁 Folders & Collections**
   - Hierarchical organization
   - Drag & drop notes into folders
   - Color-coded folders with custom icons
   - Default folders: Personal, Work, Projects, Learning, Archive

4. **⭐ Favorites & Bookmarks**
   - Star important notes for quick access
   - Favorites sidebar
   - One-click access to starred notes

5. **🕐 Version History**
   - Automatic version tracking
   - View all past versions
   - Restore to any previous version
   - Compare versions

6. **📝 Note Templates**
   - Pre-built templates (Meeting Notes, Book Review, etc.)
   - Custom template creation
   - One-click apply template
   - 6 default templates included

7. **📅 Daily Notes**
   - Auto-generated daily notes
   - Calendar view
   - Quick access to today's note
   - Daily journal template

8. **📤 Advanced Export/Import**
   - Export to: Markdown, JSON, PDF, ZIP
   - Import from: Obsidian, Notion, Markdown files
   - Bulk export all notes
   - Preserve metadata and links

9. **🎨 UI Enhancements**
   - Dark mode toggle
   - Enhanced sidebar with folders
   - Quick action buttons
   - Better note cards with previews

---

## ✨ Core Features (from v1.0)

### Note Management
- **📝 Smart Note Creation**: Markdown support with live preview
- **✏️ Rich Editor**: Code blocks, tables, lists, formatting
- **🏷️ Auto-Tagging**: AI-powered tag suggestions using YAKE
- **#️⃣ Hashtag Support**: Auto-detect #hashtags in content

### Search & Discovery
- **🔍 Hybrid Search Engine**:
  - **Keyword Search**: Lightning-fast FTS5 full-text search
  - **Semantic Search**: Find by meaning, not just keywords
  - **Multilingual**: Vietnamese & English support
- **🎯 Related Notes**: AI-suggested similar notes
- **👁️ View Tracking**: See most-viewed notes

### Organization
- **🗂️ Smart Tagging**: Auto-suggest + manual tags
- **🏷️ Tag Cloud**: Visual tag browser
- **📊 Statistics**: Detailed analytics dashboard
- **🔎 Advanced Filters**: Filter by tags, date, folder

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ndthong2411/Knowledge-vault.git
cd Knowledge-vault

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (for v2.0 features)
python scripts/migrate_db.py

# Start application
streamlit run app.py
```

**Docker:**
```bash
docker-compose up -d
```

---

## 📖 User Guide

### Using Backlinks

Create links between notes using `[[Note Title]]` syntax:

```markdown
# Machine Learning Basics

This builds upon [[Python Fundamentals]] and [[Linear Algebra]].

See also: [[Deep Learning]] for advanced topics.
```

**Features:**
- Auto-complete note titles while typing `[[`
- Click links to navigate between notes
- View all backlinks in note sidebar
- Find broken links (links to non-existent notes)

### Using Folders

1. **Create Folder**: Settings → Manage Folders → New Folder
2. **Move Notes**: Drag note card to folder or use "Move to Folder" button
3. **Browse**: Click folder in sidebar to view notes
4. **Customize**: Set custom icon and color for each folder

**Default Folders:**
- 👤 Personal - Private notes
- 💼 Work - Work-related content
- 🎯 Projects - Project documentation
- 🎓 Learning - Study materials
- 📦 Archive - Archived content

### Using Templates

1. **Apply Template**: New Note → Choose Template → Edit & Save
2. **Custom Template**: Templates page → Create Template
3. **Quick Fill**: Template auto-fills title, content, tags

**Built-in Templates:**
- 📄 Blank Note
- 📋 Meeting Notes - Agenda, attendees, action items
- 📚 Book Review - Structured book notes
- 🎯 Project Plan - Project planning template
- 🎓 Learning Notes - Study session notes
- 📓 Daily Journal - Daily reflection

### Daily Notes

- **Quick Access**: Click "Today" button or use `Ctrl+D`
- **Auto-Create**: Daily note auto-created for today
- **Calendar**: Browse past daily notes
- **Template**: Uses Daily Journal template

### Favorites

- **Star Note**: Click ⭐ on any note card
- **Quick Access**: Favorites show in sidebar
- **Unstar**: Click again to remove from favorites

### Version History

1. Open any note
2. Click "History" button
3. View all versions with timestamps
4. Click "Restore" to revert to previous version

### Export & Import

**Export:**
- Single Note → Markdown, JSON
- All Notes → ZIP file
- Folder → ZIP file
- Obsidian Format → Compatible export

**Import:**
- Markdown files → New notes
- Obsidian Vault → Bulk import with links
- Notion Export → Import from ZIP
- JSON → With full metadata

---

## 🎨 Advanced Features

### Graph Visualization

- **Network View**: See all note connections
- **Interactive**: Click nodes to navigate
- **Filters**: Show/hide by tags, folders
- **Insights**: Find note clusters, orphans

### Link Analysis

- **Orphan Notes**: Notes with no links
- **Most Linked**: Hub notes with many backlinks
- **Broken Links**: Links to missing notes
- **Link Suggestions**: AI-suggested links

### Search Features

- **Search Modes**: Keyword, Semantic, Hybrid
- **Tag Filters**: Search within tags
- **Folder Filters**: Search within folders
- **Date Range**: Filter by creation/update date
- **Sort Options**: Relevance, date, views

---

## 🏗️ Architecture

```
Knowledge-vault/
├── app.py                    # Main Streamlit app
├── app_v2.py                 # Enhanced v2.0 app (WIP)
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
│
├── src/
│   ├── database.py           # Database + new methods
│   ├── storage.py            # File operations
│   ├── search_engine.py      # Hybrid search
│   ├── tagging.py            # Auto-tagging
│   ├── backlinks.py          # ⭐ NEW: Backlinks parser
│   ├── export_import.py      # ⭐ NEW: Export/Import
│   └── utils.py              # Utilities
│
├── scripts/
│   ├── migrate_db.py         # ⭐ NEW: Database migration
│   ├── test_enhanced_features.py  # Feature tests
│   └── setup.sh              # Installation script
│
├── tests/                    # Unit tests
└── data/
    ├── notes/                # Markdown files
    ├── media/                # Images, audio
    └── knowledge.db          # SQLite database
```

### Database Schema (v2.0)

**New Tables:**
- `folders` - Hierarchical folders
- `note_links` - Bidirectional links
- `note_versions` - Version history
- `templates` - Note templates

**Enhanced Tables:**
- `notes` + `is_favorite`, `is_daily_note`, `folder_id`

---

## 🔧 Configuration

Edit `config.py`:

```python
# Search
SEMANTIC_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
MAX_SEARCH_RESULTS = 50

# Tagging
MAX_TAGS = 10
YAKE_LANGUAGE = "en"  # or "vi" for Vietnamese

# UI
NOTES_PER_PAGE = 20
DEFAULT_THEME = "light"
```

---

## 🎯 Use Cases

### Personal Knowledge Management
- Store book summaries with [[links]] to related concepts
- Track learning progress with daily notes
- Build a second brain with interconnected ideas

### Research
- Link research papers with `[[Paper Title]]`
- Organize by projects in folders
- Tag by methodology, field, year
- Export bibliography

### Work & Projects
- Meeting notes with action items
- Project documentation with backlinks
- Knowledge sharing with team (export/import)
- Version history for important docs

### Learning & Education
- Course notes with concept linking
- Flashcards and study materials
- Daily learning logs
- Resource library with tags

---

## 📊 Statistics & Analytics

- **Total notes, tags, folders**
- **Most viewed notes**
- **Most linked notes** (hubs)
- **Orphan notes** (isolated)
- **Tag distribution**
- **Note growth over time**
- **Storage usage**

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Test enhanced features
python scripts/test_enhanced_features.py

# With coverage
pytest --cov=src --cov-report=html
```

---

## 🚀 Deployment

### Local
```bash
streamlit run app.py --server.port=8501
```

### Docker
```bash
docker-compose up -d
```

### Streamlit Cloud
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Deploy

---

## 🛣️ Roadmap

### v2.1 (Current Development)
- [x] Backlinks system
- [x] Folders
- [x] Templates
- [x] Version history
- [x] Export/Import
- [ ] Graph visualization UI
- [ ] Keyboard shortcuts
- [ ] Drag & drop files
- [ ] Performance optimization

### v2.2 (Planned)
- [ ] Mobile responsive design
- [ ] Real-time collaboration
- [ ] Note encryption
- [ ] Cloud sync
- [ ] Browser extension
- [ ] API endpoints

### v3.0 (Future)
- [ ] Image upload & OCR
- [ ] Audio notes with transcription
- [ ] Video embeds
- [ ] Drawing/whiteboard
- [ ] AI chat with notes
- [ ] Mobile apps

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📝 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **Obsidian** - Inspiration for backlinks
- **Roam Research** - Bidirectional linking concept
- **Notion** - Templates and organization
- **Streamlit** - Web framework
- **Sentence Transformers** - Semantic search
- **YAKE** - Keyword extraction

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/ndthong2411/Knowledge-vault/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ndthong2411/Knowledge-vault/discussions)
- **Docs**: [Full Documentation](https://docs.example.com)

---

Made with ❤️ for knowledge workers, researchers, and lifelong learners.

**Version**: 2.0.0
**Last Updated**: 2024-11-17
