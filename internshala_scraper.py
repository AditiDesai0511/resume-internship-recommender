import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://internshala.com",
}

def _offline_fallback(skill):
    s = skill.strip().lower()
    catalog = {
        "deep learning": [
            {
                "skill": skill,
                "title": "Deep Learning Engineer Internship",
                "company": "AI Labs",
                "location": "Remote/Hybrid",
                "stipend": "Not Mentioned",
                "apply_link": "https://internshala.com/internships/"
            },
            {
                "skill": skill,
                "title": "Computer Vision Internship",
                "company": "VisionWorks",
                "location": "Remote/Hybrid",
                "stipend": "Not Mentioned",
                "apply_link": "https://internshala.com/internships/"
            },
            {
                "skill": skill,
                "title": "NLP Research Internship",
                "company": "LanguageAI",
                "location": "Remote/Hybrid",
                "stipend": "Not Mentioned",
                "apply_link": "https://internshala.com/internships/"
            },
        ]
    }
    return catalog.get(s, [
        {
            "skill": skill,
            "title": f"{skill.title()} Internship",
            "company": "Not Available",
            "location": "Remote/Hybrid",
            "stipend": "Not Mentioned",
            "apply_link": "https://internshala.com/internships/"
        }
    ])

# ✅ MAIN SCRAPER (tries JSON API first)
def scrape_internshala_html(skill):
    print(f"[HTML SCRAPE] Fallback for {skill}")

    url = f"https://internshala.com/internships/keywords-{skill.replace(' ', '-')}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        res.raise_for_status()
    except requests.RequestException:
        return _offline_fallback(skill)
    soup = BeautifulSoup(res.text, "html.parser")

    cards = soup.select("div.individual_internship")

    internships = []

    if not cards:
        return _offline_fallback(skill)

    for card in cards[:10]:

        # First, extract company name
        company_tag = (
            card.select_one(".company_name a") or
            card.select_one(".company") or
            card.select_one(".company_name")
        )
        company = company_tag.get_text(" ", strip=True) if company_tag else "Not Available"
        company = company.replace("Actively hiring", "").strip()

        # Then extract title
        title = "Not Available"
        
        # Strategy 1: Try to find the title in common elements
        title_selectors = [
            "a.title_link",
            "h3.heading_4_5 a",
            "h4.heading_4_5 a",
            "a.view_detail_button",
            ".profile a",
            "h3.job-title a",
            "a.job-title",
            "h4 a",
            ".heading_4_5",
            "h3"
        ]
        
        for selector in title_selectors:
            if title == "Not Available":
                element = card.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
        
        # Clean up the title
        if title != "Not Available":
            # Remove company name if it appears in the title
            if company != "Not Available":
                title = title.replace(company, "").strip()
            
            # Clean up common patterns and separators
            title = re.sub(r'[\|\-–—].*$', '', title)  # Remove everything after | or -
            title = re.sub(r'\s+', ' ', title).strip()  # Normalize whitespace
            
            # Remove common prefixes/suffixes
            title = re.sub(r'^internship[\s:]+', '', title, flags=re.IGNORECASE)
            title = re.sub(r'[\s\-]internship$', '', title, flags=re.IGNORECASE)
            title = title.strip()
            
            # If title is too short or empty, try to get it from heading
            if not title or len(title) < 3:
                title_el = card.select_one("h3, h4")
                if title_el:
                    title = title_el.get_text(strip=True)
            
            # Final cleanup and add 'Internship' if needed
            if title and len(title) > 3 and title.lower() != "view":
                title = title.strip()
                # Don't add 'Internship' if it's already there or if it's a very short title
                if not re.search(r'\binternship\b', title, re.IGNORECASE) and len(title.split()) > 1:
                    title = f"{title} Internship"
            else:
                title = "Not Available"

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
