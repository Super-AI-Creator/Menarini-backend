import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import json
import io
import cv2
import os
import re
import numpy as np
from .google_drive import authenticate_gdrive,get_specific_file,download_file_from_drive
# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(img):
    open_cv_image = np.array(img)
    open_cv_image = open_cv_image[:, :, ::-1].copy()  # Convert RGB to BGR
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                           cv2.THRESH_BINARY, 11, 2)
    denoised = cv2.fastNlMeansDenoising(adaptive_thresh, None, 30, 7, 21)
    return Image.fromarray(denoised)


def sanitize_filename(filename):
    """Removes invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    
def extract_matching_values_with_positions(pdf_path, input_json):
    service = authenticate_gdrive()
    parts = pdf_path.split(os.sep)
    supplier_domain = ''
    supplier_name = ''
    basic_dn = ''
    filename = ''
    if len(parts) == 4:
        supplier_domain, supplier_name, basic_dn, filename = parts
    file_info = get_specific_file(service, supplier_domain, supplier_name, basic_dn, filename)
    DOWNLOAD_FOLDER = "ocr_downloads/"
    download_file_from_drive(file_info["id"], file_info["name"],DOWNLOAD_FOLDER)
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
    if os.path.exists(local_path):  # Ensure file exists before processing
      doc = fitz.open(local_path)
      structured_data = []

      # Flatten input JSON to get all target values
      target_values = []
      for entry in input_json:
          for k, v in entry.items():
              if v:  # Skip empty values
                  target_values.append((k, str(v)))

      for page_num in range(len(doc)):
          page = doc.load_page(page_num)
          page_width = page.rect.width  # Width of the page in points (1 point = 1/72 inch)
          page_height = page.rect.height
          pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))  # High DPI for better OCR
          pix_width = pix.width
          pix_height = pix.height
          img = Image.open(io.BytesIO(pix.tobytes()))
          img = preprocess_image(img)
          
          # Get OCR data (words + positions)
          ocr_data = pytesseract.image_to_data(
              img, 
              output_type=pytesseract.Output.DICT,
              config='--psm 6'
          )
          
          # Group words into lines (based on Y-coordinate)
          lines = {}
          for i in range(len(ocr_data['text'])):
              text = ocr_data['text'][i].strip()
              if text:
                  y_pos = ocr_data['top'][i]
                  line_key = y_pos // 10  # Group words with similar Y positions
                  if line_key not in lines:
                      lines[line_key] = []
                  lines[line_key].append({
                      "text": text,
                      "x": ocr_data['left'][i],
                      "y": ocr_data['top'][i],
                      "width": ocr_data['width'][i],
                      "height": ocr_data['height'][i]
                  })
          
          # Extract only matching values
          page_values = []
          for line in lines.values():
              line_text = " ".join([word["text"] for word in line])
              for key,target in target_values:
                  if target in line_text:
                      # Find the exact word(s) matching the target
                      matched_words = [word for word in line if word["text"] in target]
                      if matched_words:
                          x_min = min(w["x"] for w in matched_words)
                          y_min = min(w["y"] for w in matched_words)
                          x_max = max(w["x"] + w["width"] for w in matched_words)
                          y_max = max(w["y"] + w["height"] for w in matched_words)
                          page_values.append({
                              "key":key,
                              "value": target,
                              "x": x_min,
                              "y": y_min,
                              "width": x_max - x_min,
                              "height": y_max - y_min
                          })
          
          if page_values:
              structured_data.append({
                  "page": page_num + 1,
                  "page_width":pix_width,
                  "page_height":pix_height,
                  "matches": page_values
              })
  
    data = {
      "data":structured_data,
      "pdf_path":local_path
    }
    return data
