import os
import requests
import threading
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Securely fetch API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Error: GEMINI_API_KEY is missing. Set it in Render.")

# Set up Google Gemini API URL
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Initialize Flask app
app = Flask(__name__)

# Set up rate limiting (5 requests per 5 minutes per user)
limiter = Limiter(
    get_remote_address,  
    app=app,  
    default_limits=["5 per 5 minutes"]
)

@app.route("/")
def home():
    return jsonify({"message": "✅ Gemini AI API is running!"})

@app.route("/ask", methods=["POST"])
@limiter.limit("5 per 5 minutes")  # Enforce rate limiting
def ask_gemini():
    try:
        data = request.json
        user_prompt = data.get("prompt")

        if not user_prompt:
            return jsonify({"error": "❌ Please provide a prompt!"}), 400

        response_data = []

        # Request to Gemini API (Run in a separate thread for better performance)
        def fetch_response():
            payload = {"contents": [{"parts": [{"text": user_prompt}]}]}
            headers = {"Content-Type": "application/json"}

            response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                response_data.append(response.json())
            else:
                response_data.append({"error": "❌ Failed to fetch response from Gemini API"})

        thread = threading.Thread(target=fetch_response)
        thread.start()
        thread.join()

        return jsonify(response_data[0])

    except Exception as e:
        return jsonify({"error": "❌ Server Error! Please try again later."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Use a non-default port for security