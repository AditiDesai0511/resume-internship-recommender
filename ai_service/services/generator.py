from providers.openai_provider import generate_text

def build_prompt(profile, skills, mode):
    return f"""
You are a career assistant. Generate 5 resume bullet points for {mode}.
Profile: {profile}
Skills: {", ".join(skills)}

Format bullet points only. No titles.
"""

def generate_suggestions(profile, skills, mode):
    prompt = build_prompt(profile, skills, mode)
    return generate_text(prompt)
