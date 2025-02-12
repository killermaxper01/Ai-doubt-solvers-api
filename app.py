from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import threading

app = Flask(__name__)

# ✅ Secure API Key (Store in Render Environment Variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Initialize Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("❌ ERROR: Gemini API Key is missing!")

# ✅ Function to Generate Response from Gemini
def get_gemini_response(user_question):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_question)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ✅ API Route for AI Doubt Solver
@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "Missing question"}), 400

        # ✅ Use Threading for Fast Response
        response = []
        thread = threading.Thread(target=lambda: response.append(get_gemini_response(question)))
        thread.start()
        thread.join()

        return jsonify({"response": response[0]})

    except Exception as e:
        return jsonify({"error": "Server error, please try again later"}), 500

# ✅ Run Flask App (For Local Testing)
if __name__ == "__main__":
    app.run(debug=True)
