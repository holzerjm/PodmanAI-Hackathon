# 📚 RAG Document Q&A — Local AI, Zero Cloud

> **Pods, Prompts & Prototypes Hackathon** | Intermediate Challenge: *RAG on Your Data*

Upload your documents and chat with them using a fully local AI pipeline. All inference runs on your machine — no cloud APIs, no data leaving your network.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (Granite 3.1 8B) |
| Embeddings | all-MiniLM-L6-v2 (local) |
| Vector Store | ChromaDB |
| Framework | LangChain |
| Frontend | Streamlit |
| Containers | Podman |

## Quick Start

```bash
# Clone and run
cd rag-doc-qa
podman compose up -d

# Wait for model download (~5 min first time), then open:
# http://localhost:8501
```

## How It Works

1. **Upload** — Drop PDFs, text files, or code into the sidebar
2. **Chunk & Embed** — Documents are split into overlapping chunks and embedded locally using MiniLM
3. **Ask** — Type a question in the chat
4. **Retrieve & Generate** — Relevant chunks are retrieved from ChromaDB and sent to the local LLM for grounded answer generation
5. **Sources** — Every answer includes expandable source references

## Configuration

Change the model via environment variable or the sidebar dropdown:

```bash
OLLAMA_MODEL=mistral:7b podman compose up -d
```

Supported models: `granite3.1-dense:8b`, `qwen2.5:7b`, `mistral:7b`, `llama3.1:8b`

## Project Structure

```
rag-doc-qa/
├── Containerfile          # App container image
├── compose.yml            # Full stack: Ollama + App
├── README.md
├── app/
│   ├── app.py             # Streamlit application
│   └── requirements.txt   # Python dependencies
└── docs/                  # Sample documents (optional)
```

## Judging Criteria Alignment

- **User Flow & UI/UX**: Clean chat interface with document management sidebar
- **Engineering Quality**: Proper RAG pipeline with LangChain, persistent vector store
- **Grounding & Verifiability**: Source citations with every answer
- **Creativity**: Local-first approach with zero cloud dependency
- **Real-World Fit**: Enterprise document Q&A without data leaving the network
