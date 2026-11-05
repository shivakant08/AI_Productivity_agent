import os
import streamlit as st
from agent import run_agent_turn
from database import init_db

init_db()

st.set_page_config(
    page_title="AI Productivity Agent", page_icon="⚡", layout="centered"
)

st.title("⚡ Local AI Productivity Agent (RAG + Streaming)")
st.caption("Powered by Ollama (Qwen2.5:3b + nomic-embed-text) & ChromaDB.")

if "messages" not in st.session_state:
  st.session_state.messages = []

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])
    if "trace" in message and message["trace"]:
      with st.expander("🔍 Agent Reasoning & Tool Trace"):
        for log in message["trace"]:
          st.json(log)

if prompt := st.chat_input(
    "Try: 'Save a note about our cloud migration strategy' then 'What did I"
    " note about cloud migration?'"
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    with st.spinner("Agent thinking & checking vector memory..."):
      history_payload = [
          {
              "role": "system",
              "content": "You are an expert productivity agent.",
          }
      ]
      for m in st.session_state.messages[:-1]:
        history_payload.append({"role": m["role"], "content": m["content"]})

      stream_response, trace_logs = run_agent_turn(prompt, history_payload)

      # Stream tokens live into the Streamlit UI
      def generate_tokens():
        for chunk in stream_response:
          if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0]

      full_response = st.write_stream(
          chunk.choices[0].delta.content
          for chunk in stream_response
          if chunk.choices[0].delta.content is not None
      )

      if trace_logs:
        with st.expander("🔍 Agent Reasoning & Tool Trace"):
          for log in trace_logs:
            st.json(log)

  st.session_state.messages.append({
      "role": "assistant",
      "content": full_response,
      "trace": trace_logs,
  })



  # Prompt 1: "Save a note: We decided to migrate our production database from MySQL to PostgreSQL next quarter."

# Prompt 2: "What are our plans regarding the database backend?" (Watch it use semantic search to fetch your note even without exact keyword matches, while streaming the answer live word-by-word!)