import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import streamlit as st
from main import load_document, rag_answer, chat_history, reset_chat_and_store

st.set_page_config(page_title="Documentation RAG Assistant", layout="wide")

st.title("📄 Documentation RAG Assistant")
st.caption("Load .txt documentation files (like SvelteKit llms.txt) and ask grounded questions.")

url = st.text_input("Document URL (.txt required)")

if st.button("Load Document"):
    reset_chat_and_store()   # fully clears chat + vector store
    msg = load_document(url)
    st.write(msg)

st.write("### 💬 Chat with the document")
query = st.text_input("Ask a question:")

if st.button("Ask"):
    answer = rag_answer(query)
    st.write("📌 **Answer:**")
    st.write(answer)

# Chat history
if chat_history:
    st.write("### 📝 Chat History")
    for role, msg in chat_history:
        st.write(f"**{role}:** {msg}")
