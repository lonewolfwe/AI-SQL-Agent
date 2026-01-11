from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

def get_engine(db_path: str = "chinook.db") -> Engine:
    """Creates and returns a SQLAlchemy engine for the SQLite database."""
    return create_engine(f"sqlite:///{db_path}")

def get_schema(engine: Engine) -> str:
    """
    Inspects the database and returns the schema in a format suitable for LLMs.
    Includes table names and column details.
    """
    inspector = inspect(engine)
    schema_str = ""
    
    for table_name in inspector.get_table_names():
        schema_str += f"Table: {table_name}\n"
        columns = inspector.get_columns(table_name)
        for col in columns:
            schema_str += f"  - {col['name']} ({col['type']})\n"
        schema_str += "\n"
        
    return schema_str
