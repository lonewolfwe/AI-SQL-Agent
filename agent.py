import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from database import get_engine, get_schema
from tools import execute_sql

load_dotenv()

# Define State
class AgentState(TypedDict):
    question: str
    sql_query: str
    query_result: str
    answer: str
    error: str

# Initialize LLM
# Check for API keys and select provider
if os.getenv("GOOGLE_API_KEY"):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
elif os.getenv("OPENAI_API_KEY"):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
else:
    # Fallback or error - for now assume user will provide key
    print("Warning: No API Key found. Please set GOOGLE_API_KEY or OPENAI_API_KEY in .env")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# Nodes
def generate_sql_node(state: AgentState):
    """Generates SQL query based on the question and schema."""
    question = state["question"]
    engine = get_engine()
    schema = get_schema(engine)
    
    prompt = f"""You are an expert SQL assistant.
    Given the following database schema:
    {schema}
    
    Write a SQL query to answer the user's question: "{question}"
    Return ONLY the SQL query, nothing else. Do not wrap it in markdown code blocks (```sql ... ```).
    If you cannot answer the question with the given schema, return "ERROR: Cannot answer".
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    sql_query = response.content.strip()
    
    # Clean up markdown if present
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]
    if sql_query.startswith("```"):
        sql_query = sql_query[3:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
        
    return {"sql_query": sql_query.strip()}

def execute_query_node(state: AgentState):
    """Executes the generated SQL query."""
    sql_query = state["sql_query"]
    
    if sql_query.startswith("ERROR"):
        return {"query_result": "Error in SQL generation", "error": sql_query}
        
    result = execute_sql(sql_query)
    return {"query_result": result}

def explain_result_node(state: AgentState):
    """Explains the query result in plain English."""
    question = state["question"]
    sql_query = state["sql_query"]
    result = state["query_result"]
    
    prompt = f"""You are a helpful data analyst.
    User Question: {question}
    SQL Query Executed: {sql_query}
    Result Data:
    {result}
    
    Please provide a concise, natural language answer to the user's question based on the result.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content}

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_query", execute_query_node)
workflow.add_node("explain_result", explain_result_node)

workflow.set_entry_point("generate_sql")
workflow.add_edge("generate_sql", "execute_query")
workflow.add_edge("execute_query", "explain_result")
workflow.add_edge("explain_result", END)

app = workflow.compile()

def run_agent(question: str):
    """Helper to run the agent."""
    result = app.invoke({"question": question})
    return result
