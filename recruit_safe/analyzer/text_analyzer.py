import re

# -----------------------------
# Main analysis function
# -----------------------------
def analyze_job_text(text):
    text_lower = text.lower()
    risk_score = 0
    reasons = []

    # -----------------------------
    # 1. PAYMENT / FEE DETECTION
    # -----------------------------
    payment_keywords = [
        "registration fee", "processing fee", "pay", "payment required",
        "security deposit", "training fee", "₹", "rs.", "fees required"
    ]

    if any(word in text_lower for word in payment_keywords):
        risk_score += 30
        reasons.append("Job asks for upfront payment or registration fee")

    # -----------------------------
    # 2. UNOFFICIAL EMAIL CHECK
    # -----------------------------
    free_email_domains = ["@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com"]

    email_matches = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text_lower)

    for email in email_matches:
        if any(domain in email for domain in free_email_domains):
            risk_score += 20
            reasons.append("Uses unofficial or personal email address")
            break

    # -----------------------------
    # 3. WHATSAPP / PERSONAL CONTACT
    # -----------------------------
    if "whatsapp" in text_lower or re.search(r"\b\d{10}\b", text_lower):
        risk_score += 15
        reasons.append("Only WhatsApp or personal number provided for contact")

    # -----------------------------
    # 4. URGENCY LANGUAGE
    # -----------------------------
    urgency_words = [
        "urgent", "immediate hiring", "limited slots",
        "apply immediately", "hurry up", "last chance"
    ]

    if any(word in text_lower for word in urgency_words):
        risk_score += 10
        reasons.append("Uses urgent or pressure-based language")

    # -----------------------------
    # 5. UNREALISTIC SALARY
    # -----------------------------
    salary_patterns = [
        r"\b\d{2,3},?\d{3}\s*(per day|per week)",
        r"\b\d{5,6}\s*(for freshers|no experience)",
        r"\bhigh salary\b"
    ]

    if any(re.search(pattern, text_lower) for pattern in salary_patterns):
        risk_score += 25
        reasons.append("Unrealistic salary claims detected")

    # -----------------------------
    # 6. NO COMPANY DETAILS
    # -----------------------------
    if not any(word in text_lower for word in ["company", "pvt", "ltd", "inc", "llp", "website"]):
        risk_score += 10
        reasons.append("No clear company details or official website mentioned")
    
     # -----------------------------
     # 7. UNREALISTIC PAY VS HOURS (OCR SAFE)
     # -----------------------------
    numbers = re.findall(r"\d+", text_lower)

    if any(word in text_lower for word in ["hour", "hours", "hrs"]):
      if len(numbers) >= 4:
        risk_score += 40
        reasons.append(
            "Extremely high pay promised for very few working hours"
        )


    # -----------------------------
    # SCORE NORMALIZATION
    # -----------------------------
    if risk_score > 100:
        risk_score = 100

    # -----------------------------
    # FINAL DECISION
    # -----------------------------
    if risk_score >= 60:
        status = "Fraudulent Job"
        risk_level = "High"
        next_steps = [
            "Do not respond to the recruiter",
            "Do not make any payment",
            "Block the contact details",
            "Report this job post on the platform"
        ]
    elif risk_score >= 30:
        status = "Suspicious Job"
        risk_level = "Medium"
        next_steps = [
            "Verify the company on Google and LinkedIn",
            "Ask for an official company email",
            "Do not share personal documents yet"
        ]
    else:
        status = "Likely Genuine Job"
        risk_level = "Low"
        next_steps = [
            "Apply only through the official website",
            "Proceed carefully with communication",
            "Save a copy of the job post"
        ]

    # -----------------------------
    # AWARENESS TIPS (COMMON)
    # -----------------------------
    awareness_tips = [
        "Never pay money to get a job",
        "Verify company details before applying",
        "Avoid sharing Aadhaar, PAN, or bank details",
        "Check company email domain carefully"
    ]

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------
    return {
        "status": status,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "awareness_tips": awareness_tips,
        "what_to_do_next": next_steps
    }
