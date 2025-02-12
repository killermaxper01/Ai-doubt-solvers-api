import os
import requests
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Load secure environment variables from Render
AUTH_SECRET = os.getenv("AUTH_SECRET")  # Security Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Google Gemini API Key

# Rate Limiting: Max 5 requests per hour per user
limiter = Limiter(
    get_remote_address,  # Identify users by IP
    app=app,
    default_limits=["5 per hour"]
)

def ask_gemini(question):
    """Send question to Google Gemini API and return the response."""
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateText"
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": {"text": question},
        "temperature": 0.7
    }

    response = requests.post(f"{url}?key={GEMINI_API_KEY}", json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("candidates", [{}])[0].get("output", "No response")
    return "Error contacting AI"

@app.route('/ask', methods=['POST'])
@limiter.limit("5 per hour")  # Enforce Rate Limit
def ask_question():
    """Process question and return AI-generated answer."""
    auth_token = request.headers.get("Authorization")
    if auth_token != AUTH_SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    answer = ask_gemini(question)
    return jsonify({"answer": answer})

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors."""
    return jsonify({"error": "Rate limit exceeded. Try again in 1 hour."}), 429

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)