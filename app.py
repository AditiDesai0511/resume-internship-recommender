# app.py (MAIN SERVICE)

import os
import re
import json
import requests
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from skills_extractor import extract_text_from_pdf, extract_skills
from internshala_scraper import scrape_internshala_html, _offline_fallback

DEFAULT_SKILLS = ["python", "web development", "data science", "machine learning", "java"]

_groq_client = None
def get_groq():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            _groq_client = Groq(api_key=api_key)
    return _groq_client

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

AI_SERVICE_URL = "http://127.0.0.1:5002"
API_TOKEN = "secret123"

@app.route("/debug-card", methods=["GET"])
def debug_card():
    """Returns first card's raw HTML for diagnosing selector issues."""
    from internshala_scraper import HEADERS
    import requests as req
    from bs4 import BeautifulSoup
    skill = request.args.get("skill", "python")
    slug = skill.replace(" ", "-")
    url = f"https://internshala.com/internships/keywords-{slug}"
    try:
        res = req.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, "html.parser")
        card = soup.select_one("div.individual_internship")
        if not card:
            return jsonify({"error": "no cards found", "page_snippet": res.text[:2000]})
        return jsonify({
            "card_html": str(card)[:3000],
            "all_classes": list({c for el in card.select("[class]") for c in el.get("class", [])}),
            "all_links": [{"href": a.get("href"), "text": a.get_text(strip=True)} for a in card.select("a")],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/recommend", methods=["POST"])
def recommend():
    if "resume" not in request.files:
        return jsonify({"error": "Upload PDF file"}), 400

    pdf = request.files["resume"]
    path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(path)

    text = extract_text_from_pdf(path)
    skills = extract_skills(text)
    
    if not skills:
        return jsonify({
            "skills_detected": [],
            "internships_found": 0,
            "internships": []
        })
    
    all_internships = []
    for skill in skills[:5]:
        try:
            results = scrape_internshala_html(skill)
            all_internships.extend(results if results else _offline_fallback(skill))
        except Exception as e:
            print(f"[ERROR] skill='{skill}': {e}")
            all_internships.extend(_offline_fallback(skill))

    return jsonify({
        "skills_detected": skills,
        "internships_found": len(all_internships),
        "internships": all_internships
    })


@app.route("/internships-by-skills", methods=["POST"])
def internships_by_skills():
    data = request.get_json(silent=True) or {}
    skills = [s for s in data.get("skills", []) if isinstance(s, str) and s.strip()]

    # Use popular defaults when no resume skills are available
    skills_to_fetch = skills[:5] if skills else DEFAULT_SKILLS[:3]

    all_internships = []
    for skill in skills_to_fetch:
        try:
            results = scrape_internshala_html(skill.strip())
            # Guaranteed non-empty: scraper falls back to offline if web scraping fails
            all_internships.extend(results if results else _offline_fallback(skill.strip()))
        except Exception as e:
            print(f"[ERROR] skill='{skill}': {e}")
            all_internships.extend(_offline_fallback(skill.strip()))

    return jsonify({
        "skills_used": skills,
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


@app.route("/resume-ai-review", methods=["POST"])
def resume_ai_review():
    if "resume" not in request.files:
        return jsonify({"error": "Upload a PDF file"}), 400

    pdf = request.files["resume"]
    path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(path)

    text = extract_text_from_pdf(path)
    skills = extract_skills(text)

    if not text.strip():
        return jsonify({"error": "Could not extract text from the PDF. Make sure it is not scanned/image-only."}), 400

    resume_text = text[:4000]  # stay within token budget

    prompt = f"""You are an expert resume reviewer and ATS (Applicant Tracking System) specialist.

Analyse the following resume text and return ONLY a JSON object with exactly this structure (no markdown, no explanation):
{{
  "ats_score": <integer 0-100>,
  "summary": "<2-sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": [
    {{"issue": "<specific problem>", "suggestion": "<actionable fix>"}},
    {{"issue": "<specific problem>", "suggestion": "<actionable fix>"}},
    {{"issue": "<specific problem>", "suggestion": "<actionable fix>"}}
  ],
  "missing_sections": ["<missing item 1>", "<missing item 2>"],
  "ats_tips": ["<ATS tip 1>", "<ATS tip 2>", "<ATS tip 3>"]
}}

Resume:
{resume_text}
"""

    groq = get_groq()
    if not groq:
        return jsonify({"error": "AI service not configured. Set GROQ_API_KEY in your environment."}), 503

    try:
        response = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a resume expert. Respond with valid JSON only — no markdown fences, no extra text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if model adds them
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

        # Extract first {...} block as a safety net
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group()

        result = json.loads(raw)
        result["skills_found"] = skills
        return jsonify(result)

    except json.JSONDecodeError as e:
        print(f"[AI REVIEW] JSON parse error: {e}\nRaw: {raw}")
        return jsonify({"error": "AI returned malformed JSON. Please try again."}), 500
    except Exception as e:
        print(f"[AI REVIEW] Error: {e}")
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500


@app.route("/faculty-resume-review", methods=["POST"])
def faculty_resume_review():
    """
    Accepts JSON resume data (as stored in the DB) and returns an AI analysis
    with an approval recommendation for faculty use.
    """
    data = request.get_json(silent=True) or {}
    resume_data = data.get("resume_data", {})

    if not resume_data:
        return jsonify({"error": "resume_data is required"}), 400

    # Convert structured JSON resume into readable text for the LLM
    def text_from_data(d):
        lines = []
        pi = d.get("personalInformation", {})
        if pi.get("fullName"):   lines.append(f"Name: {pi['fullName']}")
        if pi.get("email"):      lines.append(f"Email: {pi['email']}")
        if pi.get("phoneNumber"):lines.append(f"Phone: {pi['phoneNumber']}")
        if pi.get("location"):   lines.append(f"Location: {pi['location']}")
        if pi.get("linkedIn"):   lines.append(f"LinkedIn: {pi['linkedIn']}")
        if pi.get("gitHub"):     lines.append(f"GitHub: {pi['gitHub']}")
        if d.get("summary"):     lines.append(f"\nSummary:\n{d['summary']}")
        skills = [s.get("title","") for s in d.get("skills", []) if s.get("title")]
        if skills: lines.append(f"\nSkills: {', '.join(skills)}")
        for edu in d.get("education", []):
            lines.append(f"\nEducation: {edu.get('degree','')} at {edu.get('university','')} ({edu.get('graduationYear','')})")
        for exp in d.get("experience", []):
            lines.append(f"\nExperience: {exp.get('jobTitle','')} at {exp.get('company','')} ({exp.get('duration','')})\n  {exp.get('responsibility','')}")
        for proj in d.get("projects", []):
            lines.append(f"\nProject: {proj.get('title','')} — {proj.get('description','')}")
        for cert in d.get("certifications", []):
            lines.append(f"\nCertification: {cert.get('title','')} ({cert.get('issuingOrganization','')}, {cert.get('year','')})")
        for ach in d.get("achievements", []):
            lines.append(f"\nAchievement: {ach.get('title','')} ({ach.get('year','')})")
        langs = d.get("languages", [])
        if langs: lines.append(f"\nLanguages: {', '.join(str(l) for l in langs if l)}")
        return "\n".join(lines)

    resume_text = text_from_data(resume_data)[:4000]

    if not resume_text.strip():
        return jsonify({"error": "Resume data appears to be empty."}), 400

    prompt = f"""You are an expert resume reviewer assisting a faculty member who must decide whether to approve a student's resume for internship applications.

Analyse the resume below and return ONLY a JSON object with exactly this structure (no markdown, no explanation):
{{
  "ats_score": <integer 0-100>,
  "recommendation": "<approve|reject>",
  "recommendation_reason": "<1-2 sentences explaining the recommendation>",
  "summary": "<2-sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": [
    {{"issue": "<specific problem>", "suggestion": "<actionable fix>"}},
    {{"issue": "<specific problem>", "suggestion": "<actionable fix>"}}
  ],
  "missing_sections": ["<missing item 1>", "<missing item 2>"]
}}

Guidelines for recommendation:
- "approve" if ATS score >= 60 and the resume has essential sections (contact info, education, skills, at least one experience or project)
- "reject" if score < 60 or critical sections are missing

Resume:
{resume_text}
"""

    groq = get_groq()
    if not groq:
        return jsonify({"error": "AI service not configured. Set GROQ_API_KEY in your environment."}), 503

    try:
        response = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a resume expert assisting faculty. Respond with valid JSON only — no markdown fences, no extra text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group()
        result = json.loads(raw)
        return jsonify(result)

    except json.JSONDecodeError as e:
        print(f"[FACULTY AI REVIEW] JSON parse error: {e}\nRaw: {raw}")
        return jsonify({"error": "AI returned malformed JSON. Please try again."}), 500
    except Exception as e:
        print(f"[FACULTY AI REVIEW] Error: {e}")
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)