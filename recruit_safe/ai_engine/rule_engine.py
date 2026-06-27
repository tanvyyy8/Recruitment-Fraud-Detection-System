import re


def detect_rules(data):

    reasons = []

    email = data.get("email", "").lower()
    fee = data.get("fee", "").lower()
    salary = data.get("salary", "").lower()
    description = data.get("description", "").lower()
    company = data.get("company", "").lower()

    full_text = f"{salary} {description}"

    # =========================================
    # SAFE / GENUINE INDICATORS
    # =========================================

    safe_keywords = [
        "no registration fee",
        "no payment required",
        "apply through official website",
        "official company website",
        "company career page",
        "interview process",
        "hr department",
        "employee benefits",
        "full-time employment",
        "official email"
    ]

    safe_matches = []

    for word in safe_keywords:
        if word in full_text:
            safe_matches.append(word)

    # =========================================
    # PAYMENT REQUEST DETECTION
    # =========================================

    payment_keywords = [
        "registration fee",
        "processing fee",
        "security deposit",
        "advance payment",
        "joining fee",
        "refundable fee",
        "payment before joining"
    ]

    if fee == "yes":
        reasons.append(
            "The job posting asks the candidate to make a payment before joining."
        )

    for word in payment_keywords:
        if word in full_text:
            reasons.append(
                f'The description contains the exact phrase "{word}" indicating payment request.'
            )

    # =========================================
    # FREE EMAIL DOMAIN DETECTION
    # =========================================

    free_domains = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com"
    ]

    domain = email.split("@")[-1] if "@" in email else ""

    if domain in free_domains:
        reasons.append(
            f'The recruiter email uses free domain "{domain}" instead of official company domain.'
        )

    # =========================================
    # WEEKLY / UNREALISTIC SALARY DETECTION
    # =========================================

    if "per week" in full_text:
        reasons.append(
            'Weekly salary-based offers are frequently used in recruitment scams, especially for simple work-from-home jobs.'
        )

    salary_numbers = re.findall(r"\d+", salary + " " + description)

    if salary_numbers:
        try:
            value = int(salary_numbers[0])

            # unrealistic weekly salary
            if value >= 30000 and "per week" in full_text:
                reasons.append(
                    f'Unrealistically high weekly salary detected: ₹{value} per week for simple job tasks, which is uncommon in genuine recruitment.'
                )

            # unrealistic monthly salary
            if value >= 200000 and "per month" in full_text:
                reasons.append(
                    f'Unrealistically high monthly salary detected: ₹{value} per month, which exceeds normal hiring patterns.'
                )

            # no experience + high salary mismatch
            if value >= 30000 and "no experience required" in full_text:
                reasons.append(
                    'High salary combined with "no experience required" creates a strong mismatch often seen in fraudulent job postings.'
                )

        except:
            pass

    # =========================================
    # SUSPICIOUS KEYWORD DETECTION
    # =========================================

    suspicious_keywords = [
        "urgent hiring",
        "immediate joining",
        "limited seats",
        "quick earning",
        "earn money fast",
        "freshers can apply",
        "work from home",
        "whatsapp",
        "telegram",
        "direct recruiter contact",
        "guaranteed income",
        "minimal workload"
    ]

    for word in suspicious_keywords:
        if word in full_text:
            reasons.append(
                f'The suspicious phrase "{word}" is found in the job description.'
            )

    # =========================================
    # SAFE LOGIC OVERRIDE
    # =========================================

    if len(safe_matches) >= 2 and len(reasons) <= 1:
        return []

    # =========================================
    # REMOVE DUPLICATES
    # =========================================

    reasons = list(dict.fromkeys(reasons))

    return reasons