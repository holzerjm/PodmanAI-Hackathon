# 🚀 PodmanAI-Hackathon

**Pods, Prompts & Prototypes** — Two containerized AI applications built for the [Pods, Prompts & Prototypes Hackathon](https://the-open-accelerator.com/hackathon/upcoming/PodmanAI/) at The Open Accelerator, Boston.

Both apps run entirely in Podman containers and showcase different approaches to AI integration: one fully local with Ollama, the other cloud-powered via Anthropic Claude.

---

## 📦 Projects

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

---

### 🔍 [AI Code Reviewer](./ai-code-reviewer/)

Paste code and get **expert-level reviews** with a quality score, categorized findings, an improved version of your code, and plain-English explanations.

Supports Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, and Ruby. Choose focus areas like security, performance, readability, and best practices.

| Component | Technology |
|-----------|-----------|
| AI Model | [Anthropic Claude](https://www.anthropic.com/) (Sonnet) |
| Syntax Highlighting | [Pygments](https://pygments.org/) |
| Frontend | [Streamlit](https://streamlit.io/) |

```bash
cd ai-code-reviewer
ANTHROPIC_API_KEY=sk-ant-... podman compose up -d
# → http://localhost:8502
```

---

## 🛠️ Shared Stack

Both applications are built on a common foundation:

- **Containers** — [Podman](https://podman.io/) (rootless, daemonless, OCI-compliant)
- **Compose** — `podman compose` with standard `compose.yml`
- **Frontend** — [Streamlit](https://streamlit.io/) with custom dark-themed UIs
- **Language** — Python 3.11

## 📁 Repository Structure

```
PodmanAI-Hackathon/
│
├── rag-doc-qa/                  # App 1 — Local RAG pipeline
│   ├── Containerfile
│   ├── compose.yml              # Ollama + Streamlit app
│   ├── README.md
│   └── app/
│       ├── app.py
│       └── requirements.txt
│
├── ai-code-reviewer/            # App 2 — Claude-powered reviewer
│   ├── Containerfile
│   ├── compose.yml
│   ├── README.md
│   └── app/
│       ├── app.py
│       └── requirements.txt
│
└── README.md                    # ← You are here
```

## 🏆 Hackathon Alignment

These projects target the **Intermediate** and **Intermediate/Advanced** challenge tiers of the Pods, Prompts & Prototypes hackathon, specifically:

- **RAG on Your Data** — local document retrieval and generation
- **The Local AI API** — containerized AI microservice

Both are designed around the hackathon judging rubric:

| Criterion | How We Address It |
|-----------|-------------------|
| **User Flow & UI/UX** | Dark-themed Streamlit UIs with intuitive chat and paste-to-review flows |
| **Engineering Quality** | Clean separation of concerns, structured prompts, proper RAG pipeline |
| **Grounding & Verifiability** | Source citations (RAG), line-specific findings with diffs (Reviewer) |
| **Creativity & Innovation** | Local-first zero-cloud RAG; structured code review with scoring |
| **Real-World Fit** | Enterprise doc Q&A without data leaving the network; democratized code review |

## 📋 Prerequisites

- [Podman Desktop](https://podman-desktop.io/) (or Podman CLI)
- ~8 GB free disk space (for Ollama models)
- An [Anthropic API key](https://console.anthropic.com/) (for the Code Reviewer only)

## 📄 License

MIT
