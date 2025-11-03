# app.py (MAIN SERVICE)

import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from skills_extractor import extract_text_from_pdf, extract_skills
from internshala_scraper import scrape_internshala_html

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

AI_SERVICE_URL = "http://127.0.0.1:5002"
API_TOKEN = "secret123"

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
    for skill in skills[:5]:  
        all_internships.extend(scrape_internshala_html(skill))

    return jsonify({
        "skills_detected": skills,
        "internships_found": len(all_internships),
        "internships": all_internships
    })


@app.route("/recommend-with-ai", methods=["POST"])
def recommend_with_ai():
    if "resume" not in request.files:
        return jsonify({"error": "Upload resume file"}), 400

    pdf = request.files["resume"]
    path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(path)

    text = extract_text_from_pdf(path)
    skills = extract_skills(text)

    headers = {"Authorization": API_TOKEN, "Content-Type": "application/json"}

    achievements = requests.post(
        f"{AI_SERVICE_URL}/suggest/achievements",
        json={"profile": text, "skills": skills},
        headers=headers
    ).json()

    projects = requests.post(
        f"{AI_SERVICE_URL}/suggest/projects",
        json={"profile": text, "skills": skills},
        headers=headers
    ).json()

    return jsonify({
        "skills_detected": skills,
        "achievements_suggestions": achievements.get("items", []),
        "projects_suggestions": projects.get("items", [])
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)
