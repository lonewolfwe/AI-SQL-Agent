import os
from lightweight_agent import SQLAgent
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("Initializing AI SQL Agent...")
    agent = SQLAgent()
    
    if not agent.provider:
        print("Error: No API Key found. Please set GOOGLE_API_KEY or OPENAI_API_KEY in .env")
        return

    print("\n📊 AI SQL Agent (Lightweight CLI)")
    print("Connected to Chinook Database.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            user_input = input("Ask a question: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue
                
            response = agent.run(user_input)
            
            if "error" in response:
                print(f"\n❌ Error: {response['error']}\n")
            else:
                print(f"\n📝 Answer: {response['answer']}")
                print(f"🔧 SQL: {response['sql']}")
                print("-" * 50 + "\n")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
