from flask import Flask, request, jsonify
from flask_cors import CORS  # NEW
import os
import requests
from dotenv import load_dotenv

# ✅ Load Environment Variables (from Render)
load_dotenv()

app = Flask(__name__)
CORS(app)  # ✅ This enables CORS for all routes

# ✅ Load API Key and Secret Token from Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_AUTH_TOKEN = os.getenv("SECRET_AUTH_TOKEN")

if not GEMINI_API_KEY or not SECRET_AUTH_TOKEN:
    raise ValueError("❌ API Key or Secret Token is missing!")

# ✅ Define Gemini API Endpoint
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-4b-it:generateContent?key={GEMINI_API_KEY}"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to AI Doubt Solvers API"}), 200

@app.route("/get_ai_answer", methods=["POST"])
def get_ai_answer():
    token = request.headers.get("Authorization")

    # ✅ Check Authorization
    if token != SECRET_AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # ✅ Call Gemini API
        response = requests.post(API_URL, json={"contents": [{"parts": [{"text": question}]}]})
        response_data = response.json()

        answer = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response from AI.")

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": "It is a server-side problem, please be patient."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)