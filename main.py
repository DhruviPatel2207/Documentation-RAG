# main.py

from dotenv import load_dotenv
load_dotenv()


from infrastructure.chroma_adapter import ChromaVectorStore
from infrastructure.openrouter_adapter import OpenRouterLLM

# Global pipeline state
vector_store = None
chat_history = []  # list of ChatMessage
raw_text = ""      # last loaded document text
llm = OpenRouterLLM()  # will raise if OPENROUTER_API_KEY not provided


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 50):
    """
    Simple sliding-window chunker by characters. Returns list of chunks.
    """
    text = text.replace("\r\n", "\n")
    n = len(text)
    chunks = []
    start = 0
    while start < n:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def extract_topics_from_document(text: str):
    """
    Extracts 3 high-level keywords from the document to show as scope guidance.
    """
    words = [
        w.strip().lower()
        for w in text.replace("\n", " ").split()
        if w.isalpha() and 4 < len(w) < 20
    ]

    if not words:
        return ["document", "content", "topics"]

    unique = list(dict.fromkeys(words))
    return unique[:3] if len(unique) >= 3 else unique + ["topic", "reference"]

# ---------- Reset ----------
def reset_chat_and_store():
    global chat_history, vector_store, raw_text
    chat_history = []
    raw_text = ""
    if vector_store:
        try:
            vector_store.reset()
        except Exception:
            pass
    vector_store = None

def load_document(url: str):
    global vector_store, raw_text, chat_history
    reset_chat_and_store()

    # 1. BASIC URL VALIDATION

    if not url.startswith("http://") and not url.startswith("https://"):
        return "❌ Invalid URL format. Please enter a valid http/https link."

    if not url.lower().endswith(".txt"):
        return "❌ Only .txt documentation files are supported."

    # 2. TRY FETCHING DOCUMENT

    import requests
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.MissingSchema:
        return "❌ Invalid URL. Please check the link again."
    except requests.exceptions.ConnectionError:
        return "❌ Could not connect to the URL. Network or domain error."
    except requests.exceptions.Timeout:
        return "❌ Request timed out. The server is too slow or unreachable."
    except Exception as e:
        return f"❌ Unexpected network error: {e}"


    # 3. HTTP STATUS CHECK

    if response.status_code == 404:
        return "❌ Document not found (404). Please check the URL."
    elif response.status_code == 403:
        return "❌ Access denied (403). The server is blocking this file."
    elif response.status_code != 200:
        return f"❌ Error loading document (HTTP {response.status_code})."


    # 4. TEXT VALIDATION

    text = response.text.strip()
    if len(text) < 20:
        return "❌ Document is empty or too short to index."

    # 5. VECTOR STORE SETUP

    raw_text = text
    chunks = chunk_text(text, chunk_size=1200, overlap=100)

    vector_store = ChromaVectorStore()
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    vector_store.add_documents(chunks, ids=ids)

    chat_history = []
    return f"✅ Document loaded successfully ({len(chunks)} chunks)."


# ---------- RAG + Forced Answer (Mode C) ----------
def rag_answer(query: str, k: int = 3):
    global vector_store, chat_history, raw_text

    if vector_store is None:
        return "❌ Please load a document before asking questions."

    # Retrieve top-k relevant chunks
    retrieved = vector_store.similarity_search(query, k=k)

    # ---------- CASE: NO MATCH FOUND ----------
    if not retrieved or all(len(r.strip()) == 0 for r in retrieved):

        topics = extract_topics_from_document(raw_text)

        return (
            "❗ **The requested information is not present in the loaded document.**\n\n"
            "This documentation primarily covers:\n"
            f"• {topics[0]}\n"
            f"• {topics[1]}\n"
            f"• {topics[2]}\n\n"
            "Please ask questions related to these topics."
        )

    # ---------- CASE: MATCH FOUND → Answer strictly from doc ----------
    context = "\n\n---\n\n".join(retrieved)

    system_prompt = (
        "You are a documentation-strict assistant. "
        "Answer ONLY using the content provided in the DOCUMENTATION CONTEXT. "
        "Do not use outside knowledge. Do not guess. "
        "If the answer is not directly stated in the context, respond: 'The document does not provide this information.'"
    )

    user_prompt = (
        f"DOCUMENTATION CONTEXT:\n{context}\n\n"
        f"USER QUESTION:\n{query}\n\n"
        "Provide a concise, factual answer based only on the context above."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    answer = llm.generate(messages)

    chat_history.append(("user", query))
    chat_history.append(("assistant", answer))

    return answer
