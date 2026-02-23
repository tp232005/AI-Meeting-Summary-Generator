import re
import string


def clean_text(text: str) -> str:
    """Remove noise, normalize whitespace, and clean meeting transcripts."""
    # Remove timestamps like [00:01:23] or (00:01)
    text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', text)
    # Remove speaker labels like "John:" or "Speaker 1:"
    text = re.sub(r'^[A-Z][a-zA-Z\s]+\d*:\s*', '', text, flags=re.MULTILINE)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using simple heuristics."""
    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """Extract simple keyword candidates by frequency (non-stopword nouns)."""
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
        'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'that', 'this', 'it',
        'we', 'i', 'you', 'he', 'she', 'they', 'them', 'our', 'their',
        'about', 'up', 'so', 'as', 'if', 'not', 'also', 'just', 'very',
    }
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    freq = {}
    for word in words:
        if word not in stopwords:
            freq[word] = freq.get(word, 0) + 1
    sorted_words = sorted(freq, key=freq.get, reverse=True)
    return sorted_words[:top_n]


def preprocess(text: str) -> dict:
    """Full preprocessing pipeline."""
    cleaned = clean_text(text)
    sentences = split_sentences(cleaned)
    keywords = extract_keywords(cleaned)
    return {
        'cleaned_text': cleaned,
        'sentences': sentences,
        'keywords': keywords,
        'word_count': len(cleaned.split()),
        'sentence_count': len(sentences),
    }
