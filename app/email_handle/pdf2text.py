import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import json
import io
import cv2
import numpy as np
import os

# Path to Tesseract executable (for Windows users)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



def preprocess_image(img):
    # Convert to OpenCV image format
    open_cv_image = np.array(img)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    # Apply adaptive thresholding
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY, 11, 2)

    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(adaptive_thresh, None, 30, 7, 21)

    return Image.fromarray(denoised)

def extract_text_with_positions_from_scanned_pdf(pdf_path, output_txt_path):
    structured_text = []

    # Open the PDF document
    doc = fitz.open(pdf_path)

    for i in range(len(doc)):
        page = doc.load_page(i)  # Load each page
        # Increase resolution by a factor of 4 (for higher quality)
        pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))  # Render page to an image with higher resolution
        img = Image.open(io.BytesIO(pix.tobytes()))  # Convert to PIL Image
        
        # Preprocess the image
        img = preprocess_image(img)
        
        # Perform OCR on the image with custom config to preserve spaces
        config = '--psm 6 preserve_interword_spaces'
        ocr_result = pytesseract.image_to_string(img, config=config)
        structured_text.append(ocr_result)

    # Save the structured text to a text file with spaces preserved
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for page_text in structured_text:
            f.write(page_text)
            f.write("\n\n")  # Add spacing between pages
    print(f"Structured text saved to {output_txt_path}")

# Example usage
# pdf_path = "./data/1295_001.pdf"
# output_json_path = "output.json"
# output_txt_path = "output.txt"
# extract_text_with_positions_from_scanned_pdf(pdf_path, output_json_path, output_txt_path)
