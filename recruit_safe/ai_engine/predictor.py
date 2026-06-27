import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import os

# ================= MODEL PATH =================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "distilbert_fraud_detector")

# ================= LOAD MODEL =================

tokenizer = DistilBertTokenizer.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()


# ================= PREDICT FUNCTION =================

def predict_job(data):

    title = data.get("title", "")
    company = data.get("company", "")
    description = data.get("description", "")

    # Full text for model prediction
    text = f"{title} {company} {description}".strip()

    # Safety fallback
    if not text:
        return "Genuine", 50

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    with torch.no_grad():

        outputs = model(**inputs)

        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)

        # Fraud class probability
        fraud_probability = probs[0][1].item()

        confidence = round(fraud_probability * 100, 2)

        # confidence normalization
        if confidence > 95:
            confidence = round(88 + (confidence % 7), 2)

        if confidence > 92:
            confidence = 92

        if confidence < 35:
            confidence = round(confidence + 20, 2)

    # Temporary raw label only
    # Final decision will happen inside views.py
    if confidence >= 75:
        label = "Fraud"
    else:
        label = "Genuine"

    return label, confidence