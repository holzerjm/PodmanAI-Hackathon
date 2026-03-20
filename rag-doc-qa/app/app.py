"""
📚 RAG Document Q&A — Local AI, Zero Cloud
Pods, Prompts & Prototypes Hackathon | Powered by Ollama + ChromaDB

Upload your documents and chat with them using a fully local AI pipeline.
"""

import os
import tempfile
import hashlib
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

# ── Config ────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "granite3.1-dense:8b")
CHROMA_DIR = "/data/chroma_db"
UPLOAD_DIR = "/data/uploads"

os.makedirs(CHROMA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Page Setup ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Doc Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }
    .main-header {
        text-align: center;
        padding: 1.5rem 0 1rem;
    }
    .main-header h1 {
        background: linear-gradient(90deg, #00d2ff, #7b2ff7, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .main-header p {
        color: #8892b0;
        font-size: 1.1rem;
    }
    .status-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 2px 4px;
    }
    .pill-green { background: #064e3b; color: #6ee7b7; }
    .pill-blue  { background: #1e3a5f; color: #7dd3fc; }
    .pill-amber { background: #78350f; color: #fcd34d; }

    .doc-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 8px;
        transition: all 0.2s;
    }
    .doc-card:hover { background: rgba(255,255,255,0.07); }
    .doc-card .title { color: #e2e8f0; font-weight: 600; }
    .doc-card .meta { color: #64748b; font-size: 0.82rem; }

    /* Chat bubbles */
    .stChatMessage [data-testid="stMarkdownContainer"] {
        font-size: 0.95rem;
    }

    section[data-testid="stSidebar"] {
        background: rgba(15,12,41,0.85);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_count" not in st.session_state:
    st.session_state.doc_count = 0
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []


# ── Helpers ───────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


def get_llm(model: str, temperature: float):
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=model,
        temperature=temperature,
    )


def file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def load_document(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return PyPDFLoader(path).load()
    elif ext in (".txt", ".md", ".py", ".js", ".ts", ".java", ".go", ".rs"):
        return TextLoader(path).load()
    else:
        return TextLoader(path).load()


def process_documents(files):
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    for f in files:
        fhash = file_hash(f.getvalue())
        if fhash in [p["hash"] for p in st.session_state.processed_files]:
            continue

        tmp_path = os.path.join(UPLOAD_DIR, f.name)
        with open(tmp_path, "wb") as out:
            out.write(f.getvalue())

        docs = load_document(tmp_path)
        chunks = splitter.split_documents(docs)
        all_docs.extend(chunks)

        st.session_state.processed_files.append({
            "name": f.name,
            "hash": fhash,
            "chunks": len(chunks),
            "size": len(f.getvalue()),
        })

    if all_docs:
        embeddings = get_embeddings()
        if st.session_state.vectorstore is None:
            st.session_state.vectorstore = Chroma.from_documents(
                all_docs, embeddings, persist_directory=CHROMA_DIR
            )
        else:
            st.session_state.vectorstore.add_documents(all_docs)

        st.session_state.doc_count = len(st.session_state.processed_files)
        st.session_state.chunk_count += len(all_docs)

    return len(all_docs)


# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    model = st.selectbox(
        "Ollama Model",
        ["granite3.1-dense:8b", "qwen2.5:7b", "mistral:7b", "llama3.1:8b"],
        index=0,
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    top_k = st.slider("Retrieval top-k", 2, 10, 4)

    st.markdown("---")
    st.markdown("## 📄 Upload Documents")
    uploaded = st.file_uploader(
        "Drop PDFs, text, or code files",
        type=["pdf", "txt", "md", "py", "js", "ts", "java", "go", "rs"],
        accept_multiple_files=True,
    )

    if uploaded:
        with st.spinner("🔍 Chunking & embedding..."):
            new_chunks = process_documents(uploaded)
        if new_chunks:
            st.success(f"✅ Added {new_chunks} new chunks!")

    if st.session_state.processed_files:
        st.markdown("---")
        st.markdown("## 📂 Loaded Documents")
        for doc in st.session_state.processed_files:
            size_kb = doc["size"] / 1024
            st.markdown(
                f"""<div class="doc-card">
                    <div class="title">📄 {doc['name']}</div>
                    <div class="meta">{doc['chunks']} chunks · {size_kb:.1f} KB</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        '<span class="status-pill pill-green">🟢 Local AI</span>'
        '<span class="status-pill pill-blue">🔵 Ollama</span>'
        '<span class="status-pill pill-amber">🟡 ChromaDB</span>',
        unsafe_allow_html=True,
    )

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()


# ── Main Area ─────────────────────────────────────────────────────────
st.markdown(
    """<div class="main-header">
        <h1>📚 RAG Document Q&A</h1>
        <p>Upload documents → Ask questions → Get answers grounded in your data<br>
        <em>100% local AI · Ollama + ChromaDB · Zero cloud dependency</em></p>
    </div>""",
    unsafe_allow_html=True,
)

# Stats row
c1, c2, c3, c4 = st.columns(4)
c1.metric("📄 Documents", st.session_state.doc_count)
c2.metric("🧩 Chunks", st.session_state.chunk_count)
c3.metric("🤖 Model", model.split(":")[0])
c4.metric("💬 Messages", len(st.session_state.messages))

st.markdown("---")

# No-docs welcome
if st.session_state.vectorstore is None:
    st.markdown("""
    ### 👋 Welcome! Get started in 3 steps:

    1. **Upload documents** using the sidebar (PDFs, text, code files)
    2. **Ask a question** about your documents in the chat below
    3. **Get grounded answers** with source references

    > 💡 *Tip: Try uploading a PDF manual or codebase and ask questions about it!*
    """)

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about your documents…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    if st.session_state.vectorstore is None:
        assistant_msg = "⚠️ Please upload at least one document first so I have something to search through!"
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(assistant_msg)
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
    else:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔎 Searching docs & generating answer..."):
                llm = get_llm(model, temperature)
                memory = ConversationBufferWindowMemory(
                    k=5,
                    memory_key="chat_history",
                    return_messages=True,
                    output_key="answer",
                )
                for i in range(0, len(st.session_state.chat_history), 2):
                    if i + 1 < len(st.session_state.chat_history):
                        memory.save_context(
                            {"input": st.session_state.chat_history[i]},
                            {"output": st.session_state.chat_history[i + 1]},
                        )

                chain = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    retriever=st.session_state.vectorstore.as_retriever(
                        search_kwargs={"k": top_k}
                    ),
                    memory=memory,
                    return_source_documents=True,
                )

                result = chain({"question": prompt})
                answer = result["answer"]
                sources = result.get("source_documents", [])

                st.markdown(answer)

                if sources:
                    with st.expander(f"📑 Sources ({len(sources)} chunks)"):
                        for i, src in enumerate(sources):
                            source_name = src.metadata.get("source", "Unknown")
                            page = src.metadata.get("page", "")
                            page_str = f" · Page {page}" if page != "" else ""
                            st.markdown(f"**[{i+1}]** `{os.path.basename(source_name)}`{page_str}")
                            st.caption(src.page_content[:300] + "…" if len(src.page_content) > 300 else src.page_content)

                st.session_state.chat_history.extend([prompt, answer])
                st.session_state.messages.append({"role": "assistant", "content": answer})
