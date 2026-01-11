import os
from lightweight_agent import SQLAgent
from dotenv import load_dotenv

load_dotenv()

def test_agent():
    print("Testing Lightweight AI SQL Agent...")
    
    agent = SQLAgent()
    if not agent.provider:
        print("SKIPPING TEST: No API Key found.")
        return

    questions = [
        "How many tracks are there?",
        "List top 3 artists by number of albums."
    ]
    
    for q in questions:
        print(f"\nQuestion: {q}")
        try:
            result = agent.run(q)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"SQL: {result['sql']}")
                print(f"Answer: {result['answer']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_agent()
