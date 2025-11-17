"""
Configuration file for Knowledge Vault application
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
NOTES_DIR = DATA_DIR / "notes"
MEDIA_DIR = DATA_DIR / "media"
IMAGES_DIR = MEDIA_DIR / "images"
AUDIO_DIR = MEDIA_DIR / "audio"

# Database
DB_PATH = DATA_DIR / "knowledge.db"

# Search Configuration
SEMANTIC_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # Supports Vietnamese
EMBEDDING_DIM = 384  # Dimension for the above model
MAX_SEARCH_RESULTS = 50
SEMANTIC_SEARCH_THRESHOLD = 0.3  # Minimum similarity score

# Tagging Configuration
MAX_TAGS = 10
MIN_TAG_LENGTH = 2
YAKE_LANGUAGE = "en"  # Can be changed to "vi" for Vietnamese
YAKE_MAX_NGRAM = 2
YAKE_DEDUPLICATION_THRESHOLD = 0.9

# UI Configuration
NOTES_PER_PAGE = 20
DEFAULT_THEME = "light"

# Create directories if they don't exist
for directory in [DATA_DIR, NOTES_DIR, MEDIA_DIR, IMAGES_DIR, AUDIO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
