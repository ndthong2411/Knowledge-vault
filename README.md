# 📚 Knowledge Vault

A smart note-taking and knowledge management system with AI-powered search and auto-tagging.

[![CI/CD Pipeline](https://github.com/ndthong2411/Knowledge-vault/actions/workflows/ci.yml/badge.svg)](https://github.com/ndthong2411/Knowledge-vault/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### Core Features
- **📝 Smart Note Management**: Create, edit, and organize notes with markdown support
- **🔍 Hybrid Search**: Combine keyword-based and semantic search for powerful note discovery
  - **Keyword Search**: Fast full-text search using SQLite FTS5
  - **Semantic Search**: Find notes by meaning using sentence embeddings (supports Vietnamese & English)
  - **Hybrid Mode**: Best of both worlds with combined scoring
- **🏷️ Auto-Tagging**: Automatic tag suggestions using YAKE keyword extraction
- **📊 Statistics Dashboard**: Track your knowledge base with detailed analytics
- **🎯 Related Notes**: Discover similar notes automatically
- **👁️ View Tracking**: Monitor which notes are most accessed

### Technical Features
- Markdown file storage with frontmatter metadata
- SQLite database with full-text search indexing
- Sentence-BERT embeddings for multilingual semantic search
- Responsive Streamlit UI
- Docker support for easy deployment
- Comprehensive test suite with CI/CD pipeline

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ndthong2411/Knowledge-vault.git
cd Knowledge-vault
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Docker Installation

**Using Docker Compose** (recommended)
```bash
docker-compose up -d
```

**Using Docker**
```bash
docker build -t knowledge-vault .
docker run -p 8501:8501 -v $(pwd)/data:/app/data knowledge-vault
```

## 📖 Usage Guide

### Creating Notes

1. Click **"➕ New Note"** in the sidebar
2. Enter a title and write your content (Markdown supported)
3. Review auto-suggested tags or add your own
4. Click **"Create Note"** to save

**Pro tip**: Use `#hashtags` in your content for automatic tagging!

### Searching Notes

1. Click **"🔍 Search"** in the sidebar
2. Enter your search query
3. Choose search mode:
   - **Hybrid** (recommended): Combines keyword and semantic search
   - **Keyword**: Fast exact/fuzzy text matching
   - **Semantic**: Find by meaning, not just keywords
4. Optionally filter by tags

**Example searches**:
- "python tutorial" (finds notes about Python)
- "machine learning beginner" (finds ML notes for beginners)
- Vietnamese: "học lập trình" (finds programming learning notes)

### Browsing Tags

1. Click **"🏷️ Browse Tags"** to see all tags
2. Click any tag to view related notes
3. Tag size indicates usage frequency

### Viewing Statistics

1. Click **"📊 Statistics"** for insights:
   - Total notes and tags
   - Most viewed notes
   - Recent activity
   - Storage usage

## 🏗️ Architecture

```
Knowledge-vault/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── data/
│   ├── notes/                  # Markdown note files
│   ├── media/                  # Images and audio (future)
│   └── knowledge.db            # SQLite database
├── src/
│   ├── database.py             # Database operations
│   ├── storage.py              # File storage operations
│   ├── search_engine.py        # Hybrid search engine
│   ├── tagging.py              # Auto-tagging system
│   └── utils.py                # Utility functions
├── tests/                      # Unit tests
│   ├── test_database.py
│   ├── test_storage.py
│   ├── test_tagging.py
│   └── test_utils.py
└── .github/
    └── workflows/              # CI/CD pipelines
        ├── ci.yml
        └── deploy.yml
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Search Configuration
SEMANTIC_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
MAX_SEARCH_RESULTS = 50
SEMANTIC_SEARCH_THRESHOLD = 0.3

# Tagging Configuration
MAX_TAGS = 10
YAKE_LANGUAGE = "en"  # Change to "vi" for Vietnamese

# UI Configuration
NOTES_PER_PAGE = 20
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_database.py -v
```

## 🚀 Deployment

### Local Deployment
```bash
streamlit run app.py --server.port=8501
```

### Docker Deployment
```bash
docker-compose up -d
```

### Cloud Deployment

**Streamlit Cloud**:
1. Push to GitHub
2. Connect repository on [share.streamlit.io](https://share.streamlit.io)
3. Deploy!

**Heroku**:
```bash
heroku create your-app-name
git push heroku main
```

## 📊 Performance

- **Search Speed**: < 100ms for keyword search on 1000+ notes
- **Semantic Search**: ~500ms for 1000 notes (first load ~10s for model)
- **Storage**: ~1KB per note (markdown + metadata)
- **Memory**: ~500MB (includes ML model)

## 🛣️ Roadmap

### Phase 2: Media Support (Planned)
- [ ] Image upload and display in notes
- [ ] Audio recording and playback
- [ ] Speech-to-text for audio notes
- [ ] Image OCR for searchability

### Phase 3: Advanced Features (Future)
- [ ] Note linking and backlinks
- [ ] Graph visualization of note relationships
- [ ] Export to PDF, Notion, Obsidian
- [ ] Collaborative editing
- [ ] Mobile app

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Web framework
- [Sentence Transformers](https://www.sbert.net/) - Semantic search
- [YAKE](https://github.com/LIAAD/yake) - Keyword extraction
- [SQLite FTS5](https://www.sqlite.org/fts5.html) - Full-text search

## 📧 Contact

Project Link: [https://github.com/ndthong2411/Knowledge-vault](https://github.com/ndthong2411/Knowledge-vault)

---

Made with ❤️ by Knowledge Vault Team
