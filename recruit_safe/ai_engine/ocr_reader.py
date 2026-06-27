import pytesseract
import cv2
from PIL import Image

# Windows path for Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_image(image_path):

    try:

        img = cv2.imread(image_path)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # noise reduction
        gray = cv2.medianBlur(gray, 3)

        # threshold for better text contrast
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        text = pytesseract.image_to_string(gray)

        return text

    except Exception as e:

        print("OCR Error:", e)

        return ""

# ================= AUTO JOB TITLE FROM OCR =================

def extract_job_title(text):

    try:

        lines = text.split("\n")

        for line in lines:

            line = line.strip()

            if len(line) > 5 and len(line) < 60:

                lower = line.lower()

                if (
                    "job" in lower or
                    "data entry" in lower or
                    "work from home" in lower or
                    "assistant" in lower or
                    "analyst" in lower
                ):
                    return line.title()

        # fallback
        for line in lines:

            line = line.strip()

            if len(line) > 8:
                return line.title()

        return "Image Job Poster"

    except:
        return "Image Job Poster"