# 🚀 PodmanAI-Hackathon

**Pods, Prompts & Prototypes** — Three containerized AI applications built for the [Pods, Prompts & Prototypes Hackathon](https://the-open-accelerator.com/hackathon/upcoming/PodmanAI/) at The Open Accelerator, Boston.

All apps run entirely in Podman containers and showcase different approaches to AI integration: two fully local with Ollama, one cloud-powered via Anthropic Claude.

## 📋 Quick Index

| Level | App | Description | Port |
|-------|-----|-------------|------|
| **Beginner** | [📖 AI Story Forge](#ai-story-forge) | Choose-your-own-adventure with local AI | [8503](http://localhost:8503) |
| **Intermediate** | [📚 RAG Document Q&A](#rag-document-qa) | Upload docs & chat with them — fully local | [8501](http://localhost:8501) |
| **Intermediate/Advanced** | [🔍 AI Code Reviewer](#ai-code-reviewer) | Expert code reviews powered by Claude | [8502](http://localhost:8502) |

---

## 📦 Projects

<a id="rag-document-qa"></a>

### 📚 [RAG Document Q&A](./rag-doc-qa/)

Upload documents and chat with them using a fully **local AI pipeline** — no data ever leaves your machine.

Drop in PDFs, text files, or source code, and the app chunks, embeds, and indexes them into a local vector store. Ask questions in a chat interface and get grounded answers with source citations.

| Component | Technology |
|-----------|-----------|
| LLM | [Ollama](https://ollama.com/) — Granite 3.1 8B (local) |
| Embeddings | all-MiniLM-L6-v2 (local) |
| Vector Store | [ChromaDB](https://www.trychroma.com/) |
| Orchestration | [LangChain](https://www.langchain.com/) |
| Frontend | [Streamlit](https://streamlit.io/) |

```bash
cd rag-doc-qa
podman compose up -d
# → http://localhost:8501
```

> **Note:** The first run downloads the Granite 3.1 8B model (~4.9 GB). This can take 5–10 minutes depending on your connection.

---

<a id="ai-code-reviewer"></a>

### 🔍 [AI Code Reviewer](./ai-code-reviewer/)

Paste code and get **expert-level reviews** with a quality score, categorized findings, an improved version of your code, and plain-English explanations.

Supports Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, and Ruby. Choose focus areas like security, performance, readability, and best practices.

| Component | Technology |
|-----------|-----------|
| AI Model | [Anthropic Claude Sonnet 4](https://www.anthropic.com/) |
| Syntax Highlighting | [Pygments](https://pygments.org/) |
| Frontend | [Streamlit](https://streamlit.io/) |

```bash
cd ai-code-reviewer
ANTHROPIC_API_KEY=sk-ant-... podman compose up -d
# → http://localhost:8502
```

> **Tip:** You can also enter your API key via the sidebar UI after launch. The key is session-only and never stored to disk.

---

<a id="ai-story-forge"></a>

### 📖 [AI Story Forge](./ai-story-forge/)

Choose your own adventure with **local AI** — pick a genre, make choices, and watch an interactive story unfold in real time. Great for beginners!

| Component | Technology |
|-----------|-----------|
| LLM | [Ollama](https://ollama.com/) — Granite 3.1 8B (local) |
| Frontend | [Streamlit](https://streamlit.io/) |

```bash
cd ai-story-forge
podman compose up -d
# → http://localhost:8503
```

> **Note:** Shares the same Ollama model as the RAG app. If you've already run that app, startup is instant.

---

## 🛠️ Shared Stack

All three applications are built on a common foundation:

- **Containers** — [Podman](https://podman.io/) (rootless, daemonless, OCI-compliant)
- **Compose** — `podman compose` with standard `compose.yml`
- **Frontend** — [Streamlit](https://streamlit.io/) with custom dark-themed UIs
- **Language** — Python 3.11

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd PodmanAI-Hackathon
```

### 2. Start an app

**RAG Document Q&A** (fully local — no API key needed):

```bash
cd rag-doc-qa
podman compose up -d
# Open http://localhost:8501
```

**AI Code Reviewer** (requires Anthropic API key):

```bash
cd ai-code-reviewer
ANTHROPIC_API_KEY=sk-ant-... podman compose up -d
# Open http://localhost:8502
```

**AI Story Forge** (fully local — no API key needed):

```bash
cd ai-story-forge
podman compose up -d
# Open http://localhost:8503
```

### 3. Stop an app

```bash
podman compose down
```

To also remove volumes (model cache, vector store data):

```bash
podman compose down -v
```

## ⚙️ Environment Variables

| Variable | App | Default | Description |
|----------|-----|---------|-------------|
| `ANTHROPIC_API_KEY` | Code Reviewer | *(none, required)* | Your Anthropic API key |
| `ANTHROPIC_MODEL` | Code Reviewer | `claude-sonnet-4-20250514` | Claude model to use for reviews |
| `OLLAMA_MODEL` | RAG Doc Q&A, Story Forge | `granite3.1-dense:8b` | Ollama model for generation |
| `OLLAMA_BASE_URL` | RAG Doc Q&A, Story Forge | `http://ollama:11434` | Ollama server URL (set automatically by compose) |

## 📁 Repository Structure

```
PodmanAI-Hackathon/
│
├── rag-doc-qa/                  # App 1 — Local RAG pipeline
│   ├── Containerfile
│   ├── compose.yml              # Ollama + Streamlit app
│   ├── .gitignore
│   ├── README.md
│   └── app/
│       ├── app.py
│       └── requirements.txt
│
├── ai-code-reviewer/            # App 2 — Claude-powered reviewer
│   ├── Containerfile
│   ├── compose.yml
│   ├── .gitignore
│   ├── README.md
│   └── app/
│       ├── app.py
│       └── requirements.txt
│
├── ai-story-forge/              # App 3 — Choose-your-own-adventure (Beginner)
│   ├── Containerfile
│   ├── compose.yml
│   ├── .gitignore
│   ├── README.md
│   └── app/
│       ├── app.py
│       └── requirements.txt
│
├── LICENSE
└── README.md                    # ← You are here
```

## 🏆 Hackathon Alignment

These projects span **Beginner**, **Intermediate**, and **Intermediate/Advanced** challenge tiers of the Pods, Prompts & Prototypes hackathon:

- **The Local AI API** — containerized AI microservice (Story Forge — Beginner)
- **RAG on Your Data** — local document retrieval and generation (RAG Doc Q&A — Intermediate)
- **AI-Powered Code Reviewer** — cloud-powered code analysis (Code Reviewer — Intermediate/Advanced)

All three are designed around the hackathon judging rubric:

| Criterion | How We Address It |
|-----------|-------------------|
| **User Flow & UI/UX** | Dark-themed Streamlit UIs with intuitive chat, paste-to-review, and interactive story flows |
| **Engineering Quality** | Clean separation of concerns, structured prompts, proper RAG pipeline |
| **Grounding & Verifiability** | Source citations (RAG), line-specific findings with diffs (Reviewer), choice-driven narrative (Story Forge) |
| **Creativity & Innovation** | Local-first zero-cloud RAG; structured code review with scoring; interactive fiction with AI |
| **Real-World Fit** | Enterprise doc Q&A without data leaving the network; democratized code review; engaging AI demo for newcomers |

## 📋 Prerequisites

- [Podman Desktop](https://podman-desktop.io/) (or Podman CLI)
- ~10 GB free disk space (Granite 3.1 8B model is ~4.9 GB, plus container images)
- An [Anthropic API key](https://console.anthropic.com/) (for the Code Reviewer only)

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8501, 8502, or 8503 already in use | Stop the conflicting process, or edit `ports` in the relevant `compose.yml` |
| Ollama model download is slow | The Granite 3.1 8B model is ~4.9 GB. On slower connections, the initial pull may take 10+ minutes. Check progress with `podman logs rag-ollama-pull -f` |
| RAG app says "Ollama not reachable" | Ensure the Ollama container is healthy: `podman ps` should show `rag-ollama` as running. If not, check logs: `podman logs rag-ollama` |
| Code Reviewer returns auth error | Verify your `ANTHROPIC_API_KEY` is valid. You can also enter it via the sidebar UI |
| Switching Ollama models | Set `OLLAMA_MODEL=mistral:7b` (or another supported model) before `podman compose up`. The model will be pulled automatically on first run |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b my-feature`
3. Make your changes
4. Test locally with `podman compose up -d`
5. Submit a pull request

### Local Development (without containers)

```bash
# RAG Doc Q&A
cd rag-doc-qa/app
pip install -r requirements.txt
# Requires a running Ollama instance at http://localhost:11434
OLLAMA_BASE_URL=http://localhost:11434 streamlit run app.py

# AI Code Reviewer
cd ai-code-reviewer/app
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-ant-... streamlit run app.py --server.port 8502

# AI Story Forge
cd ai-story-forge/app
pip install -r requirements.txt
# Requires a running Ollama instance at http://localhost:11434
OLLAMA_BASE_URL=http://localhost:11434 streamlit run app.py --server.port 8503
```

## 📄 License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
