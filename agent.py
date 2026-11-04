# import json
# import os
# import sqlite3
# from dotenv import load_dotenv
# from openai import OpenAI
# from streamlit import status

# load_dotenv()

# CLIENT = OpenAI(
#     base_url=os.getenv("OLLAMA_BASE_URL"),
#     api_key="ollama",
# )

# MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5")
# DB_PATH = "data/productivity.db"    

# def add_task(title: str, due_date: str ="Today")-> str:
#     """Adds a new task to the local SQLite productivity database."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO tasks (title, due_date, status) VALUES (?, ?, ?)",
#         (title, due_date, "PENDING")

#     )
#     conn.commit()
#     conn.close()
#     return json.dumps(
#         {"status": "success", "message": f"Task '{title}' added due {due_date}."}
        
#     )

# def list_tasks()-> str:
#     """Retrieves all pending tasks from the database"""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, title, due_date, status FROM tasks WHERE status = 'PENDING'")
#     rows = cursor.fetchall()
#     conn.close()
#     tasks = [
#         {
#             "id": r[0],
#             "title": r[1],
#             "due_date":r[2],
#             "status":r[3],
#         }
#         for r in rows
#     ]

#     return json.dumps(tasks)


# def add_note(content: str)->str:
#     """Saves a quick note or meeting summary to the database."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
#     conn.commit()
#     conn.close()
#     return json.dumps(
#         {"status": "success", "message": "Notes successfully saved."}
#     )


# AVAILABLE_TOOLS= {
#     "add_task": add_task,
#     "list_tasks": list_tasks,
#     "add_note": add_note,
# }

# TOOLS=[
#     {
#         "type":"function",
#         "function": {
#             "name": "add_task",
#             "description": "Add a new task or action item to the task list.",
#             "parameters":{
#                 "type": "object",
#                 "properties":{
#                     "title":{
#                         "type": "string",
#                         "description": "The description of the task."
#                     },
#                     "due_date":{
#                         "type": "string",
#                         "description":(
#                             "Due timeframe (e.g., 'Tomorrow', 'Friday',"
#                             "'2026-06-01'."
#                         ),
#                     },
#                 },
#                 "required":["title"]
#             },
#         },
#     },
#     {
#         "type":"function",
#         "function":{
#             "name":"list_tasks",
#             "description": "Retrieve all tasks currently stored in the database."
#         },
#         "parameters":{
#             "type": "object", 
#             "properties":{}
#         },
#     },

#     {
#         "type":"function",
#         "function":{
#             "name":"add_note",
#             "description":"Save a meeting note, thought, or text log.",
#             "parameters":{
#                 "type": "object",
#                 "properties":{
#                     "content":{
#                         "type": "string",
#                         "description": "The text content of the note.",
#                     },
#                 },
#                 "required":["content"],
#             }
#         }
#     }
# ]


# def run_agent_turn(user_prompt: str, chat_history:list=None)-> str:
#     """Executes a single reasoning turn with tool-calling capabilities."""
#     if chat_history is None:
#         chat_history=[
#             {
#                 "role": "system",
#                 "content":(
#                     "You are an expert personal productivity and workflow"
#                     "automation agent. Use your tools to manage tasks and notes"
#                     "accurately based on user requests."
#                 ),
#             }
#         ]

#     chat_history.append({"role": "user", "content": user_prompt})

#     #First pass: Ask model for response or tool call request
#     response = CLIENT.chat.completions.create(
#         model=MODEL_NAME,
#         messages=chat_history,
#         tools=TOOLS,
#     )

#     response_message = response.choices[0].message
#     chat_history.append(response_message)

#     if response_message.tool_calls:
#         for tool_call in response_message.tool_calls:
#             fn_name= tool_call.function.name
#             fn_args= json.loads(tool_call.function.arguments)

#             if fn_name in AVAILABLE_TOOLS:
#                 tool_output = AVAILABLE_TOOLS[fn_name](**fn_args)

#                 chat_history.append({
#                     "role":"tool",
#                     "tool_call_id": tool_call.id,
#                     "name":fn_name,
#                     "content":tool_output
#                 })

#         #Second pass: Generate a final conversational reply incorporating tool output
#         second_response = CLIENT.chat.completions.create(
#             model=MODEL_NAME, messages=chat_history
#         )
#         final_reply = second_response.choices[0].message.content
#     else:
#         final_reply = response_message.content

#     chat_history.append({"role": "assistant", "content": final_reply})

#     return final_reply
    



import json
import os
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CLIENT = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    api_key="ollama",  # Ollama placeholder key
)
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5")
DB_PATH = "data/productivity.db"


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
  """Saves a quick note or meeting summary to the database."""
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
  conn.commit()
  conn.close()
  return json.dumps(
      {"status": "success", "message": "Note successfully saved."}
  )


# Mapping tool names to executable python functions
AVAILABLE_TOOLS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "add_note": add_note,
    "read_local_file":read_local_file,
}

# OpenAI/Ollama compatible function schemas
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task or action item to the task list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The description of the task.",
                    },
                    "due_date": {
                        "type": "string",
                        "description": (
                            "Due timeframe (e.g., 'Tomorrow', 'Friday',"
                            " '2026-06-01')."
                        ),
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": (
                "Retrieve all tasks currently stored in the database."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "Save a meeting note, thought, or text log.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text content of the note.",
                    }
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_local_file",
            "description": "Read the contents of a local text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": (
                            "The name or path of the file to read (e.g.,"
                            " 'README.md')."
                        ),
                    }
                },
                "required": ["filename"],
            },
        },
    },
]


def run_agent_turn(user_prompt: str, chat_history: list = None) -> str:
  """Executes a single reasoning turn with tool-calling capabilities."""
  if chat_history is None:
    chat_history = [
        {
            "role": "system",
            "content": (
                "You are an expert personal productivity and workflow"
                " automation agent. Use your tools to manage tasks and notes"
                " accurately based on user requests."
            ),
        }
    ]

  chat_history.append({"role": "user", "content": user_prompt})
  trace_logs=[]

  # First pass: Ask model for response or tool call request
  response = CLIENT.chat.completions.create(
      model=MODEL_NAME, messages=chat_history, tools=TOOLS_SCHEMA
  )

  response_message = response.choices[0].message
  chat_history.append(response_message)

  # Check if model invoked tool calls
  if response_message.tool_calls:
    for tool_call in response_message.tool_calls:
      fn_name = tool_call.function.name
      fn_args = json.loads(tool_call.function.arguments)

      trace_logs.append({
        "type":"tool_call",
        "tool":fn_name,
        "arguments": fn_args,
      })

      if fn_name in AVAILABLE_TOOLS:
        tool_output = AVAILABLE_TOOLS[fn_name](**fn_args)
        trace_logs.append({"type":"tool_output", "output":tool_output})
        # Append tool output to history
        chat_history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": fn_name,
            "content": tool_output,
        })

    # Second pass: Generate final conversational reply incorporating tool output
    second_response = CLIENT.chat.completions.create(
        model=MODEL_NAME, messages=chat_history
    )
    final_reply = second_response.choices[0].message.content
  else:
    final_reply = response_message.content
    trace_logs.append(
      {"type": "thought", "message": "Direct respinse, no tool required."}
    )

  chat_history.append({"role": "assistant", "content": final_reply})
  return final_reply, trace_logs


def read_local_file(filename: str)->str:
  """Reads the content of a local text file in the project directory."""
  try:
    if not os.path.exists(filename):
      return json.dumps(
        {"status": "error", "message":f"File '{filename}' not found."}
      )
    with open(filename, "r", encoding="utf-8") as f:
      content= f.read()
    return json.dumps({"status": "success", "content": content})
  except Exception as e:
    return json.dumps({"status":"error", "message": str(e)})