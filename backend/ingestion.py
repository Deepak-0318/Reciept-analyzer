import pytesseract
from pdf2image import convert_from_path
import os
from PIL import Image
import tempfile
import sys
import cv2

# --- Configure Tesseract Path ---
tesseract_path = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
if not os.path.exists(tesseract_path):
    raise FileNotFoundError(f"Tesseract not found at: {tesseract_path}")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

SUPPORTED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg', '.txt']

def extract_text_from_image(image_path):
    try:
        print(f"Extracting text from image: {image_path}")
        
        # Load image using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image with OpenCV")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to enhance text
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Save the enhanced image temporarily
        temp_path = "temp_ocr.jpg"
        cv2.imwrite(temp_path, thresh)

        # Use PIL to open enhanced image and run OCR
        with Image.open(temp_path) as enhanced_img:
            text = pytesseract.image_to_string(enhanced_img)

        # Clean up temp file
        os.remove(temp_path)

        return text.strip()

    except Exception as e:
        raise RuntimeError(f"Error processing image: {e}")


def extract_text_from_pdf(pdf_path):
    poppler_path = r'C:/Users/ASUS/OneDrive/Documents/poppler-24.08.0/Library/bin'
    if not os.path.exists(poppler_path):
        raise FileNotFoundError(f"Poppler path not found: {poppler_path}")
    
    pages = convert_from_path(pdf_path, poppler_path=poppler_path)
    full_text = ""

    with tempfile.TemporaryDirectory() as temp_dir:
        for i, page in enumerate(pages):
            temp_path = os.path.join(temp_dir, f'page_{i}.jpg')
            page.save(temp_path, 'JPEG')
            text = extract_text_from_image(temp_path)
            full_text += text + "\n"
    return full_text.strip()

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def extract_text(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")

    if ext in ['.jpg', '.jpeg', '.png']:
        return extract_text_from_image(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)

# --- Example Run ---
if __name__ == "__main__":
    sample_file = "C:/Users/ASUS/OneDrive/Desktop/Reciept-analyzer/data/2sample.png"
    try:
        text = extract_text(sample_file)
        print("Extracted Text:\n", text)
    except Exception as e:
        print("Error:", e)
