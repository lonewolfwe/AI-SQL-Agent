from langchain_core.tools import tool
from sqlalchemy import text
from database import get_engine, get_schema

# Initialize engine globally for tools to access (or pass it in context)
# For simplicity in this agent, we'll create a new engine instance or use a singleton pattern if needed.
# Here we'll just create it.
engine = get_engine()

@tool
def list_tables() -> str:
    """Lists all tables in the database."""
    from sqlalchemy import inspect
    inspector = inspect(engine)
    return ", ".join(inspector.get_table_names())

@tool
def get_table_schema(table_names: str) -> str:
    """
    Returns the schema for the specified table(s). 
    Input should be a comma-separated list of table names.
    """
    inspector = inspect(engine)
    tables = [t.strip() for t in table_names.split(",")]
    schema_str = ""
    all_tables = inspector.get_table_names()
    
    for table in tables:
        if table in all_tables:
            schema_str += f"Table: {table}\n"
            columns = inspector.get_columns(table)
            for col in columns:
                schema_str += f"  - {col['name']} ({col['type']})\n"
            schema_str += "\n"
        else:
            schema_str += f"Table {table} not found.\n"
            
    return schema_str

@tool
def execute_sql(sql_query: str) -> str:
    """
    Executes a SQL query against the database and returns the results.
    Use this tool to run the generated SQL.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            # Fetch all results
            rows = result.fetchall()
            # Get column names
            columns = result.keys()
            
            if not rows:
                return "Query executed successfully but returned no results."
            
            # Format as a simple string or JSON
            result_str = f"Columns: {', '.join(columns)}\n"
            for row in rows:
                result_str += f"{row}\n"
                
            return result_str
    except Exception as e:
        return f"Error executing SQL: {str(e)}"
