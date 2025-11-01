import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://internshala.com",
}

# ✅ MAIN SCRAPER (tries JSON API first)
def scrape_internshala_html(skill):
    print(f"[HTML SCRAPE] Fallback for {skill}")

    url = f"https://internshala.com/internships/keywords-{skill.replace(' ', '-')}"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    cards = soup.select("div.individual_internship")

    internships = []

    for card in cards[:10]:

        # Title
        title_tag = (
            card.select_one("a.job-title") or
            card.select_one("h3.job-title a") or
            card.select_one(".profile")
        )
        title = title_tag.get_text(strip=True) if title_tag else "Not Available"

        # Company
        company_tag = (
            card.select_one(".company_name a") or
            card.select_one(".company") or
            card.select_one(".company_name")
        )
        company = company_tag.get_text(" ", strip=True) if company_tag else "Not Available"
        company = company.replace("Actively hiring", "").strip()

        # Location
        loc_tag = card.select_one(".location_link") or card.select_one(".location")
        location = loc_tag.get_text(strip=True) if loc_tag else "Remote/Hybrid"

        # Stipend
        stipend_tag = (
            card.select_one(".stipend") or
            card.select_one(".stipend_container") or
            card.select_one(".other_info")
        )
        stipend = stipend_tag.get_text(strip=True) if stipend_tag else "Not Mentioned"

        # Apply Link
        apply_btn = (
            card.select_one("a.view_detail_button") or
            card.select_one(".view_detail a") or
            card.select_one("a.job-details-button") or
            card.select_one("a[href*='internship']")
        )

        apply_link = ""
        if apply_btn and apply_btn.get("href"):
            href = apply_btn.get("href")
            apply_link = href if href.startswith("http") else f"https://internshala.com{href}"

        internships.append({
            "skill": skill,
            "title": title,
            "company": company,
            "location": location,
            "stipend": stipend,
            "apply_link": apply_link
        })

    return internships
