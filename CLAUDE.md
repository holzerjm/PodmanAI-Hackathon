# CLAUDE.md

## Project Overview

Three containerized AI applications built for the "Pods, Prompts & Prototypes Hackathon" (The Open Accelerator, Boston). Each app demonstrates a different AI integration approach, all running in Podman containers with Streamlit UIs.

| App | Difficulty | AI Backend | Port |
|-----|-----------|------------|------|
| **RAG Document Q&A** | Intermediate | Ollama + ChromaDB | 8501 |
| **AI Code Reviewer** | Intermediate/Advanced | Anthropic Claude API | 8502 |
| **AI Story Forge** | Beginner | Ollama | 8503 |

## Repository Structure

```
PodmanAI-Hackathon/
├── CLAUDE.md
├── LICENSE                    # MIT
├── README.md
├── rag-doc-qa/               # RAG pipeline app
│   ├── Containerfile
│   ├── compose.yml
│   └── app/
│       ├── app.py            # ~334 lines, LangChain + ChromaDB
│       └── requirements.txt
├── ai-code-reviewer/         # Code review app
│   ├── Containerfile
│   ├── compose.yml
│   └── app/
│       ├── app.py            # ~469 lines, Anthropic API
│       └── requirements.txt
└── ai-story-forge/           # Interactive story app
    ├── Containerfile
    ├── compose.yml
    └── app/
        ├── app.py            # ~440 lines, Ollama
        └── requirements.txt
```

## Build & Run

All apps use **Podman** (rootless, daemonless, OCI-compliant). No Docker required.

```bash
# Run any app
cd <app-directory>
podman compose up --build

# Run without containers (local dev)
cd <app-directory>
pip install -r app/requirements.txt
streamlit run app/app.py
```

### Environment Variables

| Variable | Used By | Default |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | ai-code-reviewer | (required, entered in UI) |
| `ANTHROPIC_MODEL` | ai-code-reviewer | `claude-sonnet-4-20250514` |
| `OLLAMA_BASE_URL` | rag-doc-qa, ai-story-forge | `http://ollama:11434` |
| `OLLAMA_MODEL` | rag-doc-qa, ai-story-forge | `granite3.1-dense:8b` |

## Tech Stack

- **Python 3.11** (slim base image)
- **Streamlit 1.41.0** — all UI
- **LangChain 0.3.14** — RAG orchestration (rag-doc-qa only)
- **ChromaDB 0.6.3** — vector store (rag-doc-qa only)
- **Anthropic 0.42.0** — Claude API client (ai-code-reviewer only)
- **Ollama 0.4.7** — local LLM client (ai-story-forge only)
- **sentence-transformers** — `all-MiniLM-L6-v2` embeddings (rag-doc-qa only)

## Code Conventions

### Streamlit Patterns

- **Page config**: `st.set_page_config(page_title=..., page_icon=..., layout="wide", initial_sidebar_state="expanded")`
- **Session state**: All mutable state in `st.session_state` (chat history, documents, game state)
- **Caching**: `@st.cache_resource` for expensive initialization (model loading, client creation)
- **Sidebar layout**: Settings at top, inputs in middle, status/help at bottom
- **Custom CSS**: Dark-themed gradients injected via `st.markdown(unsafe_allow_html=True)`
- **Fonts**: Google Fonts — Inter (UI), JetBrains Mono (code), Crimson Text (story)

### Architecture Per App

- **rag-doc-qa**: Upload → Hash → Chunk → Embed → ChromaDB → LangChain ConversationalRetrievalChain → Answer with source citations
- **ai-code-reviewer**: Paste/upload code → Structured prompt → Claude API → Regex parse response (score, findings, improved code) → Render cards
- **ai-story-forge**: Genre config → Ollama prompt → Regex parse (STORY:, CHOICE_1:, etc.) → Turn-based state machine (max 10 turns context)

### Style

- PEP 8 informal (no linter configured)
- No type hints
- Single `app.py` per application — all logic in one file
- Environment-driven configuration via `os.environ.get()`

## Testing

No automated test suite exists. Testing is manual:

```bash
# Build and run
podman compose up --build

# Verify health
curl http://localhost:<PORT>/_stcore/health
```

Each Containerfile includes a `HEALTHCHECK` directive for container-level health monitoring.

## CI/CD

No CI/CD pipelines configured. No `.github/workflows/` directory.

## Container Build Details

All Containerfiles follow the same pattern:
1. `FROM python:3.11-slim`
2. Install system deps (`build-essential`, `curl`)
3. `pip install` from `requirements.txt`
4. Copy app source
5. Expose port, add healthcheck
6. `ENTRYPOINT ["streamlit", "run", "app.py", ...]`

Compose files use multi-service setups for apps needing Ollama (rag-doc-qa, ai-story-forge): an `ollama` service, an `ollama-pull` init service to fetch the model, and the app service with `depends_on` health checks.

## Important Notes

- **No secrets in code**: `ANTHROPIC_API_KEY` is entered per-session in the UI sidebar, never persisted
- **Data is ephemeral**: Session state is in-memory only (except ChromaDB volumes in rag-doc-qa)
- **GPU optional**: Compose files have commented-out GPU passthrough (`nvidia.com/gpu=all`)
- **License**: MIT (2026, Jan Mark Holzer)
