# ⚡ Local AI Productivity Agent

An autonomous personal productivity and workflow assistant powered by a custom **Python ReAct (Reason + Act) loop**, local function-calling tools, and an open-source LLM (**Ollama / Qwen2.5**). 

Built with **zero paid API dependencies** to demonstrate local agent orchestration, state management, and real-time tool tracing.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)

---

## 🏗️ System Architecture & Workflow

The agent uses a two-pass tool-dispatching loop:
1. **Reasoning Pass:** The user prompt is sent to `Qwen2.5` via Ollama with strict JSON tool schemas.
2. **Action / Tool Execution:** If a tool call is requested, the Python backend executes the local function (e.g., SQLite query or file reader).
3. **Synthesis Pass:** The tool output is fed back into the message history, allowing the model to synthesize a final conversational response.

```text
[ User Prompt ] 
       │
       ▼
[ Streamlit UI ] ──(State & Trace History)──> [ Agent ReAct Loop ]
                                                    │
                                        ┌───────────┴───────────┐
                                        ▼                       ▼
                               [ Ollama / Qwen2.5 ]    [ Python Tool Router ]
                                        │                       │
                                        └───────(JSON)──────────┘
                                                    │
                                                    ▼
                                           [ SQLite / Local Files ]
✨ Core Features
Custom ReAct Agent Loop: Handles multi-step intent parsing, tool selection, and feedback integration without heavy black-box frameworks (like LangChain).

Function Calling & Tool Dispatching: Dynamically parses natural language into precise JSON arguments to execute tasks.

Task Manager: Add and list productivity tasks.

Note Taker: Save quick logs or meeting summaries.

Local File Reader: Inspect project files directly from conversational prompts.

Stateful Memory & Storage: Persists chat conversations, tasks, and notes securely using local SQLite.

Live Agent Trace Visualizer: Expandable UI component that reveals the agent's internal reasoning steps and raw JSON tool payloads in real-time.

100% Local & Free: Runs completely on your local machine using Ollama, requiring zero cloud API keys or subscription costs.

🛠️ Tech Stack
Language: Python

LLM Runtime: Ollama (qwen2.5 with native tool-calling)

Database: SQLite

Frontend / UI: Streamlit

SDK: OpenAI Python SDK (pointed to local Ollama endpoint)

🚀 Getting Started Locally
1. Prerequisites
Ensure you have Python installed along with Ollama running on your system. Pull the Qwen model:

Bash
ollama pull qwen2.5
2. Clone and Setup Repository
Bash
git clone [https://github.com/YOUR_USERNAME/ai-productivity-agent.git](https://github.com/YOUR_USERNAME/ai-productivity-agent.git)
cd ai-productivity-agent
3. Create a Virtual Environment & Install Dependencies
Bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
4. Initialize the Database
Bash
python database.py
5. Run the Streamlit Application
Bash
streamlit run app.py
Open your browser at http://localhost:8501 and start chatting with your agent!