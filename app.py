import streamlit as st
import os
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()

st.set_page_config(page_title="AI SQL Agent", page_icon="📊")

st.title("📊 AI SQL Business Analyst")
st.markdown("Ask questions about your data in plain English.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter API Key (Google or OpenAI)", type="password")
    if api_key:
        if api_key.startswith("AIza"): # Simple check for Google Key
            os.environ["GOOGLE_API_KEY"] = api_key
        else:
            os.environ["OPENAI_API_KEY"] = api_key
            
    st.info("Using Chinook Sample Database")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql" in message:
            with st.expander("View SQL"):
                st.code(message["sql"], language="sql")
        if "data" in message:
            with st.expander("View Raw Data"):
                st.text(message["data"])

if prompt := st.chat_input("Ask a question (e.g., 'How many tracks are there?')"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run Agent
    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            try:
                response = run_agent(prompt)
                
                answer = response.get("answer", "I couldn't generate an answer.")
                sql_query = response.get("sql_query", "")
                query_result = response.get("query_result", "")
                
                st.markdown(answer)
                
                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "sql": sql_query,
                    "data": query_result
                })
                
                # Show details immediately for this turn
                if sql_query:
                    with st.expander("View SQL"):
                        st.code(sql_query, language="sql")
                if query_result:
                    with st.expander("View Raw Data"):
                        st.text(query_result)
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
