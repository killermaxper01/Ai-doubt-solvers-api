from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from Render (.env)
load_dotenv()

app = Flask(__name__)

# Secure API Key and Secret Token
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_AUTH_TOKEN = os.getenv("SECRET_AUTH_TOKEN")  # Custom token for security

if not GEMINI_API_KEY or not SECRET_AUTH_TOKEN:
    raise ValueError("Missing API key or secret auth token in environment variables!")

# Gemini API Endpoint
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# ✅ Flask-Limiter for Rate Limiting (10 requests per hour per IP)
limiter = Limiter(
    get_remote_address,  
    app=app,
    default_limits=["10 per hour"],  # ✅ Limits users to 10 AI queries per hour
    storage_uri="memory://",  # ✅ Uses in-memory storage (reset every hour)
)

@app.route("/get_ai_answer", methods=["POST"])
@limiter.limit("10 per hour")  # ✅ Apply limit to this route
def get_ai_answer():
    """Secure API endpoint for AI response with rate limiting"""
    
    # ✅ Check for secret token in headers
    token = request.headers.get("Authorization")
    if token != SECRET_AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403  # Reject unauthorized requests

    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Call Gemini AI API securely
    try:
        response = requests.post(API_URL, json={"contents": [{"parts": [{"text": question}]}]})
        response_data = response.json()
        answer = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response from AI.")

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ✅ Custom Error Message for Rate Limit Exceeded
@app.errorhandler(429)
def ratelimit_exceeded(e):
    return jsonify({"error": "Rate limit exceeded! You can only ask 10 questions per hour."}), 429

if __name__ == "__main__":
    app.run(debug=True)
