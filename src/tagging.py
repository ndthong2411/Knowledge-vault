"""
Auto-tagging system for Knowledge Vault
Uses YAKE for keyword extraction to suggest tags
"""
import re
from typing import List, Set
import yake

from config import (
    MAX_TAGS,
    MIN_TAG_LENGTH,
    YAKE_LANGUAGE,
    YAKE_MAX_NGRAM,
    YAKE_DEDUPLICATION_THRESHOLD
)


class AutoTagger:
    """Automatic tag suggestion system"""

    def __init__(self):
        # Initialize YAKE keyword extractor
        self.kw_extractor = yake.KeywordExtractor(
            lan=YAKE_LANGUAGE,
            n=YAKE_MAX_NGRAM,
            dedupLim=YAKE_DEDUPLICATION_THRESHOLD,
            top=MAX_TAGS * 2,  # Extract more, then filter
            features=None
        )

        # Common stop words to exclude from tags (English + Vietnamese)
        self.stop_words = {
            # English
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            # Vietnamese
            'và', 'hoặc', 'nhưng', 'của', 'cho', 'từ', 'với', 'bởi', 'là',
            'được', 'có', 'các', 'này', 'đó', 'những', 'tôi', 'bạn', 'chúng',
            'trong', 'trên', 'ở', 'về', 'đến', 'rằng', 'để', 'như', 'khi',
            'nếu', 'hay', 'thì', 'sẽ', 'đã', 'cũng', 'không', 'chỉ', 'rất'
        }

    def suggest_tags(self, title: str, content: str, max_tags: int = MAX_TAGS) -> List[str]:
        """
        Suggest tags based on note title and content
        Returns a list of suggested tag strings
        """
        # Combine title and content, giving more weight to title
        text = f"{title} {title} {content}"

        # Extract keywords using YAKE
        keywords = self.kw_extractor.extract_keywords(text)

        # Process and filter keywords
        suggested_tags = []
        seen_tags = set()

        for keyword, score in keywords:
            # Clean and normalize tag
            tag = self._normalize_tag(keyword)

            if not tag:
                continue

            # Filter out invalid tags
            if (len(tag) < MIN_TAG_LENGTH or
                tag in self.stop_words or
                tag in seen_tags or
                tag.isdigit()):
                continue

            suggested_tags.append(tag)
            seen_tags.add(tag)

            if len(suggested_tags) >= max_tags:
                break

        # If no tags found from YAKE, try simple word frequency
        if not suggested_tags:
            suggested_tags = self._fallback_tag_extraction(text, max_tags)

        return suggested_tags

    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text (e.g., #python, #machinelearning)
        """
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, text)

        # Normalize and filter
        tags = []
        for tag in hashtags:
            normalized = self._normalize_tag(tag)
            if normalized and len(normalized) >= MIN_TAG_LENGTH:
                tags.append(normalized)

        return list(set(tags))  # Remove duplicates

    def merge_tags(self, suggested_tags: List[str], user_tags: List[str],
                   hashtags: List[str] = None) -> List[str]:
        """
        Merge suggested tags with user-provided tags and hashtags
        Prioritize user tags > hashtags > suggested tags
        """
        merged = []
        seen = set()

        # Add user tags first
        for tag in user_tags:
            tag = self._normalize_tag(tag)
            if tag and tag not in seen:
                merged.append(tag)
                seen.add(tag)

        # Add hashtags
        if hashtags:
            for tag in hashtags:
                tag = self._normalize_tag(tag)
                if tag and tag not in seen:
                    merged.append(tag)
                    seen.add(tag)

        # Add suggested tags
        for tag in suggested_tags:
            if len(merged) >= MAX_TAGS:
                break
            tag = self._normalize_tag(tag)
            if tag and tag not in seen:
                merged.append(tag)
                seen.add(tag)

        return merged[:MAX_TAGS]

    def _normalize_tag(self, tag: str) -> str:
        """
        Normalize a tag string
        """
        # Convert to lowercase
        tag = tag.lower().strip()

        # Remove special characters except hyphens and underscores
        tag = re.sub(r'[^\w\s-]', '', tag)

        # Replace spaces with hyphens
        tag = re.sub(r'\s+', '-', tag)

        # Remove leading/trailing hyphens
        tag = tag.strip('-_')

        return tag

    def _fallback_tag_extraction(self, text: str, max_tags: int) -> List[str]:
        """
        Fallback method using simple word frequency when YAKE fails
        """
        # Tokenize and clean
        words = re.findall(r'\b\w+\b', text.lower())

        # Count word frequency
        word_freq = {}
        for word in words:
            if (len(word) >= MIN_TAG_LENGTH and
                word not in self.stop_words and
                not word.isdigit()):
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Return top N
        tags = [word for word, freq in sorted_words[:max_tags]]

        return tags

    def validate_tags(self, tags: List[str]) -> List[str]:
        """
        Validate and clean a list of tags
        """
        validated = []
        seen = set()

        for tag in tags:
            tag = self._normalize_tag(tag)
            if (tag and
                len(tag) >= MIN_TAG_LENGTH and
                tag not in seen and
                tag not in self.stop_words):
                validated.append(tag)
                seen.add(tag)

        return validated[:MAX_TAGS]

    def get_related_tags(self, tag: str, all_tags: List[str], max_related: int = 5) -> List[str]:
        """
        Find tags that are related to the given tag
        Uses simple string similarity
        """
        tag = self._normalize_tag(tag)
        if not tag:
            return []

        related = []

        for other_tag in all_tags:
            other_tag = self._normalize_tag(other_tag)
            if other_tag == tag:
                continue

            # Simple substring matching
            if tag in other_tag or other_tag in tag:
                related.append(other_tag)

        return related[:max_related]
