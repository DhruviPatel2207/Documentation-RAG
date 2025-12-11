# rag/vector_store.py
import os
import chromadb
from chromadb.config import Settings
from typing import List
from rag.embedding import embed_texts, embed_query

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR") or None

def get_chroma_client():
    try:
        if PERSIST_DIR:
            return chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=PERSIST_DIR))
        else:
            return chromadb.Client()
    except Exception:
        # final fallback
        return chromadb.Client()

class ChromaVectorStore:
    """
    Minimal wrapper around chroma collection for documents (chunks).
    """

    def __init__(self, collection_name: str = "docs"):
        self.client = get_chroma_client()
        self.collection_name = collection_name
        # try to delete existing collection (safe)
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        # create fresh collection
        self.collection = self.client.create_collection(name=self.collection_name)
        self.raw_chunks: List[str] = []

    def add_texts(self, texts: List[str]):
        """
        Add documents (texts) to chroma with local sentence-transformers embeddings.
        """
        if not texts:
            return
        ids = [str(len(self.raw_chunks) + i) for i in range(len(texts))]
        embeddings = embed_texts(texts)
        try:
            self.collection.add(ids=ids, documents=texts, embeddings=embeddings)
        except TypeError:
            # fallback for older chroma versions
            self.collection.add(documents=texts, ids=ids)
        self.raw_chunks.extend(texts)

    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Return top-k documents (strings) most relevant to the query.
        """
        q_emb = embed_query(query)
        try:
            res = self.collection.query(query_embeddings=[q_emb], n_results=k, include=["documents", "distances"])
            docs = res.get("documents", [[]])[0]
        except Exception:
            # fallback: try without include
            res = self.collection.query(query_embeddings=[q_emb], n_results=k)
            docs = res.get("documents", [[]])[0] if isinstance(res, dict) else []
        # ensure strings
        return [d for d in docs if isinstance(d, str)]

    def reset(self):
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.create_collection(name=self.collection_name)
        self.raw_chunks = []
