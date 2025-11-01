import re
import pdfplumber

TECH_SKILLS = [
    "python","django","flask","fastapi","java","spring","c++","c","javascript","react",
    "angular","node","express","html","css","bootstrap","jquery","sql","mysql","mongodb",
    "postgres","postgresql","ml","machine learning","deep learning","nlp",
    "natural language processing","ai","data science","data analysis","pandas",
    "numpy","tensorflow","pytorch","aws","azure","gcp","docker","kubernetes",
    "devops","git","github","rest","flutter","android","ios","opencv",
    "scikit-learn"
]

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + " "
    return text

def extract_skills(text):
    found = set()
    text = text.lower()

    for skill in TECH_SKILLS:
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", text):
            found.add(skill)
    return list(found)
