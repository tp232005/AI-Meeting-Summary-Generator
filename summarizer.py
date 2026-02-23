import re
import math
from collections import defaultdict


def _score_sentences(sentences: list[str], keywords: list[str]) -> dict[int, float]:
    """Score sentences by keyword density and position."""
    keyword_set = set(keywords)
    scores = {}
    total = len(sentences)
    for i, sentence in enumerate(sentences):
        words = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
        if not words:
            scores[i] = 0.0
            continue
        keyword_hits = sum(1 for w in words if w in keyword_set)
        keyword_score = keyword_hits / len(words)
        # Boost first and last sentences
        position_score = 0.1 if i == 0 or i == total - 1 else 0.0
        # Penalize very short or very long sentences
        length_score = min(len(words), 30) / 30
        scores[i] = keyword_score * 0.6 + position_score * 0.2 + length_score * 0.2
    return scores


def extractive_summary(sentences: list[str], keywords: list[str], num_sentences: int = 5) -> str:
    """Return an extractive summary by picking the top-scored sentences."""
    if not sentences:
        return ""
    num_sentences = min(num_sentences, len(sentences))
    scores = _score_sentences(sentences, keywords)
    top_indices = sorted(scores, key=scores.get, reverse=True)[:num_sentences]
    # Preserve original order
    top_indices = sorted(top_indices)
    return ' '.join(sentences[i] for i in top_indices)


def bullet_points(sentences: list[str], keywords: list[str], num_bullets: int = 5) -> list[str]:
    """Return bullet-point action items / key highlights."""
    if not sentences:
        return []
    scores = _score_sentences(sentences, keywords)
    top_indices = sorted(scores, key=scores.get, reverse=True)[:num_bullets]
    top_indices = sorted(top_indices)
    return [sentences[i] for i in top_indices]


def summarize(preprocessed: dict, length: str = 'medium') -> dict:
    """
    Master summarize function.
    length: 'short' (3 sentences), 'medium' (5), 'long' (8)
    """
    length_map = {'short': 3, 'medium': 5, 'long': 8}
    n = length_map.get(length, 5)

    sentences = preprocessed['sentences']
    keywords = preprocessed['keywords']

    summary = extractive_summary(sentences, keywords, num_sentences=n)
    bullets = bullet_points(sentences, keywords, num_bullets=min(n, 5))

    return {
        'summary': summary,
        'bullet_points': bullets,
        'length_setting': length,
        'original_sentences': preprocessed['sentence_count'],
        'summary_sentences': n,
    }
