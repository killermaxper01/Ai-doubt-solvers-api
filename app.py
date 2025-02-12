from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# Load API Key from Render's Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Secure Authentication Token (Use a strong, secret token)
AUTH_SECRET = os.getenv("AUTH_SECRET")

@app.route('/get-api-key', methods=['POST'])
def get_api_key():
    """Securely returns the Gemini API Key only if a valid request is made"""
    auth_token = request.headers.get("Authorization")

    if auth_token == AUTH_SECRET:
        return jsonify({"api_key": GEMINI_API_KEY})
    else:
        return jsonify({"error": "Unauthorized Access"}), 403

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)