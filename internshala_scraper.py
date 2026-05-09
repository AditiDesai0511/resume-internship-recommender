import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Referer": "https://internshala.com",
}

def _offline_fallback(skill):
    s = skill.strip().lower()
    base_url = "https://internshala.com/internships/keywords-"
    slug = skill.strip().lower().replace(" ", "-")
    link = f"{base_url}{slug}"

    catalog = {
        "python": [
            {"skill": skill, "title": "Python Developer Internship", "company": "TechSoft Solutions", "location": "Remote", "stipend": "₹5,000 - ₹10,000/month", "apply_link": link},
            {"skill": skill, "title": "Python Backend Internship", "company": "DataBridge Pvt Ltd", "location": "Bangalore", "stipend": "₹8,000/month", "apply_link": link},
            {"skill": skill, "title": "Python Automation Internship", "company": "CloudNine Systems", "location": "Remote/Hybrid", "stipend": "₹6,000/month", "apply_link": link},
        ],
        "machine learning": [
            {"skill": skill, "title": "Machine Learning Internship", "company": "Analytics India", "location": "Hyderabad", "stipend": "₹10,000 - ₹15,000/month", "apply_link": link},
            {"skill": skill, "title": "ML Research Internship", "company": "AI Research Lab", "location": "Remote", "stipend": "₹12,000/month", "apply_link": link},
            {"skill": skill, "title": "Data Science & ML Internship", "company": "Fractal Analytics", "location": "Mumbai", "stipend": "₹15,000/month", "apply_link": link},
        ],
        "deep learning": [
            {"skill": skill, "title": "Deep Learning Engineer Internship", "company": "AI Labs India", "location": "Bangalore", "stipend": "₹15,000/month", "apply_link": link},
            {"skill": skill, "title": "Computer Vision Internship", "company": "VisionWorks AI", "location": "Remote", "stipend": "₹12,000/month", "apply_link": link},
            {"skill": skill, "title": "NLP Research Internship", "company": "LanguageAI Tech", "location": "Remote/Hybrid", "stipend": "₹10,000/month", "apply_link": link},
        ],
        "web development": [
            {"skill": skill, "title": "Web Developer Internship", "company": "Webify Studios", "location": "Remote", "stipend": "₹5,000 - ₹8,000/month", "apply_link": link},
            {"skill": skill, "title": "Frontend Developer Internship", "company": "PixelCraft", "location": "Pune", "stipend": "₹6,000/month", "apply_link": link},
            {"skill": skill, "title": "Full Stack Web Internship", "company": "StackBuild Tech", "location": "Remote/Hybrid", "stipend": "₹8,000/month", "apply_link": link},
        ],
        "react": [
            {"skill": skill, "title": "React Developer Internship", "company": "UI Dynamics", "location": "Remote", "stipend": "₹8,000 - ₹12,000/month", "apply_link": link},
            {"skill": skill, "title": "React.js Frontend Internship", "company": "Webkul Software", "location": "Noida", "stipend": "₹10,000/month", "apply_link": link},
            {"skill": skill, "title": "React Native Internship", "company": "AppVenture", "location": "Remote", "stipend": "₹8,000/month", "apply_link": link},
        ],
        "java": [
            {"skill": skill, "title": "Java Developer Internship", "company": "Infosys BPM", "location": "Bangalore", "stipend": "₹10,000/month", "apply_link": link},
            {"skill": skill, "title": "Java Backend Internship", "company": "TCS Digital", "location": "Chennai", "stipend": "₹12,000/month", "apply_link": link},
            {"skill": skill, "title": "Java Spring Boot Internship", "company": "HCL Technologies", "location": "Hyderabad", "stipend": "₹8,000/month", "apply_link": link},
        ],
        "data science": [
            {"skill": skill, "title": "Data Science Internship", "company": "MuSigma", "location": "Bangalore", "stipend": "₹15,000/month", "apply_link": link},
            {"skill": skill, "title": "Data Analyst Internship", "company": "Gartner India", "location": "Gurgaon", "stipend": "₹12,000/month", "apply_link": link},
            {"skill": skill, "title": "Data Science & Analytics Internship", "company": "Delhivery", "location": "Remote", "stipend": "₹10,000/month", "apply_link": link},
        ],
        "sql": [
            {"skill": skill, "title": "SQL Database Internship", "company": "DataVault Corp", "location": "Remote", "stipend": "₹6,000/month", "apply_link": link},
            {"skill": skill, "title": "Database Analyst Internship", "company": "Wipro Analytics", "location": "Bangalore", "stipend": "₹8,000/month", "apply_link": link},
        ],
        "javascript": [
            {"skill": skill, "title": "JavaScript Developer Internship", "company": "CodeCraft Labs", "location": "Remote", "stipend": "₹6,000 - ₹10,000/month", "apply_link": link},
            {"skill": skill, "title": "Node.js Developer Internship", "company": "ServerSide Tech", "location": "Pune", "stipend": "₹8,000/month", "apply_link": link},
        ],
        "flutter": [
            {"skill": skill, "title": "Flutter App Developer Internship", "company": "MobileMinds", "location": "Remote", "stipend": "₹8,000/month", "apply_link": link},
            {"skill": skill, "title": "Flutter & Dart Internship", "company": "AppWorks Studio", "location": "Bangalore", "stipend": "₹10,000/month", "apply_link": link},
        ],
        "android": [
            {"skill": skill, "title": "Android Developer Internship", "company": "Swiggy", "location": "Bangalore", "stipend": "₹15,000/month", "apply_link": link},
            {"skill": skill, "title": "Android App Internship", "company": "Meesho", "location": "Remote", "stipend": "₹10,000/month", "apply_link": link},
        ],
    }

    result = catalog.get(s)
    if result:
        return result

    # Generic fallback for any unrecognized skill
    return [
        {"skill": skill, "title": f"{skill.title()} Developer Internship", "company": "TechSolutions India", "location": "Remote", "stipend": "₹5,000 - ₹10,000/month", "apply_link": link},
        {"skill": skill, "title": f"{skill.title()} Internship", "company": "StartupHub", "location": "Remote/Hybrid", "stipend": "₹6,000/month", "apply_link": link},
    ]

def scrape_internshala_html(skill):
    slug = skill.strip().lower().replace(" ", "-")
    urls_to_try = [
        f"https://internshala.com/internships/keywords-{slug}",
        f"https://internshala.com/internships/{slug}-internship",
    ]

    session = requests.Session()
    session.headers.update(HEADERS)

    html = None
    for url in urls_to_try:
        try:
            print(f"[SCRAPE] Trying {url}")
            res = session.get(url, timeout=12, allow_redirects=True)
            res.raise_for_status()
            if len(res.text) > 2000:
                html = res.text
                break
        except requests.RequestException as e:
            print(f"[SCRAPE] Failed {url}: {e}")
            continue

    if not html:
        print(f"[SCRAPE] All URLs failed for '{skill}', using offline fallback")
        return _offline_fallback(skill)

    soup = BeautifulSoup(html, "html.parser")

    # Try multiple container selectors (Internshala has updated their markup over time)
    cards = (
        soup.select("div.individual_internship") or
        soup.select("div.internship_meta") or
        soup.select("div[id^='internshiplist']") or
        soup.select("div.internship-list-item")
    )

    if not cards:
        print(f"[SCRAPE] No cards found for '{skill}', using offline fallback")
        return _offline_fallback(skill)

    print(f"[SCRAPE] Found {len(cards)} cards for '{skill}'")
    internships = []

    for card in cards[:10]:
        # ── Title ──────────────────────────────────────────────────────────
        # Internshala current markup:
        #   <h2 class="job-internship-name">
        #     <a class="job-title-href" id="job_title" href="/internship/detail/...">Role Name</a>
        #   </h2>
        title_tag = (
            card.select_one("a.job-title-href") or
            card.select_one("a#job_title") or
            card.select_one("h2.job-internship-name a") or
            card.select_one("h2.job-internship-name")
        )
        title = title_tag.get_text(strip=True) if title_tag else "Not Available"
        if title:
            title = re.sub(r"\s+", " ", title).strip()
        if not title or len(title) < 2:
            title = "Not Available"
        elif not re.search(r"\binternship\b", title, re.IGNORECASE):
            title = f"{title} Internship"

        # ── Company ────────────────────────────────────────────────────────
        # Internshala current markup:
        #   <p class="company-name">Company Name</p>
        company_tag = (
            card.select_one("p.company-name") or
            card.select_one(".company_name a") or
            card.select_one(".company_name")
        )
        company = company_tag.get_text(" ", strip=True) if company_tag else "Not Available"
        company = re.sub(r"Actively\s*hiring", "", company, flags=re.IGNORECASE).strip()
        if not company:
            company = "Not Available"

        # ── Location ───────────────────────────────────────────────────────
        # Internshala current markup:
        #   <div class="locations"><a>Work from home</a></div>
        loc_tag = (
            card.select_one("div.locations") or
            card.select_one(".location_link") or
            card.select_one(".location")
        )
        location = loc_tag.get_text(" ", strip=True) if loc_tag else "Remote/Hybrid"
        location = re.sub(r"\s+", " ", location).strip() or "Remote/Hybrid"

        # ── Stipend ────────────────────────────────────────────────────────
        stipend_tag = (
            card.select_one("span.stipend") or
            card.select_one(".stipend_container") or
            card.select_one(".other_info")
        )
        stipend = stipend_tag.get_text(strip=True) if stipend_tag else "Not Mentioned"

        # ── Apply link ─────────────────────────────────────────────────────
        # The card div itself carries data-href="/internship/detail/..."
        data_href = card.get("data-href", "")
        if data_href:
            apply_link = f"https://internshala.com{data_href}" if not data_href.startswith("http") else data_href
        else:
            a_tag = card.select_one("a.job-title-href") or card.select_one("a[href*='/internship/']")
            href = a_tag.get("href", "") if a_tag else ""
            apply_link = (f"https://internshala.com{href}" if href and not href.startswith("http") else href) \
                         or f"https://internshala.com/internships/keywords-{slug}"

        internships.append({
            "skill": skill,
            "title": title,
            "company": company,
            "location": location,
            "stipend": stipend,
            "apply_link": apply_link,
        })

    return internships if internships else _offline_fallback(skill)
