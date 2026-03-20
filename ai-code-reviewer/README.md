# 🔍 AI Code Reviewer — Powered by Anthropic Claude

> **Pods, Prompts & Prototypes Hackathon** | Intermediate/Advanced Challenge: *AI-Powered Code Reviewer*

Paste your code and get expert-level reviews with quality scores, categorized findings, improved code, and explanations — all containerized and ready to deploy.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Model | Anthropic Claude (Sonnet) |
| Frontend | Streamlit |
| Syntax | Pygments |
| Containers | Podman |

## Quick Start

```bash
cd ai-code-reviewer

# Set your API key and run
ANTHROPIC_API_KEY=sk-ant-... podman compose up -d

# Open http://localhost:8502
```

Or enter your API key in the sidebar after launch.

## Features

- **Quality Score** — 0-100 score with visual ring indicator
- **Categorized Findings** — Critical 🔴, Warning 🟡, Info 🔵, Good 🟢
- **Side-by-Side Diff** — Original vs. improved code comparison
- **Multiple Languages** — Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, Ruby
- **Focus Areas** — Security, Performance, Readability, Best Practices, Error Handling, Testing, Type Safety
- **Built-in Examples** — SQL injection, performance, and error handling samples to try

## How It Works

1. **Paste or Upload** your code
2. **Select** language and focus areas
3. **Click Review** — Claude analyzes your code
4. **Get Results** — Score, findings with line references, improved code, and explanation

## Project Structure

```
ai-code-reviewer/
├── Containerfile          # App container image
├── compose.yml            # Container orchestration
├── README.md
└── app/
    ├── app.py             # Streamlit application
    └── requirements.txt   # Python dependencies
```

## Judging Criteria Alignment

- **User Flow & UI/UX**: GitHub-inspired dark theme, intuitive paste-and-review flow
- **Engineering Quality**: Structured prompt engineering, robust response parsing
- **Grounding & Verifiability**: Line-specific findings, side-by-side code comparison
- **Creativity**: Professional code review experience in a single container
- **Real-World Fit**: Every developer needs code review — this democratizes expert feedback
