# utils/embeddings.py

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def generate_embedding(text: str):
    model = get_model()
    return model.encode(text)


def generate_embeddings(texts):
    model = get_model()
    return model.encode(texts)