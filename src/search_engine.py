"""
Hybrid search engine for Knowledge Vault
Combines keyword-based (FTS5) and semantic search (sentence embeddings)
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    SEMANTIC_MODEL,
    MAX_SEARCH_RESULTS,
    SEMANTIC_SEARCH_THRESHOLD
)
from src.database import Database


class SearchEngine:
    """Hybrid search engine combining keyword and semantic search"""

    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.model = None
        self._model_loaded = False

    def _load_model(self):
        """Lazy load the sentence transformer model"""
        if not self._model_loaded:
            print("Loading semantic search model...")
            self.model = SentenceTransformer(SEMANTIC_MODEL)
            self._model_loaded = True

    def encode_text(self, text: str) -> np.ndarray:
        """Encode text into embedding vector"""
        self._load_model()
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def encode_note(self, note_id: int, title: str, content: str):
        """
        Encode a note and save its embedding to database
        Combines title and content for better representation
        """
        # Give more weight to title by repeating it
        text = f"{title} {title} {content[:1000]}"  # Limit content length for efficiency

        embedding = self.encode_text(text)
        self.db.save_embedding(note_id, embedding)

    def keyword_search(self, query: str, limit: int = MAX_SEARCH_RESULTS) -> List[Dict]:
        """
        Perform keyword-based full-text search using FTS5
        Returns list of notes with relevance scores
        """
        try:
            results = self.db.full_text_search(query, limit)
            return results
        except Exception as e:
            print(f"Keyword search error: {e}")
            return []

    def semantic_search(self, query: str, limit: int = MAX_SEARCH_RESULTS,
                       threshold: float = SEMANTIC_SEARCH_THRESHOLD) -> List[Dict]:
        """
        Perform semantic search using sentence embeddings
        Returns list of notes with similarity scores
        """
        try:
            # Encode query
            query_embedding = self.encode_text(query)

            # Get all note embeddings
            note_embeddings = self.db.get_all_embeddings()

            if not note_embeddings:
                return []

            # Calculate similarity scores
            similarities = []
            for note_id, note_embedding in note_embeddings:
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    note_embedding.reshape(1, -1)
                )[0][0]

                if similarity >= threshold:
                    similarities.append((note_id, float(similarity)))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Get top results
            results = []
            for note_id, similarity in similarities[:limit]:
                note = self.db.get_note(note_id)
                if note:
                    note['similarity_score'] = similarity
                    results.append(note)

            return results

        except Exception as e:
            print(f"Semantic search error: {e}")
            return []

    def hybrid_search(self, query: str, limit: int = MAX_SEARCH_RESULTS,
                     keyword_weight: float = 0.5,
                     semantic_weight: float = 0.5) -> List[Dict]:
        """
        Perform hybrid search combining keyword and semantic search

        Args:
            query: Search query string
            limit: Maximum number of results
            keyword_weight: Weight for keyword search (0-1)
            semantic_weight: Weight for semantic search (0-1)

        Returns:
            List of notes sorted by combined score
        """
        # Normalize weights
        total_weight = keyword_weight + semantic_weight
        keyword_weight = keyword_weight / total_weight
        semantic_weight = semantic_weight / total_weight

        # Perform both searches
        keyword_results = self.keyword_search(query, limit * 2)
        semantic_results = self.semantic_search(query, limit * 2)

        # Combine results
        note_scores = {}

        # Add keyword search scores (normalized)
        if keyword_results:
            max_rank = len(keyword_results)
            for idx, note in enumerate(keyword_results):
                note_id = note['id']
                # Inverse rank scoring
                score = (max_rank - idx) / max_rank
                note_scores[note_id] = {
                    'note': note,
                    'keyword_score': score,
                    'semantic_score': 0.0
                }

        # Add semantic search scores
        for note in semantic_results:
            note_id = note['id']
            similarity = note.get('similarity_score', 0.0)

            if note_id in note_scores:
                note_scores[note_id]['semantic_score'] = similarity
            else:
                note_scores[note_id] = {
                    'note': note,
                    'keyword_score': 0.0,
                    'semantic_score': similarity
                }

        # Calculate combined scores
        combined_results = []
        for note_id, scores in note_scores.items():
            combined_score = (
                scores['keyword_score'] * keyword_weight +
                scores['semantic_score'] * semantic_weight
            )

            note = scores['note']
            note['combined_score'] = combined_score
            note['keyword_score'] = scores['keyword_score']
            note['semantic_score'] = scores['semantic_score']

            combined_results.append(note)

        # Sort by combined score
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)

        return combined_results[:limit]

    def search(self, query: str, search_mode: str = "hybrid",
              tags: List[str] = None, limit: int = MAX_SEARCH_RESULTS) -> List[Dict]:
        """
        Main search interface

        Args:
            query: Search query string
            search_mode: "keyword", "semantic", or "hybrid"
            tags: Optional list of tags to filter by
            limit: Maximum number of results

        Returns:
            List of matching notes
        """
        # Perform search based on mode
        if search_mode == "keyword":
            results = self.keyword_search(query, limit)
        elif search_mode == "semantic":
            results = self.semantic_search(query, limit)
        else:  # hybrid
            results = self.hybrid_search(query, limit)

        # Filter by tags if provided
        if tags:
            tag_set = set(tag.lower().strip() for tag in tags)
            results = [
                note for note in results
                if any(tag.lower() in tag_set for tag in note.get('tags', []))
            ]

        return results

    def find_similar_notes(self, note_id: int, limit: int = 5) -> List[Dict]:
        """
        Find notes similar to the given note
        """
        # Get note embedding
        note_embedding = self.db.get_embedding(note_id)

        if note_embedding is None:
            return []

        # Get all other note embeddings
        all_embeddings = self.db.get_all_embeddings()

        # Calculate similarities
        similarities = []
        for other_note_id, other_embedding in all_embeddings:
            if other_note_id == note_id:
                continue

            similarity = cosine_similarity(
                note_embedding.reshape(1, -1),
                other_embedding.reshape(1, -1)
            )[0][0]

            similarities.append((other_note_id, float(similarity)))

        # Sort and get top results
        similarities.sort(key=lambda x: x[1], reverse=True)

        results = []
        for other_note_id, similarity in similarities[:limit]:
            note = self.db.get_note(other_note_id)
            if note:
                note['similarity_score'] = similarity
                results.append(note)

        return results

    def reindex_all_notes(self):
        """
        Reindex all notes for semantic search
        Useful when model is updated or embeddings need to be regenerated
        """
        print("Reindexing all notes...")
        notes = self.db.get_all_notes()

        for idx, note in enumerate(notes):
            print(f"Indexing note {idx + 1}/{len(notes)}: {note['title']}")
            self.encode_note(note['id'], note['title'], note['content'])

        print("Reindexing complete!")

    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial query
        Returns list of note titles that match
        """
        if not partial_query or len(partial_query) < 2:
            return []

        notes = self.db.get_all_notes()
        suggestions = []

        partial_lower = partial_query.lower()

        for note in notes:
            title = note['title']
            if partial_lower in title.lower():
                suggestions.append(title)

            if len(suggestions) >= limit:
                break

        return suggestions
