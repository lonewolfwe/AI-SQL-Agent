import sqlite3
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Try importing OpenAI and Google Generative AI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

load_dotenv()

class SQLAgent:
    def __init__(self, db_path: str = "chinook.db"):
        self.db_path = db_path
        self.api_key = None
        self.provider = None
        self._setup_llm()

    def _setup_llm(self):
        """Configures the LLM provider based on available keys."""
        if os.getenv("GOOGLE_API_KEY") and GOOGLE_AVAILABLE:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.provider = "google"
        elif os.getenv("OPENAI_API_KEY") and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.provider = "openai"
        else:
            print("WARNING: No valid API key found for Google or OpenAI.")

    def get_schema(self) -> str:
        """Retrieves the database schema using sqlite3."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema_str = ""
            for table in tables:
                table_name = table[0]
                schema_str += f"Table: {table_name}\n"
                
                # Get columns for each table
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                for col in columns:
                    # col[1] is name, col[2] is type
                    schema_str += f"  - {col[1]} ({col[2]})\n"
                schema_str += "\n"
                
            conn.close()
            return schema_str
        except Exception as e:
            return f"Error getting schema: {e}"

    def generate_sql(self, question: str) -> str:
        """Generates SQL query from natural language question."""
        schema = self.get_schema()
        prompt = f"""You are an expert SQL assistant.
Given the following database schema:
{schema}

Write a SQL query to answer the user's question: "{question}"
Return ONLY the SQL query, nothing else. Do not wrap it in markdown code blocks.
If you cannot answer the question, return "ERROR: Cannot answer".
"""
        return self._call_llm(prompt)

    def execute_sql(self, query: str) -> str:
        """Executes the SQL query."""
        if query.startswith("ERROR"):
            return query
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            conn.close()
            
            if not rows:
                return "Query executed successfully but returned no results."
                
            result_str = f"Columns: {', '.join(columns)}\n"
            for row in rows:
                result_str += f"{str(row)}\n"
            return result_str
        except Exception as e:
            return f"Error executing SQL: {e}"

    def explain_result(self, question: str, query: str, result: str) -> str:
        """Explains the result in plain English."""
        prompt = f"""You are a helpful data analyst.
User Question: {question}
SQL Query Executed: {query}
Result Data:
{result}

Please provide a concise, natural language answer to the user's question based on the result.
"""
        return self._call_llm(prompt)

    def _call_llm(self, prompt: str) -> str:
        """Helper to call the configured LLM."""
        if not self.provider:
            return "Error: No LLM provider configured."
            
        try:
            if self.provider == "google":
                response = self.model.generate_content(prompt)
                text = response.text.strip()
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                text = response.choices[0].message.content.strip()
            
            # Clean up markdown
            if text.startswith("```sql"):
                text = text[6:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
            
        except Exception as e:
            return f"LLM Error: {e}"

    def run(self, question: str) -> Dict[str, str]:
        """Runs the full agent pipeline."""
        print(f"Analyzing: {question}...")
        
        sql = self.generate_sql(question)
        if sql.startswith("ERROR") or sql.startswith("LLM Error"):
            return {"error": sql}
            
        print(f"Generated SQL: {sql}")
        
        result = self.execute_sql(sql)
        print(f"Execution Result: {result[:100]}...") # Truncate log
        
        answer = self.explain_result(question, sql, result)
        
        return {
            "question": question,
            "sql": sql,
            "result": result,
            "answer": answer
        }
