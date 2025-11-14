import faiss
import numpy as np
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

from .config import INDEX_DIR


class Retriever:
    def __init__(self):
        # Load FAISS index
        self.index_path = INDEX_DIR / "rag.index"
        self.index = faiss.read_index(str(self.index_path))

        # Load metadata (LIST, not dict)
        metadata_path = INDEX_DIR / "metadata.json"
        self.metadata = json.loads(Path(metadata_path).read_text())

        # Embedding model
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def retrieve(self, query, k=5):
        query_emb = self.model.encode([query]).astype(np.float32)
        D, I = self.index.search(query_emb, k)

        results = []
        for idx in I[0]:
            if idx == -1:
                continue
            results.append(self.metadata[idx])   # INTEGER index

        return results
