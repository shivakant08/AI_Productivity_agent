import json
import os
import sqlite3
import chromadb
import httpx2
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Setup HTTP client with SSL/proxy bypass for local Ollama
http_client = httpx2.Client(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    trust_env=False,
)

CLIENT = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    api_key="ollama",
    http_client=http_client,
)
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")
DB_PATH = "data/productivity.db"

# Initialize ChromaDB persistent vector store locally
chroma_client = chromadb.PersistentClient(path="data/chroma_db")
notes_collection = chroma_client.get_or_create_collection(name="user_notes")


# --- Tool Implementations ---
def add_task(title: str, due_date: str = "Today") -> str:
  """Adds a new task to the local SQLite productivity database."""
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO tasks (title, due_date, status) VALUES (?, ?, ?)",
      (title, due_date, "PENDING"),
  )
  conn.commit()
  conn.close()
  return json.dumps(
      {"status": "success", "message": f"Task '{title}' added due {due_date}."}
  )


def list_tasks() -> str:
  """Retrieves all pending tasks from the database."""
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("SELECT id, title, due_date, status FROM tasks")
  rows = cursor.fetchall()
  conn.close()
  tasks = [
      {
          "id": r[0],
          "title": r[1],
          "due_date": r[2],
          "status": r[3],
      }
      for r in rows
  ]
  return json.dumps(tasks)


def add_note(content: str) -> str:
  """Saves a quick note to SQLite and indexes it in ChromaDB for semantic search."""
  # 1. Save to SQLite
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
  note_id = cursor.lastrowid
  conn.commit()
  conn.close()

  # 2. Generate embedding using Ollama and store in ChromaDB
  try:
    embedding_response = CLIENT.embeddings.create(
        model="nomic-embed-text", input=content
    )
    vector = embedding_response.data[0].embedding
    notes_collection.add(
        ids=[str(note_id)], embeddings=[vector], documents=[content]
    )
  except Exception as e:
    print(f"Embedding warning: {e}")

  return json.dumps(
      {
          "status": "success",
          "message": "Note saved and indexed semantically.",
      }
  )


def search_notes_semantically(query: str) -> str:
  """Searches saved notes by meaning using vector similarity."""
  try:
    embedding_response = CLIENT.embeddings.create(
        model="nomic-embed-text", input=query
    )
    query_vector = embedding_response.data[0].embedding

    results = notes_collection.query(
        query_embeddings=[query_vector], n_results=3
    )
    documents = results.get("documents", [[]])[0]

    if not documents:
      return json.dumps(
          {"status": "success", "matches": [], "message": "No relevant notes found."}
      )

    return json.dumps({"status": "success", "matches": documents})
  except Exception as e:
    return json.dumps({"status": "error", "message": str(e)})


def read_local_file(filename: str) -> str:
  """Reads the content of a local text file in the project directory."""
  try:
    if not os.path.exists(filename):
      return json.dumps(
          {"status": "error", "message": f"File '{filename}' not found."}
      )
    with open(filename, "r", encoding="utf-8") as f:
      content = f.read()
    return json.dumps({"status": "success", "content": content})
  except Exception as e:
    return json.dumps({"status": "error", "message": str(e)})


AVAILABLE_TOOLS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "add_note": add_note,
    "search_notes_semantically": search_notes_semantically,
    "read_local_file": read_local_file,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task or action item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task description."},
                    "due_date": {"type": "string", "description": "Due timeframe."},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Retrieve all tasks.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "Save a meeting note or thought.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Note content."}
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes_semantically",
            "description": (
                "Search through saved notes using semantic similarity or"
                " concepts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search concept or query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_local_file",
            "description": "Read local text files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File name."}
                },
                "required": ["filename"],
            },
        },
    },
]


def run_agent_turn(user_prompt: str, chat_history: list = None):
  """Executes reasoning turn, handles tools, and yields streaming chunks for the UI."""
  if chat_history is None:
    chat_history = [
        {
            "role": "system",
            "content": (
                "You are an expert productivity agent with RAG search"
                " capabilities for notes."
            ),
        }
    ]

  chat_history.append({"role": "user", "content": user_prompt})
  trace_logs = []

  # First pass: check for tool calls
  response = CLIENT.completions.create
  response = CLIENT.chat.completions.create(
      model=MODEL_NAME, messages=chat_history, tools=TOOLS_SCHEMA
  )

  response_message = response.choices[0].message
  chat_history.append(response_message)

  if response_message.tool_calls:
    for tool_call in response_message.tool_calls:
      fn_name = tool_call.function.name
      fn_args = json.loads(tool_call.function.arguments)

      trace_logs.append({
          "type": "tool_call",
          "tool": fn_name,
          "arguments": fn_args,
      })

      if fn_name in AVAILABLE_TOOLS:
        tool_output = AVAILABLE_TOOLS[fn_name](**fn_args)
        trace_logs.append({"type": "tool_output", "output": tool_output})
        chat_history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": fn_name,
            "content": tool_output,
        })

    # Second pass generator: Stream the response back token by token
    stream = CLIENT.chat.completions.create(
        model=MODEL_NAME, messages=chat_history, stream=True
    )
    return stream, trace_logs
  else:
    trace_logs.append(
        {"type": "thought", "message": "Direct response, no tool required."}
    )
    stream = CLIENT.chat.completions.create(
        model=MODEL_NAME, messages=chat_history, stream=True
    )
    return stream, trace_logs