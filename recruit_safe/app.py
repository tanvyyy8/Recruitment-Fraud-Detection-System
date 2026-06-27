from flask import Flask, render_template, request, jsonify
import os

from analyzer.text_analyzer import analyze_job_text
from analyzer.image_analyzer import extract_text_from_image

app = Flask(__name__)

# ================= PAGES =================

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/analyze")
def analyze():
    return render_template("analyze.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/alerts")
def alerts():
    return render_template("alerts.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/how")
def how():
    return render_template("how.html")

@app.route("/why")
def why():
    return render_template("why.html")

# ================= API =================

@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    data = request.get_json()
    user_text = data.get("text", "")

    if not user_text.strip():
        return jsonify({"error": "No text provided"}), 400

    result = analyze_job_text(user_text)
    return jsonify(result)


@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    print("📸 Image endpoint hit")

    if "image" not in request.files:
        print("❌ No image in request.files")
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    print("✅ Image received:", image_file.filename)

    if image_file.filename == "":
        print("❌ Empty filename")
        return jsonify({"error": "No image selected"}), 400

    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    image_path = os.path.join(upload_folder, image_file.filename)
    image_file.save(image_path)
    print("💾 Image saved at:", image_path)

    extracted_text = extract_text_from_image(image_path)
    print("🧠 OCR extracted text:", extracted_text)

    if not extracted_text.strip():
        return jsonify({"error": "Could not extract text from image"}), 400

    result = analyze_job_text(extracted_text)
    return jsonify(result)

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)
