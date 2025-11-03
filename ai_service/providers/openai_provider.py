import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found! Add it in your .env or system env.")

client = Groq(api_key=api_key)

def generate_text(prompt: str):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ✅ working stable model
            messages=[
                {"role": "system", "content": 
                 "You are an AI assistant that improves student resumes. "
                 "You suggest bullet-point achievements, strong project tasks, "
                 "and impactful resume lines only. No long explanations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"
