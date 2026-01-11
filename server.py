from flask import Flask, request, jsonify
from flask_cors import CORS
from lightweight_agent import SQLAgent
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Agent
agent = SQLAgent()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    user_message = data['message']
    
    try:
        response = agent.run(user_message)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "agent_provider": agent.provider})

if __name__ == '__main__':
    print("Starting Flask API on port 5000...")
    app.run(debug=True, port=5000)
