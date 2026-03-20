# 📖 AI Story Forge — Choose-Your-Own-Adventure with Local AI

> **Pods, Prompts & Prototypes Hackathon** | Beginner Challenge: *The Local AI API*

Pick a genre, start an adventure, and make choices that shape the story — all powered by a local AI running on your machine. No cloud APIs, no data leaving your network.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (Granite 3.1 8B) |
| Frontend | Streamlit |
| Containers | Podman |

## Quick Start

```bash
# Clone and run
cd ai-story-forge
podman compose up -d

# Wait for model download (~5 min first time), then open:
# http://localhost:8503
```

## How It Works

1. **Pick a Genre** — Choose from Fantasy, Sci-Fi, Mystery, Horror, and more
2. **Begin Your Adventure** — The AI sets the scene with a compelling opening
3. **Read the Story** — Each turn delivers a vivid narrative paragraph
4. **Make Choices** — Pick from 3 options to steer the story your way
5. **Reach the Ending** — After several turns, the AI writes a dramatic conclusion

## Configuration

Change the model via environment variable or the sidebar dropdown:

```bash
OLLAMA_MODEL=mistral:7b podman compose up -d
```

Supported models: `granite3.1-dense:8b`, `qwen2.5:7b`, `mistral:7b`, `llama3.1:8b`

## Project Structure

```
ai-story-forge/
├── Containerfile          # App container image
├── compose.yml            # Full stack: Ollama + App
├── README.md
└── app/
    ├── app.py             # Streamlit application
    └── requirements.txt   # Python dependencies
```

## Judging Criteria Alignment

- **User Flow & UI/UX**: Immersive dark-themed UI with story cards and styled choice buttons
- **Engineering Quality**: Clean prompt engineering with structured output parsing
- **Grounding & Verifiability**: Each story turn builds on player choices with consistent narrative
- **Creativity**: Interactive fiction powered by local AI — replayable with different outcomes
- **Real-World Fit**: Demonstrates conversational AI with stateful multi-turn interaction
