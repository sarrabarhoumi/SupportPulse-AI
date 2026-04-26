import re
from typing import List

STOPWORDS = {
    'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 'a', 'au', 'aux', 'en', 'sur', 'pour',
    'avec', 'dans', 'est', 'sont', 'je', 'nous', 'vous', 'il', 'elle', 'ils', 'elles', 'ce', 'cet', 'cette',
    'mon', 'ma', 'mes', 'notre', 'nos', 'votre', 'vos', 'que', 'qui', 'quoi', 'ne', 'pas', 'plus', 'par',
    'se', 'sa', 'son', 'leurs', 'leur', 'd', 'l', 'm', 'n', 't'
}


def clean_text(text: str) -> str:
    text = (text or '').replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_text(text: str) -> str:
    text = clean_text(text).lower()
    text = re.sub(r'[^a-z0-9àâçéèêëîïôûùüÿñæœ\s@.-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    return [t for t in normalize_text(text).split() if len(t) > 2 and t not in STOPWORDS]


def summarize_text(text: str, max_sentences: int = 2, max_chars: int = 240) -> str:
    text = clean_text(text)
    if not text:
        return ''
    sentences = re.split(r'(?<=[.!?])\s+', text)
    kept = []
    total = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        kept.append(sentence)
        total += len(sentence)
        if len(kept) >= max_sentences or total >= max_chars:
            break
    result = ' '.join(kept).strip()
    return result[:max_chars].rstrip() + ('...' if len(result) > max_chars else '')
