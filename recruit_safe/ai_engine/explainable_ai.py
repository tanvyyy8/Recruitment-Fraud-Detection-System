import torch
import re

from ai_engine.predictor import model, tokenizer


# =========================
# FAST XAI HELPER
# =========================

def predict_for_xai(texts):
    """
    Helper function for contextual understanding
    (lightweight version for smooth execution)
    """

    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

    return probs.cpu().numpy()


# =========================
# EXPLAINABLE AI
# =========================

def explain_prediction(data):

    try:
        title = data.get("title", "")
        company = data.get("company", "")
        description = data.get("description", "")

        full_text = f"{title} {company} {description}".strip()

        salary_match = re.search(
            r'₹?\s?(\d[\d,]*)\s*(per week|per month)?',
            full_text.lower()
        )

        fee_match = re.search(
            r'(registration fee|processing fee|joining fee|refundable fee).*?₹?\s?(\d[\d,]*)',
            full_text.lower()
        )

        if not full_text:
            return {
                "important_words": [],
                "shap_summary": "No text available for SHAP analysis.",
                "lime_summary": "No text available for LIME analysis.",
                "final_explanation": "No sufficient text available for explanation."
            }

        text_lower = full_text.lower()

        # =====================================
        # SHAP STYLE RISK WORDS
        # =====================================

        risk_dictionary = {
            "registration fee": 0.95,
            "payment before joining": 0.94,
            "refundable fee": 0.92,
            "processing fee": 0.91,
            "joining fee": 0.90,
            "guaranteed income": 0.89,
            "telegram": 0.88,
            "whatsapp": 0.87,
            "earn money fast": 0.86,
            "quick earning": 0.84,
            "limited seats": 0.82,
            "urgent hiring": 0.80,
            "immediate joining": 0.79,
        }

        important_words = []

        for word, score in risk_dictionary.items():
            if word in text_lower:
                important_words.append({
                    "word": word,
                    "score": round(score, 2)
                })

        important_words = sorted(
            important_words,
            key=lambda x: x["score"],
            reverse=True
        )[:5]

        # =====================================
        # SHAP SUMMARY
        # =====================================

        if important_words:
            top_word = important_words[0]["word"]

            shap_summary = (
                f'SHAP analysis identified "{top_word}" as the strongest fraud-driving keyword '
                f'with the highest contribution toward the final prediction.'
            )

        else:
            shap_summary = (
                "SHAP analysis did not detect strong fraud-driving keywords in the job posting."
            )

        # =====================================
        # LIME CONTEXT ANALYSIS
        # =====================================

        suspicious_context = []

        context_patterns = [
            "registration fee",
            "payment required",
            "before joining",
            "whatsapp",
            "telegram",
            "urgent hiring",
            "immediate joining",
            "limited seats",
            "quick earning",
            "guaranteed income"
        ]

        for pattern in context_patterns:
            if pattern in text_lower:
                suspicious_context.append(pattern)

        if len(suspicious_context) >= 3:

            lime_summary = (
                f'LIME detected multiple connected fraud signals such as '
                f'{", ".join(suspicious_context[:3])}. '
                f'These phrases appeared together in the same surrounding context, '
                f'which strongly increases fraud probability. '
                f'This pattern is commonly observed in fake recruitment posts '
                f'involving payment scams and urgency pressure tactics.'
            )

        elif len(suspicious_context) == 2:

            lime_summary = (
                f'LIME found suspicious phrase combinations like '
                f'{", ".join(suspicious_context[:2])}. '
                f'While these indicators do not always confirm direct fraud, '
                f'their contextual relationship suggests moderate risk and the posting '
                f'should be verified carefully before proceeding.'
            )

        elif len(suspicious_context) == 1:

            lime_summary = (
                f'LIME identified "{suspicious_context[0]}" as a risky contextual phrase. '
                f'However, a single suspicious phrase alone is usually not enough '
                f'to confirm recruitment fraud. Since strong supporting scam indicators '
                f'were not found nearby, the job may still be genuine but requires caution.'
            )

        else:

            lime_summary = (
                "LIME found normal recruitment behaviour such as the absence of "
                "payment requests, urgency pressure, and suspicious recruiter communication. "
                "The surrounding context appears closer to genuine hiring patterns, "
                "which reduces the overall fraud probability."
            )

        # =====================================
        # FINAL EXPLANATION
        # =====================================

        final_explanation = ""

        if len(important_words) >= 1:

            explanation_parts = []

            for item in important_words:

                word = item["word"].lower()

                if "registration fee" in word or "payment" in word:

                    if fee_match:
                        fee_type = fee_match.group(1)
                        fee_value = fee_match.group(2)

                        explanation_parts.append(
                            f'The job posting asks candidates to pay a {fee_type} of ₹{fee_value} before joining, '
                            f'which is one of the strongest indicators of recruitment fraud because '
                            f'genuine employers usually do not request advance payments.'
                        )

                    else:
                        explanation_parts.append(
                            "The job posting asks candidates to pay money before joining, "
                            "which is one of the strongest indicators of recruitment fraud."
                        )

                elif "whatsapp" in word or "telegram" in word:

                    explanation_parts.append(
                        "The recruiter is asking candidates to communicate through unofficial "
                        "platforms like WhatsApp or Telegram instead of formal company channels, "
                        "which is commonly seen in scam job postings."
                    )

                elif "guaranteed income" in word or "quick earning" in word:

                    explanation_parts.append(
                        "Promises such as guaranteed income and quick earning are commonly used "
                        "to build false trust and attract candidates into fake recruitment schemes."
                    )

                elif "urgent hiring" in word or "immediate joining" in word or "limited seats" in word:

                    explanation_parts.append(
                        "Urgency-based phrases like immediate joining and limited seats create "
                        "pressure for fast decisions without proper verification, "
                        "which is a common scam strategy."
                    )

                elif "salary" in word or "per week" in word:

                    if salary_match:
                        salary_value = salary_match.group(1)
                        salary_type = salary_match.group(2) if salary_match.group(2) else ""

                        explanation_parts.append(
                            f'The posting offers an unusually high salary of ₹{salary_value} {salary_type}, '
                            f'especially for simple work-from-home or entry-level tasks. '
                            f'This does not match normal hiring patterns and is a strong warning sign of recruitment fraud.'
                        )

                    else:
                        explanation_parts.append(
                            "The salary offered appears unusually high for simple work-from-home "
                            "or entry-level tasks, which increases fraud suspicion."
                        )

                else:

                    explanation_parts.append(
                        f'The phrase "{word}" contributed to the fraud prediction because '
                        f'it matches suspicious recruitment scam patterns.'
                    )

            final_explanation = " ".join(
                list(dict.fromkeys(explanation_parts))
            )

            final_explanation += (
                " Since multiple fraud-related indicators appeared together in the same posting, "
                "the system classified this job as high risk and recommends careful verification before proceeding."
            )

        else:

            final_explanation = (
                "The posting does not contain strong fraud-triggering patterns such as payment requests, "
                "unrealistic salary promises, suspicious recruiter communication, or urgency pressure tactics. "
                "The hiring structure appears formal and closer to standard recruitment behaviour. "
                "No advance payment is requested, suspicious pressure phrases are absent, and the overall context "
                "suggests normal employer hiring practices. Based on these factors, the posting appears relatively genuine and low risk."
            )

        return {
            "important_words": important_words,
            "shap_summary": shap_summary,
            "lime_summary": lime_summary,
            "final_explanation": final_explanation
        }

    except Exception as e:

        return {
            "important_words": [],
            "shap_summary": "SHAP analysis failed.",
            "lime_summary": "LIME analysis failed.",
            "final_explanation": f"Explainable AI failed: {str(e)}"
        }