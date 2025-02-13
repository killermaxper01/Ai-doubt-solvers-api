from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ✅ Load Environment Variables (from Render)
load_dotenv()

app = Flask(__name__)

# ✅ Setup Rate Limiter (10 Requests per Hour)
limiter = Limiter(
    get_remote_address,  
    app=app,
    default_limits=["10 per hour"],  # ✅ Limits users to 10 AI queries per hour
    storage_uri="memory://",  # ✅ Uses in-memory storage (reset every hour)
)

# ✅ Load API Key and Secret Token from Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_AUTH_TOKEN = os.getenv("SECRET_AUTH_TOKEN")

if not GEMINI_API_KEY or not SECRET_AUTH_TOKEN:
    raise ValueError("❌ API Key or Secret Token is missing!")

# ✅ Define AI API Endpoint
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.route("/", methods=["GET"])
def home():
    """Simple Welcome Page"""
    return jsonify({"message": "Welcome to AI Doubt Solvers API"}), 200

@app.route("/get_ai_answer", methods=["POST"])
@limiter.limit("10 per hour")
def get_ai_answer():
    """Secure API endpoint for AI response"""
    token = request.headers.get("Authorization")
    
    # ✅ Authentication Check
    if token != SECRET_AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # ✅ Call Gemini AI API Securely
        response = requests.post(API_URL, json={"contents": [{"parts": [{"text": question}]}]})
        response_data = response.json()
        answer = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response from AI.")

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ✅ Custom Error Handler for Rate Limits
@app.errorhandler(429)
def ratelimit_exceeded(e):
    return jsonify({"error": "Rate limit exceeded! You can only ask 10 questions per hour."}), 429

# ✅ Fix Deployment: Run on 0.0.0.0 (Public Access)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
