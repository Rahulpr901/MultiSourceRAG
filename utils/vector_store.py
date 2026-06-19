# utils/vector_store.py

from __future__ import annotations

import os
import pickle
from typing import List, Dict

import faiss
import numpy as np

from utils.embeddings import generate_embeddings


class FAISSVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata_store: List[Dict] = []

    def add_documents(self, documents: List[Dict]):
        """
        Add chunked documents into FAISS.
        """
        if not documents:
            return

        texts = [doc["content"] for doc in documents]
        embeddings = generate_embeddings(texts)
        embeddings = np.array(embeddings).astype("float32")

        self.index.add(embeddings)
        self.metadata_store.extend(documents)

    def search(self, query: str, top_k: int = 5):
        """
        Search relevant chunks.
        """
        if self.index.ntotal == 0 or len(self.metadata_store) == 0:
            return []

        top_k = min(top_k, self.index.ntotal)

        query_embedding = generate_embeddings([query])
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            if idx == -1:
                continue
            if 0 <= idx < len(self.metadata_store):
                results.append(self.metadata_store[idx])

        return results

    def save(self, index_path: str, metadata_path: str):
        """
        Save FAISS index and metadata.
        """
        faiss.write_index(self.index, index_path)

        with open(metadata_path, "wb") as f:
            pickle.dump(self.metadata_store, f)

    def load(self, index_path: str, metadata_path: str):
        """
        Load FAISS index and metadata.
        """
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)

        if os.path.exists(metadata_path):
            with open(metadata_path, "rb") as f:
                self.metadata_store = pickle.load(f)