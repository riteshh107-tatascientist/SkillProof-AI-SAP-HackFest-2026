"""Optional pretrained sentence-embedding layer (sentence-transformers, all-MiniLM-L6-v2) with a TF-IDF fallback.
Install with: pip install -r requirements-optional.txt  (downloads ~90 MB model once). Disable with ENABLE_SEMANTIC=off."""
import functools
import numpy as np
from config import get_secret
from models.matching_model import tfidf_similarity
from models.skill_model import get_taxonomy

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@functools.lru_cache(maxsize=1)
def _load():
    if get_secret("ENABLE_SEMANTIC", "auto").lower() == "off": return None
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(MODEL_NAME)
    except Exception:
        return None


def available() -> bool:
    return _load() is not None


def engine_name() -> str:
    return "semantic (MiniLM embeddings)" if available() else "TF-IDF (install requirements-optional.txt for semantic)"


def _embed(texts):
    return _load().encode(list(texts), normalize_embeddings=True, show_progress_bar=False)


def similarity(a: str, b: str) -> float:
    if not (a or "").strip() or not (b or "").strip(): return 0.0
    if available():
        v = _embed([a[:4000], b[:4000]]); return float(np.clip(v[0] @ v[1], 0, 1))
    return tfidf_similarity(a, b)


@functools.lru_cache(maxsize=1)
def _skill_vectors():
    tax = get_taxonomy()
    docs = [f"{s}: {', '.join(tax.synonyms[s][:4])}" if tax.synonyms[s] else s for s in tax.names]
    return tax.names, _embed(docs)


def semantic_hits(sentences, exclude, threshold=0.6):
    """Skills implied by a sentence but not literally named (e.g. 'built dashboards' -> Data Visualization). Weak suggestions."""
    if not available() or not sentences: return []
    names, vecs = _skill_vectors(); sv = _embed([s[:300] for s in sentences]); sims = sv @ vecs.T
    out = {}
    for j, name in enumerate(names):
        if name in exclude: continue
        i = int(np.argmax(sims[:, j]))
        if sims[i, j] >= threshold: out[name] = (float(sims[i, j]), sentences[i])
    return out
