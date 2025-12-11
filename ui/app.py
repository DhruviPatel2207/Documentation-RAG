# ui/app.py

import streamlit as st
import sys, os

# allow importing main.py from parent folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import pipeline

# ---------------------- PAGE SETTINGS ----------------------
st.set_page_config(page_title="Documentation RAG Assistant", layout="wide")
st.title("📄 Documentation RAG Assistant — Gemini + ChromaDB RAG")


# ---------------------- INIT SESSION ----------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "last_load_msg" not in st.session_state:
    st.session_state.last_load_msg = ""


# ---------------------- SIDEBAR ----------------------
st.sidebar.header("Load a .txt documentation URL")

url = st.sidebar.text_input("Document URL (.txt recommended):",
                            value="https://svelte.dev/docs/kit/hooks/llms.txt")

if st.sidebar.button("Load Document"):
    msg = pipeline.load_from_url(url.strip())

    # reset chat on successful load
    if msg.startswith("✅"):
        st.session_state.chat = []
        st.sidebar.success(msg)
    else:
        st.sidebar.error(msg)

    st.session_state.last_load_msg = msg



# ---------------------- UI STYLES ----------------------
st.markdown("""
<style>

.chat-container {
    width: 100%;
    margin-top: 10px;
}

.user-msg {
    background-color: #1e1e1e;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    display: flex;
    gap: 12px;
    font-size: 17px;
    border: 1px solid #333;
}

.bot-msg {
    background-color: #2d2d2d;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    display: flex;
    gap: 12px;
    font-size: 17px;
    border: 1px solid #444;
}

.icon-user {
    font-size: 26px;
    min-width: 32px;
}

.icon-bot {
    font-size: 26px;
    min-width: 32px;
}

.msg-text {
    flex-grow: 1;
}

.chat-box {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 10px;
    margin-top: 20px;
}

.question-box input {
    font-size: 18px !important;
}

</style>
""", unsafe_allow_html=True)



# ---------------------- MAIN CHAT UI ----------------------
st.subheader("Chat with the loaded document")
st.write(st.session_state.last_load_msg)
# ---------------------- DISPLAY CHAT HISTORY ----------------------
# ---------------------- DISPLAY CHAT HISTORY ----------------------
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

for role, msg in st.session_state.chat:
    if role == "You":
        st.markdown(
            f"""
            <div class="chat-container user-msg">
                <div class="icon-user"> 👤 </div>
                <div class="msg-text">{msg}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="chat-container bot-msg">
                <div class="icon-bot"> 🤖 </div>
                <div class="msg-text">{msg}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ❌ DO NOT USE key="user_query" (causes modification error)
query = st.text_input("Ask a question:")

if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        # call pipeline
        answer = pipeline.ask(query)
        st.session_state.chat.append(("You", query))
        st.session_state.chat.append(("Assistant", answer))

        # CLEAR the input by rerunning the script
        st.experimental_set_query_params()  
        st.rerun()     # ❗ This safely resets the widget without error


