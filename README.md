# Email PO Extraction(Under development)

The **`email_po_extraction`** project automates the process of extracting **Purchase Order (PO)** details from incoming emails and their attachments. It uses **Flask** for the web interface, **Machine Learning (ML)** for email classification, and **OCR** for extracting text from image-based attachments. The system can also parse **Google Docs** and **Google Sheets** using the Google API.

## Key Features

- **Email Monitoring & Classification**:
  - Automatically checks incoming emails and classifies them as **PO** or **non-PO** using text classification models (e.g., **Llama 3.2B**).
  
- **PO Data Extraction**:
  - Extracts key PO details such as **PO Number**, **Item Name**, **Quantity**, **Rate**, **Delivery Dates**, and **Customer Info** from the email body.
  - Handles attachments in various formats, including **PDFs**, **images** (via OCR), **Excel** files, and **Google Docs/Sheets**.

- **Data Presentation**:
  - Displays the extracted PO details and relevant attachments on a **Flask-based web interface**.
  - Notifies the user if no PO is found in the email.

- **Error Handling & Validation**:
  - Provides error handling for failed data extractions and flags missing or incomplete data for manual correction.

## Installation

### Prerequisites

- Flask
- transformers (for ML models)
- pytesseract (for OCR)
- google-api-python-client (for Google Docs/Sheets parsing)
- PyPDF2 (for PDF parsing)
- pandas (for Excel parsing)
- python-docx (for Word document parsing)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/email_po_extraction.git
   cd email_po_extraction
   
   ```
2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt

   ```
4. Run the Flask App: After setting up the environment, run the Flask app:
   ```
   python run.py
   
   ```


   
"# menarini" 
