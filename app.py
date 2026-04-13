import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

current_document_text = ""


def load_knowledge_base():
    try:
        with open("knowledge_base.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "No knowledge base found."


def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text.strip()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    global current_document_text

    if "file" not in request.files:
        return jsonify({"message": "No file part found."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No file selected."}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"message": "Only PDF files are allowed."}), 400

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        current_document_text = extract_text_from_pdf(file_path)

        if not current_document_text:
            return jsonify({"message": "Could not extract any text from this PDF."}), 400

        return jsonify({"message": "PDF uploaded successfully."})
    except Exception as e:
        return jsonify({"message": f"Error reading PDF: {str(e)}"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    global current_document_text

    data = request.get_json()
    user_message = data.get("message", "")

    knowledge = load_knowledge_base()

    system_prompt = f"""
You are a helpful document assistant.
Use the uploaded PDF text and the knowledge base below to answer clearly.

Knowledge base:
{knowledge}

Uploaded PDF content:
{current_document_text}

Instructions:
- Answer in plain language.
- Base your answer on the uploaded PDF when possible.
- If the answer is not in the PDF, say so clearly.
- Do not invent details.
- Keep the answer practical and beginner-friendly.
"""

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        reply_text = response.output_text
        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
