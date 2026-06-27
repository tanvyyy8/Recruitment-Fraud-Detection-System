from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import os

# Path to trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "distilbert_fraud_detector")

# Load tokenizer
tokenizer = DistilBertTokenizer.from_pretrained(MODEL_PATH)

# Load model
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

# Set model to evaluation mode
model.eval()

def get_model():
    return model, tokenizer