import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# ---------------- FRAUD DOMAIN CHECK ----------------

def detect_suspicious_domain(url):

    suspicious_domains = [
        "bit.ly",
        "tinyurl",
        "t.me",
        "telegram",
        "wa.me",
        "whatsapp"
    ]

    for d in suspicious_domains:
        if d in url:
            return True

    return False


# ---------------- MAIN LINK SCRAPER ----------------

def extract_job_from_link(url):

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        domain = urlparse(url).netloc

        job_title = ""
        company = ""
        description = ""

        # =====================================================
        # LINKEDIN SCRAPER
        # =====================================================

        if "linkedin.com" in domain:

            title_tag = soup.find("h1")

            if title_tag:
                job_title = title_tag.get_text().strip()

            company_tag = soup.find("a", {"class": "topcard__org-name-link"})

            if company_tag:
                company = company_tag.get_text().strip()

            if not company:
                company_tag = soup.find("span", {"class": "topcard__flavor"})
                if company_tag:
                    company = company_tag.get_text().strip()

            desc = soup.find("div", {"class": "show-more-less-html__markup"})

            if desc:
                description = desc.get_text().strip()


        # =====================================================
        # INDEED SCRAPER
        # =====================================================

        elif "indeed" in domain:

            title_tag = soup.find("h1")

            if title_tag:
                job_title = title_tag.get_text().strip()

            company_tag = soup.find("div", {"data-company-name": "true"})

            if company_tag:
                company = company_tag.get_text().strip()

            desc = soup.find("div", {"id": "jobDescriptionText"})

            if desc:
                description = desc.get_text().strip()


        # =====================================================
        # NAUKRI SCRAPER
        # =====================================================

        elif "naukri" in domain:

            title_tag = soup.find("h1")

            if title_tag:
                job_title = title_tag.get_text().strip()

            company_tag = soup.find("a", {"class": "comp-name"})

            if company_tag:
                company = company_tag.get_text().strip()

            desc = soup.find("div", {"class": "dang-inner-html"})

            if desc:
                description = desc.get_text().strip()


        # =====================================================
        # GENERIC SCRAPER (fallback)
        # =====================================================

        else:

            title_tag = soup.find("h1")

            if title_tag:
                job_title = title_tag.get_text().strip()

            if not job_title and soup.title:
                job_title = soup.title.get_text().strip()

            meta_company = soup.find("meta", property="og:site_name")

            if meta_company:
                company = meta_company.get("content")

            paragraphs = soup.find_all("p")

            for p in paragraphs[:20]:
                description += p.get_text() + " "


        return job_title, company, description


    except Exception as e:

        print("Link extraction error:", e)

        return "", "", ""