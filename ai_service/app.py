from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils.auth import require_token
from utils.rate_limit import rate_limit
from services.generator import generate_suggestions



app = Flask(__name__)
CORS(app, origins=os.getenv("CORS_ORIGINS", "").split(","))

@app.route("/suggest/achievements", methods=["POST"])
@require_token
def suggest_achievements():
    if not rate_limit(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded"}), 429

    data = request.json
    profile = data.get("profile", "")
    skills = data.get("skills", [])

    results = generate_suggestions(profile, skills, "achievements")
    return jsonify({"items": results.split("\n")})


@app.route("/suggest/projects", methods=["POST"])
@require_token
def suggest_projects():
    if not rate_limit(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded"}), 429

    data = request.json
    profile = data.get("profile", "")
    skills = data.get("skills", [])

    results = generate_suggestions(profile, skills, "projects")
    return jsonify({"items": results.split("\n")})


@app.route("/suggest/courses", methods=["POST"])
@require_token
def suggest_courses():
    if not rate_limit(request.remote_addr):
        return jsonify({"error": "Rate limit exceeded"}), 429

    data = request.json
    profile = data.get("profile", "")
    skills = data.get("skills", [])

    results = generate_suggestions(profile, skills, "courses")
    return jsonify({"items": results.split("\n")})


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "AI service running ✅"})


if __name__ == "__main__":
    app.run(port=5002, debug=True)
