# rag/orchestrator.py
import os
import time
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# ------------------------------------
# LLM Provider
# ------------------------------------
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("❌ GOOGLE_API_KEY missing in .env")

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0.0,
        max_output_tokens=512,
        api_key=api_key
    )


# ------------------------------------
# GRADER – checks if context contains the answer
# ------------------------------------
def grade_with_llm(llm, query: str, retrieved_chunks: List[str]) -> bool:
    """Returns True if LLM thinks the retrieved context contains the answer."""
    if not retrieved_chunks:
        return False

    context = "\n\n---\n\n".join(retrieved_chunks[:3])

    prompt = f"""
You are a strict YES/NO grader.

DOCUMENTATION:
{context}

QUESTION:
{query}

Does the documentation contain enough information to answer the question?

Respond with ONLY YES or NO.
"""

    try:
        out = llm.predict(prompt)
    except Exception:
        time.sleep(0.1)
        out = llm.predict(prompt)

    return str(out).strip().upper().startswith("Y")


# ------------------------------------
# FINAL ANSWER GENERATOR
# ------------------------------------
def generate_answer_with_llm(llm, query: str, retrieved_chunks: List[str]) -> str:
    """Produce the final grounded answer from Gemini."""
    context = "\n\n---\n\n".join(retrieved_chunks)

    out_of_scope = "⚠️ This question is outside the scope of the provided document."

    prompt = f"""
You are a documentation assistant. Use ONLY the provided context.

DOCUMENTATION:
{context}

QUESTION:
{query}

If the answer does NOT exist in the document, respond exactly:
"{out_of_scope}"
"""

    # Primary safe call
    try:
        return llm.predict(prompt).strip()

    # Fallback: Use invoke message API
    except Exception:
        msg = HumanMessage(content=prompt)
        out = llm.invoke([msg])
        return out.content.strip()
