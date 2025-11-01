# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from skills_extractor import extract_text_from_pdf, extract_skills
from internshala_scraper import scrape_internshala_html


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

@app.route("/recommend", methods=["POST"])
def recommend():
    if "resume" not in request.files:
        return jsonify({"error": "Upload PDF file"}), 400

    pdf = request.files["resume"]
    path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(path)

    text = extract_text_from_pdf(path)
    skills = extract_skills(text)
    all_internships = []
    for skill in skills:
        print(f"Scraping for skill: {skill}")
        all_internships.extend(scrape_internshala_html(skill))

    return jsonify({
        "skills_detected": skills,
        "internships_found": len(all_internships),
        "internships": all_internships
})
if __name__ == "__main__":
    app.run(port=5000, debug=True)
