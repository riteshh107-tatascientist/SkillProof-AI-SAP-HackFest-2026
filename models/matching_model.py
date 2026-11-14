"""Pure scoring maths: weighted skill coverage and TF-IDF cosine similarity (text baseline)."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REQ_WEIGHT, PREF_WEIGHT = 0.7, 0.3


def coverage(have: set, wanted: list):
    wanted = list(dict.fromkeys(wanted))
    matched = [s for s in wanted if s in have]
    return (len(matched) / len(wanted) if wanted else 1.0), matched, [s for s in wanted if s not in have]


def weighted_score(req_cov: float, pref_cov: float) -> float:
    return round(100 * (REQ_WEIGHT * req_cov + PREF_WEIGHT * pref_cov), 1)


def tfidf_similarity(doc: str, corpus_doc: str) -> float:
    if not (doc or "").strip() or not (corpus_doc or "").strip(): return 0.0
    try:
        m = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform([doc, corpus_doc])
        return float(cosine_similarity(m[0], m[1])[0][0])
    except ValueError:
        return 0.0
