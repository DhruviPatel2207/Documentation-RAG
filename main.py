# main.py
import os
from dotenv import load_dotenv
load_dotenv()

from loaders.web_loader import validate_txt_url, fetch_text_from_url
from rag.vector_store import ChromaVectorStore
from rag.orchestrator import get_llm, grade_with_llm, generate_answer_with_llm
from typing import List

# chunking parameters
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [" ".join(words)]
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

class DocumentPipeline:
    def __init__(self):
        self.vs: ChromaVectorStore | None = None
        self.llm = get_llm()
        self.raw_text = ""
        # history is stored in streamlit session, but we keep a local representation too
        self.chat_history = []

    def reset(self):
        if self.vs:
            try:
                self.vs.reset()
            except Exception:
                pass
        self.vs = None
        self.raw_text = ""
        self.chat_history = []

    def load_from_url(self, url: str) -> str:
        # reset prior
        self.reset()

        if not validate_txt_url(url):
            return "❌ Invalid URL or not a .txt file."

        try:
            text = fetch_text_from_url(url)
        except Exception as e:
            return f"❌ Error fetching document: {e}"

        text = text.strip()
        if not text or len(text) < 20:
            return "❌ Empty or too short document."

        chunks = chunk_text(text)
        self.vs = ChromaVectorStore()
        # add chunks to vector store
        try:
            self.vs.add_texts(chunks)
        except Exception as e:
            # if chroma errors with existing collection, try reset then add
            try:
                self.vs.reset()
                self.vs.add_texts(chunks)
            except Exception as e2:
                return f"❌ Error storing chunks: {e2}"

        self.raw_text = text
        return f"✅ Document loaded ({len(chunks)} chunks)."

    def ask(self, query: str) -> str:
        if not self.vs:
            return "❌ Load a document first."

        # retrieve
        retrieved = self.vs.search(query, k=5)
        # grade retrieved
        try:
            relevant = grade_with_llm(self.llm, query, retrieved)
        except Exception:
            # fallback: if retrieval returned non-empty, assume possibly relevant
            relevant = len(retrieved) > 0

        if not relevant:
            # build friendly hint message from top chunks
            hints = (self.vs.raw_chunks[:3] if self.vs and self.vs.raw_chunks else [])
            sample_topics = [(" ".join(h.split()[:10]) + "...") for h in hints]
            hint_text = "\n".join(f"- {t}" for t in sample_topics) if sample_topics else "- (no hint available)"
            return (
                "⚠️ This question appears to be outside the scope of the loaded document.\n\n"
                "Try asking about topics present in the document, for example:\n" + hint_text
            )

        answer = generate_answer_with_llm(self.llm, query, retrieved)
        # add to local history
        self.chat_history.append(("user", query))
        self.chat_history.append(("assistant", answer))
        return answer

# single global instance used by Streamlit app
pipeline = DocumentPipeline()
