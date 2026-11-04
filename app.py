# import os
# import streamlit as st
# from agent import run_agent_turn
# from database import init_db

# init_db()

# st.set_page_config(
#     page_title="AI Productivity Agent", page_icon="⚡", layout="centered"
# )

# st.title("⚡ Local AI Productivity Agent")
# st.caption(

#     "Powered by Ollama (Qwen 2.5) & Python ReAct Loop running 100% locally."
# )

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input(
#     "What would you like me to do? (e.g., 'Add review PR to tasks for"
#     " tomorrow')"
# ) :
#     st.session_state.messages.append({"role": "user", "content": "prompt"})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         with st.spinner("Agent thinking & checking tools..."):
#             history_payload = [
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are an expert personal productivity and workflow"
#                         " automation agennt."
#                     ),
#                 }
#             ]
#             for m in st.session_state.messages[:-1]:
#                 history_payload.append({"role": m["role"], "content": m["content"]})

#             agent_response = run_agent_turn(prompt, history_payload)
#             st.markdown(agent_response)

#     st.session_state.messages.append(
#         {"role": "assistant", "content": agent_response}
#     )

import os
import streamlit as st
from agent import run_agent_turn
from database import init_db

# Initialize database on app boot
init_db()

st.set_page_config(
    page_title="AI Productivity Agent", page_icon="⚡", layout="centered"
)

st.title("⚡ Local AI Productivity Agent")
st.caption(
    "Powered by Ollama (Qwen2.5) & Python ReAct Loop running 100% locally."
)

# Initialize chat history in session state safely
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display prior chat history
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])
    # If a trace exists for this message, render it
    if "trace" in message and message["trace"]:
      with st.expander("🔍 Agent Reasoning & Tool Trace"):
        for log in message["trace"]:
          st.json(log)

# Accept user prompt via chat input box
if prompt := st.chat_input(
    "What would you like me to do? (e.g., 'Read README.md and add a task to"
    " review it')"
):
  # Display user message
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Generate agent response with a spinner
  with st.chat_message("assistant"):
    with st.spinner("Agent thinking & checking tools..."):
      history_payload = [
          {
              "role": "system",
              "content": (
                  "You are an expert personal productivity and workflow"
                  " automation agent."
              ),
          }
      ]
      for m in st.session_state.messages[:-1]:
        history_payload.append({"role": m["role"], "content": m["content"]})

      agent_response, trace_logs = run_agent_turn(prompt, history_payload)
      st.markdown(agent_response)

      # Show the trace immediately in an expander
      if trace_logs:
        with st.expander("🔍 Agent Reasoning & Tool Trace"):
          for log in trace_logs:
            st.json(log)

  # Save assistant reply and trace to state history
  st.session_state.messages.append({
      "role": "assistant",
      "content": agent_response,
      "trace": trace_logs,
  }) 