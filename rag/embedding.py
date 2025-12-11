# rag/embedding.py
from sentence_transformers import SentenceTransformer
from typing import List
import threading

# create singleton model with lazy init (thread-safe)
_model = None
_lock = threading.Lock()

def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Return list of vector embeddings for each input text.
    """
    model = _get_model()
    emb = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    # convert numpy arrays to lists for Chroma
    return [v.tolist() for v in emb]

def embed_query(text: str) -> List[float]:
    model = _get_model()
    v = model.encode([text], show_progress_bar=False, convert_to_numpy=True)[0]
    return v.tolist()
