from dotenv import load_dotenv
load_dotenv()

import requests

from infrastructure.chroma_adapter import ChromaVectorStore
from infrastructure.groq_adapter import GroqLLMProvider


# ----------------------------------------------
# GLOBAL STATE
# ----------------------------------------------
chat_history = []
vector_store = None
llm = GroqLLMProvider()


# ----------------------------------------------
# RESET FUNCTION — clears everything correctly
# ----------------------------------------------
def reset_chat_and_store():
    global chat_history, vector_store
    chat_history = []      # Clear chat
    vector_store = None    # Reset vector store
    print("🔄 Reset: Chat history and vector store cleared.")


# ----------------------------------------------
# LOAD DOCUMENT
# ----------------------------------------------
def load_document(url):
    global vector_store

    # Always reset before loading new document
    reset_chat_and_store()

    # Validate URL format
    if not url.lower().endswith(".txt"):
        return "❌ Invalid file type. Only .txt documentation files are allowed."

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return f"❌ Failed to load document (HTTP {resp.status_code})."
    except Exception as e:
        return f"❌ Error fetching document: {e}"

    text = resp.text.strip()

    if len(text) < 20:
        return "❌ Document is empty or too short."

    # Build vector store
    vector_store = ChromaVectorStore()
    vector_store.add_documents([text])
    vector_store.raw_text = text

    return "✅ Document loaded successfully!"


# ----------------------------------------------
# RAG ANSWER FUNCTION
# ----------------------------------------------
# ----------------------------------------------
# RAG ANSWER
# ----------------------------------------------
def rag_answer(query):
    global vector_store, chat_history

    if vector_store is None:
        return "❌ Load a document first."

    # Retrieve semantic chunks
    retrieved = vector_store.search(query, k=3)

    # Strict out-of-scope condition
    if not retrieved or len(" ".join(retrieved).strip()) == 0:
        topics = extract_topics(vector_store.raw_text)
        return build_out_of_scope_message(topics)

    # Build context
    context = "\n\n---\n\n".join(retrieved)

    prompt = f"""
You are a STRICT documentation assistant.

RULES:
- You may ONLY answer using the documentation provided in the CONTEXT below.
- If the answer is NOT explicitly written in the documentation, respond:
  "⚠️ This question is outside the scope of the provided document."
- DO NOT infer, DO NOT guess, DO NOT use external knowledge.
- DO NOT explain concepts unless the document explains them.
- DO NOT output any example or code unless the document contains it.

DOCUMENTATION CONTEXT:
----------------------
{context}

USER QUESTION:
{query}

YOUR RESPONSE:
- If the answer exists → summarize it in simple words.
- If it does NOT exist → output only the out-of-scope message.
"""

    answer = llm.generate(prompt)
    chat_history.append(("user", query))
    chat_history.append(("assistant", answer))

    return answer



# ----------------------------------------------
# Extract topic hints for out-of-scope replies
# ----------------------------------------------
def extract_topics(text):
    words = [w for w in text.replace("\n", " ").split() if w.isalpha() and len(w) > 4]
    unique = list(dict.fromkeys(words))
    return unique[:3] if len(unique) >= 3 else ["content", "document", "topics"]


# ----------------------------------------------
# Out-of-scope fallback message
# ----------------------------------------------
def build_out_of_scope_message(topics):
    return (
        "⚠️ **Your question is outside the scope of this document.**\n\n"
        "👉 Please ask questions ONLY about topics covered inside the loaded .txt file.\n\n"
        "**Detected topics in this document:**\n"
        f"• {topics[0]}\n• {topics[1]}\n• {topics[2]}\n\n"
        "**Example valid questions:**\n"
        f"• What is {topics[0]}?\n"
        f"• Explain {topics[1]}\n"
        f"• Purpose of {topics[2]}\n\n"
        "📌 *Note: This assistant answers strictly from the uploaded document.*"
    )
