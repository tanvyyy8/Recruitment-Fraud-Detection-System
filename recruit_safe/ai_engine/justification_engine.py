def generate_justification(label, reasons):

    if not reasons:
        return (
            "The model did not detect strong fraud indicators such as payment requests, unrealistic salary promises, "
            "suspicious urgency patterns, or unofficial recruiter communication. Based on the overall structure and contextual understanding, "
            "the posting appears closer to a genuine recruitment listing."
        )

    explanation_parts = []

    for reason in reasons[:6]:

        reason_lower = reason.lower()

        if "registration fee" in reason_lower or "payment" in reason_lower:
            explanation_parts.append(
                "The posting asks candidates to pay money before joining, which is one of the strongest indicators of recruitment fraud because genuine employers usually do not request payments for job confirmation."
            )

        elif "whatsapp" in reason_lower or "telegram" in reason_lower:
            explanation_parts.append(
                "The recruiter is using unofficial communication platforms like WhatsApp or Telegram instead of formal company channels, which is commonly seen in scam job postings."
            )

        elif "weekly salary" in reason_lower or "monthly salary" in reason_lower:
            explanation_parts.append(
                "The salary offered appears unrealistically high for the job role, especially for simple work-from-home or entry-level tasks, which is a strong warning sign of fake recruitment offers."
            )

        elif "no experience required" in reason_lower:
            explanation_parts.append(
                "The combination of high salary with 'no experience required' creates an unrealistic hiring pattern that is frequently used in fraudulent advertisements."
            )

        elif "limited seats" in reason_lower or "immediate joining" in reason_lower:
            explanation_parts.append(
                "Urgency-based phrases such as limited seats and immediate joining are used to create pressure and force quick decisions without proper verification."
            )

        elif "guaranteed income" in reason_lower or "quick earning" in reason_lower:
            explanation_parts.append(
                "Promises like guaranteed income and quick earning are commonly used to build false trust and attract victims into scam recruitment schemes."
            )

        else:
            explanation_parts.append(
                f'The system detected the suspicious pattern: {reason}. This increased the overall fraud probability.'
            )

    final_explanation = " ".join(list(dict.fromkeys(explanation_parts)))

    if label == "Fraud":
        final_explanation += (
            " Since multiple strong fraud indicators appeared together in the same job posting, "
            "the system classified this listing as Fraud with high confidence."
        )

    elif label == "Suspicious":
        final_explanation += (
            " These indicators suggest moderate risk. The posting should be verified carefully before proceeding."
        )

    else:
        final_explanation += (
            " Although minor suspicious indicators were observed, strong supporting fraud signals were not found, "
            "so the posting appears relatively safe after analysis."
        )

    return final_explanation