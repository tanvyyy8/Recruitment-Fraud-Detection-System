import pytesseract
from PIL import Image

# ✅ HARD-CODE PATH FOR WINDOWS
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        image = image.convert("RGB")  # important for OCR
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print("OCR ERROR:", e)
        return ""
