# 📄 Documentation RAG Assistant

A Retrieval-Augmented Generation (RAG) system that allows users to load `.txt` documentation files and ask questions
strictly based on the loaded content. Built with clean architecture principles, this assistant prevents hallucinations
by ensuring answers come only from the provided documentation.

![Dashboard](assets/dashboard.png)

## 🎯 Features

- **Document-Strict Responses**: Answers only from loaded documentation, no external knowledge
- **Smart Scope Detection**: Automatically identifies document topics when queries are out of scope
- **Real-time RAG Pipeline**: Vector-based semantic search with ChromaDB
- **Clean UI**: Streamlit-based interface with theme-adaptive chat bubbles
- **Error Handling**: Comprehensive validation for URLs, HTTP errors, and empty documents
- **Chat History**: Maintains conversation context throughout the session

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
Documentation-RAG/
├── core/
│   └── entities.py              # Domain entities (DocumentChunk, ChatMessage)
├── infrastructure/
│   ├── chroma_adapter.py        # Vector store implementation (ChromaDB)
│   ├── openrouter_adapter.py   # LLM integration (OpenRouter API)
│   └── web_loader.py            # Document fetching utilities
├── ui/
│   └── app.py                   # Streamlit web interface
├── main.py                      # Application logic & RAG pipeline
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (API keys)
└── assets/                      # Screenshots for documentation
```

### Layer Responsibilities

- **Core**: Business entities and domain models
- **Infrastructure**: External services (vector DB, LLM, web requests)
- **UI**: Presentation layer (Streamlit)
- **Main**: Orchestration and RAG pipeline logic

## 🚀 Setup Instructions

### Prerequisites

- **Python Version**: 3.13.9 (recommended) or 3.10+
- **IDE**: PyCharm (used in development) or VS Code
- **Operating System**: macOS, Linux, or Windows

### Step 1: Clone the Repository

```bash
git clone https://github.com/DhruviPatel2207/Documentation-RAG.git
cd Documentation-RAG
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**

```
chromadb>=0.5.0
streamlit
requests
sentence-transformers
numpy
tqdm
python-dotenv
```

### Step 4: Configure API Key

1. Visit [OpenRouter Keys](https://openrouter.ai/settings/keys) and create an account
2. Generate a new API key
3. Create a `.env` file in the project root:

```bash
touch .env
```

4. Add your API key to `.env`:

```env
OPENROUTER_API_KEY=your_api_key_here
```

⚠️ **Important**: OpenRouter's free tier allows **20 requests per day**. For additional usage beyond the free quota, you
can set up billing in your OpenRouter account settings.

### Step 5: Run the Application

```bash
streamlit run ui/app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Loading a Document

1. Enter a valid `.txt` file URL in the sidebar
    - Example: `https://svelte.dev/docs/kit/shallow-routing/llms.txt`
2. Click **"Load Document"**
3. Wait for confirmation: ✅ Document loaded successfully (X chunks)

![Document Loaded](assets/document_loaded.png)

### Asking Questions

1. Type your question in the input box
2. Press Enter to submit
3. The assistant will retrieve relevant sections and answer based solely on the document

**Sample Questions**:

- "How do I use `pushState` to create a new history entry without reloading the page?"
- "How should I handle the `onclick` event on `<a>` tags to implement shallow routing (including checks for modifier
  keys like Shift/Ctrl)?"
- "How do I populate `event.locals` to pass data to handlers?"
- "How do I define TypeScript types for `App.Locals`?"

![Chat Example](assets/chat_1.png)

![Chat 2](assets/chat_2.png)

![Chat 3](assets/chat_3.png)

![Chat UI](assets/chat_4.png)

## 🛡️ Error Handling

The system includes comprehensive error handling:

### URL Validation

- ❌ Invalid URL format (non-http/https)
- ❌ Non-.txt file extensions

![Invalid URL](assets/invalid_url.png)

### HTTP Errors

- **404**: Document not found
- **Connection errors**: Network/DNS issues
- **Timeouts**: Server unresponsive

![Document Not Found](assets/document_not_found.png)

### Content Validation

- ❌ Empty or very short documents (< 20 characters)
- ❌ Failed vector indexing

## 🧠 How It Works

### RAG Pipeline

1. **Document Loading**
    - Fetch `.txt` file from URL
    - Validate content and HTTP status
    - Split into overlapping chunks (1200 chars, 100 overlap)

2. **Vector Indexing**
    - Generate embeddings using `sentence-transformers/all-MiniLM-L6-v2`
    - Store in ChromaDB with cosine similarity

3. **Query Processing**
    - User asks a question
    - Generate query embedding
    - Retrieve top-k relevant chunks (default k=3)

4. **Answer Generation**
    - If no relevant chunks: Return scope guidance
    - If chunks found: Send to LLM with strict prompt
    - LLM (Mistral Devstral-2512) answers only from context

### Preventing Hallucinations

The system uses a **strict prompt template**:

```
"You are a documentation-strict assistant. 
Answer ONLY using the content provided in the DOCUMENTATION CONTEXT. 
Do not use outside knowledge. Do not guess. 
If the answer is not directly stated in the context, respond: 
'The document does not provide this information.'"
```

## 📊 Technical Specifications

| Component          | Technology                               |
|--------------------|------------------------------------------|
| **Vector DB**      | ChromaDB (persistent storage)            |
| **Embeddings**     | sentence-transformers (all-MiniLM-L6-v2) |
| **LLM**            | Mistral Devstral-2512 via OpenRouter     |
| **Frontend**       | Streamlit                                |
| **HTTP Client**    | requests                                 |
| **Python Version** | 3.13.9                                   |

## 🐛 Troubleshooting

### Issue: "OPENROUTER_API_KEY not set"

**Solution**: Ensure `.env` file exists in the project root with the correct key:

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

### Issue: Rate limit exceeded (429 error)

**Solution**: OpenRouter's free tier is limited to **20 requests per day**. Once you've used your daily quota:

- Set up billing in your OpenRouter account to continue using the service
- Get your API key from: https://openrouter.ai/settings/keys

### Issue: ChromaDB permission errors

**Solution**: Delete the `chroma_data/` folder and restart:

```bash
rm -rf chroma_data/
streamlit run ui/app.py
```

### Issue: Streamlit not opening in browser

**Solution**: Manually navigate to `http://localhost:8501` or check the terminal output for the correct port.

## 👩🏼‍💻 Developer

**Dhruvi Patel**  
📧 Email: pateldhruvi2207@gmail.com