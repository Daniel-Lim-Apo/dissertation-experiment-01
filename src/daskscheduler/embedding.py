# embedding.py
from sentence_transformers import SentenceTransformer

_model = None

def compute_embedding(text: str) -> list[float]:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model.encode(text).tolist()
