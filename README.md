# 🚀 AI Startup Incubator — Multi-Agent Orchestration

A multi-agent AI system built with **LangGraph**, **LangChain**, and **Streamlit** that evaluates startup ideas using a team of specialized AI agents orchestrated by a CEO supervisor.

## Architecture

```
User Input (Startup Idea)
        │
        ▼
   ┌─────────┐
   │   CEO   │ ◄── Supervisor / Orchestrator
   └────┬────┘
        │ Decides who works next
        ├──────────────────┐
        ▼                  ▼
┌──────────────┐   ┌──────────────┐
│  Researcher  │   │   Designer   │
│ (Market      │   │ (Product     │
│  Analysis)   │   │  Specs)      │
└──────┬───────┘   └──────┬───────┘
       │                  │
       └────────┬─────────┘
                ▼
        ┌──────────────┐
        │ CEO Reviews  │
        │ & Finalizes  │
        └──────────────┘
                │
                ▼
        Final Prospectus
```

### Agents

| Agent | Role |
|-------|------|
| **CEO (Supervisor)** | Orchestrates the workflow — decides which agent works next based on what's been completed |
| **Market Researcher** | Provides market analysis including target audience and competition |
| **Product Designer** | Creates a feature list and product specifications |

## Tech Stack

- **LangGraph** — Multi-agent state graph with conditional routing
- **LangChain + OpenAI GPT-4o** — LLM backbone for each agent
- **MongoDB** — Checkpoint storage for persistent agent state
- **Streamlit** — Interactive web UI with real-time progress

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/philicamit/Multi_Agent_Orchestration.git
cd Multi_Agent_Orchestration
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY="your-openai-api-key"
MONGODB_URI="mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
```

### 5. Run the Streamlit app

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## How It Works

1. You enter a startup idea in the text area
2. The **CEO supervisor** reviews the current state and delegates tasks
3. The **Researcher** produces a market analysis report
4. The **Designer** drafts product feature specifications
5. The CEO reviews the completed work and presents the final prospectus
6. All state is checkpointed to **MongoDB** for persistence

## Project Structure

```
├── app.py              # Streamlit web application
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not tracked)
└── .gitignore
```

## License

MIT
