# ui/app.py
import streamlit as st
import sys, os

# allow importing main.py from root folder
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import main  # contains load_document, rag_answer, chat_history

st.set_page_config(page_title="Documentation RAG Assistant", layout="wide")

# ------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "last_load_msg" not in st.session_state:
    st.session_state.last_load_msg = ""

# ------------------------------------------------------------
# DARK/LIGHT THEME SAFE CSS VARIABLES
# ------------------------------------------------------------
st.markdown("""
<style>
.user-bubble {
    background: var(--secondary-background-color);
    color: var(--text-color);
    padding: 14px 18px;
    border-radius: 12px;
    max-width: 80%;
    font-size: 16px;
}

.assistant-bubble {
    background: var(--background-color);
    color: var(--text-color);
    padding: 14px 18px;
    border-radius: 12px;
    max-width: 80%;
    font-size: 16px;
    border: 1px solid var(--secondary-background-color);
}

.message-row {
    display: flex;
    align-items: flex-start;
    margin-bottom: 14px;
}

.icon {
    font-size: 28px;
    margin-right: 10px;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# CALLBACK FOR SAFE INPUT CLEARING
# ------------------------------------------------------------
def submit_question():
    st.session_state.submitted_query = st.session_state.user_query
    st.session_state.user_query = ""


# ------------------------------------------------------------
# SIDEBAR — LOAD DOCUMENT
# ------------------------------------------------------------
# ------------------------------------------------------------
# SIDEBAR — LOAD DOCUMENT (.txt)
# ------------------------------------------------------------
st.sidebar.header("📄 Load Documentation (.txt)")

url = st.sidebar.text_input(
    "Document URL:",
    placeholder="Paste a .txt documentation link",
    value="",  # no default URL
)

if st.sidebar.button("Load Document"):
    if not url.strip():
        st.sidebar.error("⚠️ Please enter a valid .txt URL before loading.")
    else:
        msg = main.load_document(url.strip())
        st.session_state.last_load_msg = msg

        if msg.startswith("✅"):
            st.session_state.chat = []  # reset chat on new document
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)

# ------------------------------------------------------------
# MAIN TITLE
# ------------------------------------------------------------
st.title("🤖 Documentation RAG Assistant")
st.caption("Ask questions strictly based on the loaded .txt documentation.")

if st.session_state.last_load_msg:
    st.info(st.session_state.last_load_msg)

st.write("---")


# ------------------------------------------------------------
# CHAT DISPLAY FUNCTION (Theme Adaptive)
# ------------------------------------------------------------
def render_message(role, text):
    if role == "User":
        st.markdown(
            f"""
            <div class="message-row">
                <div class="icon">🧑</div>
                <div class="user-bubble"><strong>You:</strong><br>{text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="message-row">
                <div class="icon">🤖</div>
                <div class="assistant-bubble"><strong>Assistant:</strong><br>{text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ------------------------------------------------------------
# SHOW CHAT HISTORY
# ------------------------------------------------------------
for role, text in st.session_state.chat:
    render_message(role, text)

st.write("---")


# ------------------------------------------------------------
# DISABLE CHAT UNTIL DOCUMENT IS LOADED
# ------------------------------------------------------------
doc_loaded = st.session_state.last_load_msg.startswith("✅")

if not doc_loaded:
    st.text_input(
        "Ask a question:",
        key="user_query",
        placeholder="⚠️ Load a documentation file first...",
        disabled=True
    )
    st.warning("Please load a valid `.txt` documentation file using the sidebar.")
else:
    st.text_input(
        "Ask a question:",
        key="user_query",
        placeholder="Type your question…",
        on_change=submit_question
    )


# ------------------------------------------------------------
# HANDLE SUBMITTED QUESTION
# ------------------------------------------------------------
if doc_loaded and st.session_state.get("submitted_query"):
    query = st.session_state.submitted_query
    del st.session_state["submitted_query"]

    answer = main.rag_answer(query)

    st.session_state.chat.append(("User", query))
    st.session_state.chat.append(("Assistant", answer))

    st.rerun()
