import os
import re
import shutil
import mysql.connector
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from app.config.env import DOWNLOAD_FOLDER
from app.file_parser import parse_attachment
from app.config.database_env import database_host, database_user, database_password, database
from app.setup_model import setup_text_gen_model

from app.email_handle.google_drive import get_files_from_drive, download_file_from_drive
from app.email_handle.pdf2text import extract_text_with_positions_from_scanned_pdf
from app.email_handle.extractfields import extract_field, extract_document_field
from app.email_handle.extractfields import get_basic_data
from datetime import datetime
from app.email_handle.database_handler import logo_check,new_log_sheet,insert_ocr_result, get_supplier_domain,email_new_attachment,multi_doc_intervention,supplier_name_intervention, attatchment_error,email_no_domain, set_complete_flag, set_item_count_for_attachments,get_supplier_from_logo, new_turn, new_attachment,get_supplier, start_ocr, get_exist_attachment, exist_supplier_domain_and_name, new_supplier_domain_and_name, set_supplier_for_attachments
import json
import csv
import cv2
import numpy as np
import fitz  # PyMuPDF (for PDF handling)
from PIL import Image
import tempfile
from app.config.env import Logo_Folder
import pandas as pd
from app import socketio 

file_path = r"D:\KingTiger\email\Email_po_extraction-main\AX09.xls"

SupplierDomain = "S93T"
text_gen_model = setup_text_gen_model()

logos_folder_path = Logo_Folder

SERVICE_ACCOUNT_FILE = r'D:\KingTiger\email\Email_po_extraction-main\app\email_handle\neon-rite-449718-m4-0a3e2d4992a8.json'  # Path to your service account JSON file
FOLDER_ID = '1dIgQL8iZKT2EMT_bBDtJCI1PSlfei0FG'  # Google Drive folder ID to upload files into

# Define the scopes for the Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

supplier_domain_against_country = {
    "Australia" : "AU82",
    "Canada" : ""
}

# robert-young@neon-rite-449718-m4.iam.gserviceaccount.com
def authenticate_service_account(service_account_file, scopes):
    """
    Authenticate using a service account and return the Google Drive service object.
    """
    creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('drive', 'v3', credentials=creds)
    return service

def create_folder(service, folder_name, parent_folder_id):
    """
    Create a folder in Google Drive under the specified parent folder.

    :param service: The authenticated Google Drive API service object.
    :param folder_name: The name of the folder to be created.
    :param parent_folder_id: The ID of the parent folder where the new folder will be created.
    :return: The folder ID of the newly created folder.
    """
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }

    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder['id']


def upload_pdf_to_drive_with_folder(file_path, folder_id, service_account_file, dn):
    """
    Upload a PDF file to Google Drive after renaming it, and organize by PO folder.

    :param file_path: Path to the PDF file to upload.
    :param folder_id: Google Drive parent folder ID to upload the file into.
    :param service_account_file: Path to the service account JSON credentials file.
    :param po_number: The PO number to create or identify the folder for the uploaded document.
    :return: The file ID of the uploaded file.
    """
    service = authenticate_service_account(service_account_file, SCOPES)

    # Check if the folder for this PO exists
    query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{dn}' and '{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])

    # If no folder exists, create one
    if not folders:
        print(f"Creating new folder for PO {dn}...")
        po_folder_id = create_folder(service, dn, folder_id)
    else:
        # If the folder exists, use the existing folder ID
        po_folder_id = folders[0]['id']
        print(f"Using existing folder for PO {dn}: {po_folder_id}")

    # Define the media content (PDF file)
    media = MediaFileUpload(file_path, mimetype='application/pdf')

    # Create the file metadata
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [po_folder_id],  # Upload to the PO folder
        'mimeType': 'application/pdf'
    }

    try:
        # Upload the file to the PO folder
        file = service.files().create(media_body=media, body=file_metadata, fields='id').execute()
        print(f'File uploaded successfully to folder {po_folder_id}. File ID: {file["id"]}')
        return file['id']
    except Exception as e:
        print(f'Error uploading file: {e}')
        return None
    
    
def check_new_email(email_id,subject, sender, body, attachments,admin_email,date):
    # Connect to the database
    connection = mysql.connector.connect(
        host=database_host,
        user=database_user,
        password=database_password,  # Replace with your password if set
        database=database  # Replace with your database name
    )
    cursor = connection.cursor()

    try:
        # Check if the email_id exists in the table
        query = "SELECT COUNT(*) FROM email_check WHERE email_id = %s"
        cursor.execute(query, (email_id,))
        result = cursor.fetchone()

        if result[0] > 0:
            print(f"Email ID {email_id} already exists in the database.")
            return 0  # Email ID already exists
        else:
            # Insert the email_id into the table
            insert_query = "INSERT INTO email_check (email_id,subject, sender, body, attachments,admin_email,date) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(insert_query, (email_id,subject, sender, body, attachments,admin_email,date,))
            connection.commit()
            print(f"Email ID {email_id} added to the database.")
            return 1  # Email ID added successfully

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return -1  # Indicate a database error

    finally:
        # Close the database connection
        cursor.close()
        connection.close()

def check_email_data(email_analysis_data, emailID, subject):
    connection = mysql.connector.connect(
        host=database_host,
        user=database_user,
        password=database_password,  # Replace with your password if set
        database=database  # Replace with your database name
    )
    cursor = connection.cursor()

    try:
        # Check if the email_id exists in the table
        if email_analysis_data['DN#'] == "" or email_analysis_data['DN#'] == 'None':        
            query = "SELECT `DN#` FROM email_check WHERE email_subject = %s"
            cursor.execute(query, (subject,))
            result = cursor.fetchone()
            if result["DN#"] :
                query = "UPDATE email_check SET email_subject = %s, `DN#` = %s WHERE email_id = %s"
                cursor.execute(query, (subject, result["DN#"],emailID))
                connection.commit()
                return result["DN#"]
            else:
                return -1
        else:
            query = "UPDATE email_check SET email_subject = %s, `DN#` = %s WHERE email_id = %s"
            cursor.execute(query, (subject,email_analysis_data['DN#'], emailID))
            connection.commit()
            return 1

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return -1  # Indicate a database error

    finally:
        # Close the database connection
        cursor.close()
        connection.close()
def create_prompt_email_body(subject, sender, body):
    fields = ['Supplier', 'Delivery Note (DN)', 'Packing List (PL)','Supplier Email']
    
    # Construct the prompt with flexibility for various formats and languages
    prompt = (
        "You are a highly intelligent and multilingual assistant capable of understanding and extracting structured data "
        "from various formats of text, including different languages. I need you to identify and extract specific fields "
        "from the provided text. Please be aware that the fields might not be present, and the formats can vary. If a field "
        "is missing, simply return 'null' for that field. The fields I need are:\n"
        f"{', '.join(fields)}.\n\n"
        "Please return the extracted information as a JSON object. Here is the text:\n\n"
        f"{subject}\n\n"
        f"{body}\n\n"
        "Ensure your response follows this JSON format exactly:\n"
        "[\n"
        "   {\n"
        "     \"Supplier\": \"value or null\",\n"
        "     \"Supplier Email\": \"value or null\",\n"
        "     \"DN#\": \"value or null\",\n"
        "     \"PL#\": \"value or null\",\n"
        "   }\n"
        "]\n"
        "Remember to consider context clues and language variations to accurately extract the fields."
    )
    return prompt

def get_or_create_folder(service, folder_name, parent_folder_id):
    """
    Get or create a folder in Google Drive.
    """
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id)").execute()
    folders = results.get('files', [])

    if folders:
        return folders[0]['id']  # Return existing folder ID
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder['id']  # Return new folder ID

def upload_pdf_to_drive_with_folder(file_path, parent_folder_id, service_account_file):
    """
    Upload a PDF file to Google Drive inside the specified folder.
    """
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [parent_folder_id]
    }

    media = MediaFileUpload(file_path, mimetype='application/pdf')
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return uploaded_file.get('id')

def rename_and_upload_to_drive(supplier_domain, supplier_name, dn_pl, po, doc_type, date, original_name, file_data, service_account_file, parent_folder_id):
    """
    Rename the file, ensure folder structure (entity_code/dn_pl), and upload to Google Drive.
    """
    # Define new file name
    print("-------------------------------")
    new_name = f"{supplier_name}_{dn_pl}_{po}_!{doc_type}!_{date}{os.path.splitext(original_name)[1]}"
    print(f"Renaming file to: {new_name}")

    # Save file temporarily
    temp_folder = 'temp'
    os.makedirs(temp_folder, exist_ok=True)
    temp_file_path = os.path.join(temp_folder, new_name)

    with open(temp_file_path, 'wb') as f:
        f.write(file_data)

    # Authenticate Google Drive API
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=credentials)

    # Get or create the entity_code folder inside the parent_folder_id
    supplier_domain_folder_id = get_or_create_folder(service, supplier_domain, parent_folder_id)
    
    supplier_name_folder_id = get_or_create_folder(service, supplier_name, supplier_domain_folder_id)

    # Get or create the dn_pl folder inside entity_code folder
    dn_pl_folder_id = get_or_create_folder(service, dn_pl, supplier_name_folder_id)

    # Upload the file to the dn_pl folder
    file_id = upload_pdf_to_drive_with_folder(temp_file_path, dn_pl_folder_id, service_account_file)

    # Remove the temporary file
    os.remove(temp_file_path)

    return file_id
def get_domain_from_sender(sender):
    """
    Extracts the domain from an email sender string.
    Example Input: 'Venus Dev <venusdev42@gmail.com>'
    Output: 'gmail.com'
    """
    # Regular expression to extract email address from the sender string
    match = re.search(r'<([^>]+)>', sender)
    
    if match:
        email = match.group(1)  # Extract the email inside < >
    else:
        email = sender  # If no angle brackets, assume sender is just the email address

    # Extract the domain from the email address
    domain = email.split('@')[-1].lower()
    return domain
def clean_quantity(q):
    return q.split()[0] if q else None


def sanitize_filename(filename):
    """Removes invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    
def export_unique_to_csv(data_list):
    if not data_list:
        print("No data to export.")
        return

    # Step 1: Get INV NO# (DN) for filename
    dn = data_list[0].get('INV NO#', 'UNKNOWN_DN')
    csv_file = f"DN_{dn}.csv"

    # Step 2: Remove duplicates
    unique_data = []
    seen = set()

    for item in data_list:
        tuple_item = tuple(sorted(item.items()))
        if tuple_item not in seen:
            seen.add(tuple_item)
            unique_data.append(item)

    # Step 3: Export to CSV
    csv_columns = unique_data[0].keys() if unique_data else []

    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for row in unique_data:
                writer.writerow(row)
        print(f"Data successfully exported to {csv_file}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

# Call the function
def find_logo_match(target_image, logos_folder_path):
    # If target_image is a file path (string), read it
    if isinstance(target_image, str):
        target_img = cv2.imread(target_image, cv2.IMREAD_GRAYSCALE)
    # If target_image is a PIL Image, convert to OpenCV format
    elif isinstance(target_image, Image.Image):
        target_img = cv2.cvtColor(np.array(target_image), cv2.COLOR_RGB2GRAY)
    else:
        return "Invalid target image format."
    
    if target_img is None:
        return "Target image not found."
    
    # Initialize feature detector (SIFT)
    detector = cv2.SIFT_create()

    # Find keypoints and descriptors
    kp1, des1 = detector.detectAndCompute(target_img, None)
    if des1 is None:
        return "No features detected in the target image."

    best_match = None
    best_matches_count = 0
    matcher = cv2.BFMatcher()

    # Iterate through each logo in the folder
    for logo_file in os.listdir(logos_folder_path):
        logo_path = os.path.join(logos_folder_path, logo_file)
        logo_img = cv2.imread(logo_path, cv2.IMREAD_GRAYSCALE)
        if logo_img is None:
            continue

        # Find keypoints and descriptors for the logo
        kp2, des2 = detector.detectAndCompute(logo_img, None)
        if des2 is None:
            continue

        # Match descriptors
        matches = matcher.knnMatch(des1, des2, k=2)

        # Apply Lowe's ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        # Update best match if current logo has more good matches
        if len(good_matches) > best_matches_count:
            best_matches_count = len(good_matches)
            best_match = logo_file

    return best_match if best_match else None

def extract_top_20_percent(pdf_path, output_image_path):
    # Open the PDF
    doc = fitz.open(pdf_path)
    first_page = doc[0]  # Get the first page

    # Render the page as an image (high DPI for better quality)
    pix = first_page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Calculate 20% of the height
    height_20_percent = int(pix.height * 0.2)

    # Crop the top 20%
    cropped_img = img.crop((0, 0, pix.width, height_20_percent))

    # Save the cropped image temporarily (optional)
    temp_image_path = "temp_cropped.jpg"
    cropped_img.save(temp_image_path)

    # Find the best logo match
    matched_logo = find_logo_match(temp_image_path, logos_folder_path)
    

    # Optional: Delete the temporary image
    os.remove(temp_image_path)
    return matched_logo




    
    
def analysis_email(subject, sender, body, attachments, emailID,admin_email,date):
    
    SupplierDomain = get_supplier_domain(sender)
    
    if SupplierDomain == "":
        email_no_domain(emailID, "Unregistered User!", "Error")
        print("Unregistered User!!!")
    vendor_domain = ""
    vendor_name = ""
    vendor_domain, vendor_name = get_supplier(get_domain_from_sender(sender))
    
    if SupplierDomain == "" and (vendor_domain=="" or vendor_domain=="None"):
        email_no_domain(emailID, "There is no domain and registered User!", "Error")
        return
    
    if SupplierDomain == "":
        SupplierDomain = vendor_domain
    email_prompt=create_prompt_email_body(subject,sender,body)
    basic_detail = get_basic_data(email_prompt)
    
    print("-----------vendor information from email domain---------------")
    print(vendor_domain, vendor_name)
    if vendor_domain=="None" or vendor_domain=="":
        print("There is no vendo domain matches email domain...........")
        email_no_domain(emailID, "There is no vendo domain matches email domain.", "warning")
                
    
    if basic_detail[0]['DN#']=='null' and basic_detail[0]['PL#']:
        basic_detail[0]['DN#']=basic_detail[0]['PL#']
    
    if basic_detail[0]['DN#']=='' or basic_detail[0]['DN#']=='None' or basic_detail[0]['DN#']=='null':
        email_no_domain(emailID, "There is no DN# in this email.", "error")
        return -1
    else:
        new_vendor_domain, new_vendor_name = new_turn(emailID, basic_detail[0]['DN#'],admin_email,date)
        socketio.emit("new_dn_turn", {"DN#":basic_detail[0]['DN#']})
        if vendor_domain == "None" or vendor_domain == "":
            vendor_domain = new_vendor_domain
            vendor_name = new_vendor_name
    
    print("-----------vendor information using DN#---------------")
    print(vendor_domain, vendor_name)
    
    supplier_name = ""
    doc_type_list = []
    dn_po_number=""
    for attachment in attachments:
        try:
            output_image_path = "top_20_percent.jpg"
            matched_logo = extract_top_20_percent(attachment, output_image_path)
            if matched_logo:
                logo_id = matched_logo.split('.')[0]
                logo_domain, logo_name = get_supplier_from_logo(logo_id)
                print(f"✅ Matched logo: {logo_domain, logo_name}")
                if logo_name != vendor_name:
                    logo_check(emailID, logo_id, matched_logo,basic_detail[0]['DN#'])
                    print("To User : Check your logo.")
            else:
                print("Did not find the matched logo.")
                
            extract_text_with_positions_from_scanned_pdf(attachment,"output.txt")
            po_details = extract_field("output.txt", "output.json")
            
            print("-------------------")
            print(po_details)

            unique_docs_type = len(set(item["Doc Type"] for item in po_details))

            if unique_docs_type == 1:
                if po_details[0]["Doc Type"] != "COA" and po_details[0]["Doc Type"]!= "Certificate of Analysis":
                    count = get_exist_attachment(basic_detail[0]['DN#'], po_details[0]["Doc Type"])
                    if count > 0:
                        error_msg = "There is already "+ po_details[0]["Doc Type"] +" documnet. Please check your attachment again."
                        attatchment_error(basic_detail[0]['DN#'],error_msg, "error" ,emailID, -1, po_details[0]["Doc Type"])
                        sheet_error = "The DN - "+basic_detail[0]['DN#']+" already has "+ po_details[0]["Doc Type"] +"document. Check it."
                        new_log_sheet("Attachment Error",admin_email,sheet_error)
                        print(f"There is already {po_details[0]["Doc Type"]} documnet. Please check your attachment again.")
                        return
                    if count == -1:
                        # attatchment_error(basic_detail[0]['DN#'],"Not found the exist DN# Number.", "error"  ,emailID)
                        print("Not found the exist DN Number.")
                        return
                new_attachment(po_details[0]["Doc Type"], basic_detail[0]['DN#'])
                socketio.emit("new_attachment_detect", {})
                email_new_attachment(po_details[0]["Doc Type"], basic_detail[0]['DN#'],emailID)
                print("-------------------")
                print(po_details)
                doc_type_list.append(po_details[0]["Doc Type"])
                if po_details[0]["Doc Type"]=="DN" :
                    dn_po_number = po_details[0]["PO#"]
                    if (po_details[0]["DN#"]!="" or po_details[0]["DN#"]!="null") and po_details[0]["DN#"]!=basic_detail[0]['DN#']:
                        attatchment_error(basic_detail[0]['DN#'],"The DN# from DN is different from the DN# in email.", "error" ,emailID, -2, po_details[0]["DN#"])
                        sheet_error = "The DN - "+basic_detail[0]['DN#']+" is different from DN in the email."
                        new_log_sheet("Attachment Error",admin_email,sheet_error)
                        print("The DN# from DN is different against the DN# from email.")
                        return
                    
                if po_details[0]["Doc Type"]=="INV" or po_details[0]["Doc Type"]=="DN" :
                    if vendor_domain == "":            
                        exist_supplier = exist_supplier_domain_and_name(SupplierDomain, po_details[0]["Supplier"])
                        if exist_supplier == 0:
                            new_supplier_domain_and_name(SupplierDomain, po_details[0]["Supplier"])
                            supplier_name_intervention(emailID, SupplierDomain, po_details[0]["Supplier"],basic_detail[0]['DN#'])
                            print("---------To User : Please check this vendor name and vendor domain.------------")
                        vendor_domain = SupplierDomain
                        vendor_name = po_details[0]["Supplier"]
            if unique_docs_type >= 2:
                unique_data = {item["Doc Type"]: item for item in po_details}.values()
                # Convert back to a list if needed
                attachment_type = ""
                print("-------------------")
                print(po_details)
                unique_list_of_doc = list(unique_data)
                for po_detail in unique_list_of_doc:
                    if po_detail["Doc Type"] != "COA" and po_detail["Doc Type"]!= "Certificate of Analysis":
                        count = get_exist_attachment(basic_detail[0]['DN#'], po_detail["Doc Type"])
                        if count > 0:
                            error_msg = "There is already "+ po_detail["Doc Type"] +" documnet. Please check your attachment again."
                            attatchment_error(basic_detail[0]['DN#'],error_msg, "error"  ,emailID, -1, po_detail["Doc Type"])
                            sheet_error = "The DN - "+basic_detail[0]['DN#']+" already has "+ po_detail["Doc Type"] +"document. Check it."
                            new_log_sheet("Attachment Error",admin_email,sheet_error)
                            print(f"There is already {po_detail["Doc Type"]} documnet. Please check your attachment again.")
                            return
                        if count == -1:
                            # attatchment_error(basic_detail[0]['DN#'],"Not found the exist DN# Number.", "error"  ,emailID)
                            print("Not found the exist DN Number.")
                            return
                    new_attachment(po_detail["Doc Type"], basic_detail[0]['DN#'])
                    email_new_attachment(po_detail["Doc Type"], basic_detail[0]['DN#'],emailID)
                    attachment_type = attachment_type + " & " + po_detail["Doc Type"]
                    # doc_type_list.append(po_detail[index]["Doc Type"])
                    if po_detail["Doc Type"]=="DN" :
                        dn_po_number = po_detail["PO#"]
                        if (po_detail["DN#"]!="" or po_detail["DN#"]!="null") and po_detail["DN#"]!=basic_detail[0]['DN#']:
                            attatchment_error(basic_detail[0]['DN#'],"The DN# from DN is different against the DN# from email.", "error"  ,emailID,-2,po_detail["DN#"])
                            sheet_error = "The DN - "+basic_detail[0]['DN#']+" is different from DN in the email."
                            new_log_sheet("Attachment Error",admin_email,sheet_error)
                            print("The DN# from DN is different against the DN# from email.")
                            return
                        
                    if po_detail["Doc Type"]=="INV" or po_detail["Doc Type"]=="DN" :
                        if vendor_domain == "":                                        
                            exist_supplier = exist_supplier_domain_and_name(SupplierDomain, po_detail["Supplier"])
                            if exist_supplier == 0:
                                new_supplier_domain_and_name(SupplierDomain, po_detail["Supplier"])
                                supplier_name_intervention(emailID, SupplierDomain, po_detail["Supplier"],basic_detail[0]['DN#'])
                                print("-----To User : Please check this vendor name and vendor domain.")
                            vendor_domain = SupplierDomain
                            vendor_name = po_detail["Supplier"]
                            
                file_name = os.path.basename(attachment)
                document_name = file_name
                multi_doc_intervention(emailID, vendor_domain, vendor_name, basic_detail[0]['DN#'], attachment_type, document_name)
                doc_type_list.append(attachment_type)
        except ValueError as e:
            print(f"Skipping unsupported attachment: {attachment} - {e}")
    
    
    
    print("-----------vendor information from attachment---------------")
    print(vendor_domain, vendor_name)
    
    if vendor_domain == "" :
        return "There is no Vendor Information."
    # the supplier_domain will get from the frontend when the user register.
    else:
        set_supplier_for_attachments(basic_detail[0]["DN#"],vendor_domain, vendor_name)
        
    supplier_domain = vendor_domain
    supplier_name = vendor_name
    for index, attachment in enumerate(attachments):
        try:
            file_name = os.path.basename(attachment)
            with open(attachment, 'rb') as f:
                file_data = f.read()
    #         # Upload the file to Google Drive
            
            rename_date = datetime.now().strftime("%Y%m%d%H%M")
            if doc_type_list[index]=="DN" :
                file_id = rename_and_upload_to_drive(supplier_domain, supplier_name, basic_detail[0]["DN#"], dn_po_number, doc_type_list[index], "", file_name, file_data, SERVICE_ACCOUNT_FILE, FOLDER_ID)
            else:
                file_id = rename_and_upload_to_drive(supplier_domain, supplier_name, basic_detail[0]["DN#"], "", doc_type_list[index], rename_date, file_name, file_data, SERVICE_ACCOUNT_FILE, FOLDER_ID)
            print(f"File uploaded with ID: {file_id}")
        except ValueError as e:
            print(f"Skipping unsupported attachment: {attachment} - {e}")
 
# def google_drive_activity(supplier, basic_dn):
    
def google_drive_check_for_new_turn(supplier_domain,supplier_name, basic_dn):
    files = get_files_from_drive(supplier_domain, supplier_name, basic_dn)
    inv_data = []
    dn_data  = []
    coa_data = []
    bill_of_lading  = []
    files_doc_type = []
    for file in files:
        filename = file["name"]  # Extract only the filename
        file_id = file["id"]  # Extract file ID
        print(f"!!!!!!!!! {filename}")
        parts = filename.split("!")
        result = ""
        if len(parts) > 2:
            result = parts[1]
        
        if result == "":
            download_file_from_drive(file_id, filename)
            local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
            if os.path.exists(local_path):  # Ensure file exists before processing
                print(f"Processing file: {local_path}")
                # Now process the downloaded file
                extract_text_with_positions_from_scanned_pdf(local_path, "output.txt")
                po_details = extract_field("output.txt", "output.json")
                unique_docs_type = len(set(item["Doc Type"] for item in po_details))

                if unique_docs_type == 1:
                    result = po_details[0]["Doc Type"]
                    if po_details[0]["Doc Type"] != "COA" and po_details[0]["Doc Type"]!= "Certificate of Analysis":
                        count = get_exist_attachment(basic_dn, po_details[0]["Doc Type"])
                        if count > 0:
                            print(f"There are more than two {po_details[0]["Doc Type"]} documnets in your google drive. Please check your attachment again.")
                            return
                        if count == -1:
                            print("Not found the exist DN Number.")
                            return
                    new_attachment(po_details[0]["Doc Type"], basic_dn)
                    if po_details[0]["Doc Type"]=="DN" :
                        if (po_details[0]["DN#"]!="" or po_details[0]["DN#"]!="null") and po_details[0]["DN#"]!=basic_dn:
                            print("The DN# from DN is different against the DN# from google drive.")
                            return

                if unique_docs_type >= 2:
                    unique_data = {item["Doc Type"]: item for item in po_details}.values()
                    unique_list_of_doc = list(unique_data)
                    for po_detail in unique_list_of_doc:
                        result = result + "&" + po_detail["Doc Type"]
                        if po_detail["Doc Type"] != "COA" and po_detail["Doc Type"]!= "Certificate of Analysis":
                            count = get_exist_attachment(basic_dn, po_detail["Doc Type"])
                            if count > 0:
                                print(f"There are more than two {po_details[0]["Doc Type"]} documnets in your google drive. Please check your attachment again.")
                                return
                            if count == -1:
                                print("Not found the exist DN Number.")
                                return
                        new_attachment(po_detail["Doc Type"], basic_dn)
                        if po_detail["Doc Type"]=="DN" :
                            if (po_detail["DN#"]!="" or po_detail["DN#"]!="null") and po_detail["DN#"]!=basic_dn:
                                print("The DN# from DN is different against the DN# from email.")
                                return
        
        files_doc_type.append(result)

    startOCR = start_ocr(basic_dn)
    if startOCR == 1:
        dn_attachment = ''
        inv_attachment = ''
        coa_attachment = ''
        bol_attachment = ''
        # print("*"*20)
        # print(files_doc_type)
        for index, file in enumerate(files):
            filename = file["name"]  # Extract only the filename
            attachment_path = os.path.join(supplier_domain, supplier_name, basic_dn, filename)
            file_id = file["id"] 
            if files_doc_type[index] == "DN":
                download_file_from_drive(file_id, filename)
                local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
                if os.path.exists(local_path):  # Ensure file exists before processing
                    print(f"Processing file: {local_path}")
                    # Now process the downloaded file
                    extract_text_with_positions_from_scanned_pdf(local_path, "output.txt")
                    po_details = extract_document_field("output.txt", "output.json", 2, "")
                    dn_data = po_details
                    dn_attachment = attachment_path
            
            elif files_doc_type[index] == "INV":
                download_file_from_drive(file_id, filename)
                local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
                if os.path.exists(local_path):  # Ensure file exists before processing
                    print(f"Processing file: {local_path}")
                    # Now process the downloaded file
                    extract_text_with_positions_from_scanned_pdf(local_path, "output.txt")
                    po_details = extract_document_field("output.txt", "output.json", 3, "")
                    inv_data = po_details
                    inv_attachment = attachment_path
                    
            elif files_doc_type[index] == "COA":
                download_file_from_drive(file_id, filename)
                local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
                if os.path.exists(local_path):  # Ensure file exists before processing
                    print(f"Processing file: {local_path}")
                    # Now process the downloaded file
                    extract_text_with_positions_from_scanned_pdf(local_path, "output.txt")
                    po_details = extract_document_field("output.txt", "output.json", 4, "")
                    coa_data.append(po_details)
                    coa_attachment = attachment_path
            
            elif files_doc_type[index] == "Bill of Lading" or files_doc_type[index] == "Air Waybill":
                download_file_from_drive(file_id, filename)
                local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
                if os.path.exists(local_path):  # Ensure file exists before processing
                    print(f"Processing file: {local_path}")
                    # Now process the downloaded file
                    extract_text_with_positions_from_scanned_pdf(local_path, "output.txt")
                    po_details = extract_document_field("output.txt", "output.json", 5, "")
                    bill_of_lading = po_details
                    bol_attachment = attachment_path
            else:
                download_file_from_drive(file_id, filename)
                dn_attachment = attachment_path
                inv_attachment = attachment_path
                coa_attachment = attachment_path
                bol_attachment = attachment_path
                local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
                if os.path.exists(local_path):  # Ensure file exists before processing
                    print(f"Processing file: {local_path}")
                    # Now process the downloaded file
                    extract_text_with_positions_from_scanned_pdf(local_path, "output.txt")
                    po_details = extract_document_field("output.txt", "output.json", 6 ,files_doc_type[index])
                    for po_detail in po_details:
                        if po_detail[0]['Doc Type'] == "DN":
                            dn_data = po_detail
                        elif po_detail[0]['Doc Type'] == "INV":
                            inv_data = po_detail
                        elif po_detail[0]['Doc Type'] == "COA":
                            coa_data.append(po_detail)
                        elif po_detail[0]['Doc Type'] == "Bill of Lading" or po_detail[0]['Doc Type'] == "Air Waybill":
                            bill_of_lading.append(po_detail)
        print("==="*20)
        print(dn_data)
        print(inv_data)
        print(coa_data)
        print(bill_of_lading)
        print("==="*20)
        
        socketio.emit("ocr_finished", {"DN#":basic_dn})
        insert_ocr_result(basic_dn,dn_data, inv_data, coa_data, bill_of_lading, dn_attachment,inv_attachment,coa_attachment,bol_attachment)
        item_count = len(dn_data)
        if len(inv_data) > item_count:
            item_count = len(inv_data)
        coa_item_count = len(coa_data)
        set_item_count_for_attachments(basic_dn, item_count, coa_item_count)
        
        # df = pd.read_excel(file_path)

        # filtered_df = df[df['Item Code'] == 'RBMENSYM VN2004']

        # # Convert to JSON (orient='records' gives a list of dictionaries)
        # json_output = filtered_df.to_json(orient='records', indent=2)

        
        
        
        set_complete_flag(basic_dn)
        if item_count > coa_item_count:
            print("There is not enough COA documents. Please check the attachments again.")
            return
        
        match_data = []
        for index,dn in enumerate(dn_data):
            inv = {
                "PO#" : "",
                "Customer Part Code" : "",
                "Packing Slip#" : "",
                "Quantity" : "",
                "Batch#" : "",
                "Supplier Name" : "",
                "Incoterm" : "",
                "Item Description" :"",
                "Invoice Number" : "",
            }
            if index < len(inv_data) :
                inv = inv_data[index]
            new_entry = {
                "PO#" : dn["PO#"],
                "Item Code" : dn["Customer Part Code"] or inv["Customer Part Code"],
                "Packing Slip#" :  dn["Packing Slip#"] or inv["Packing Slip#"],
                "Quantity" :  dn["Quantity"] or inv["Quantity"],
                "Batch#" :  dn["Batch#"] or inv["Batch#"],
                "Supplier Name" : supplier_name,
                "Incoterm" :  dn["Incoterm"] or inv["Incoterm"],
                "Item Description" : dn["Item Description"] or inv["Item Description"],
                "Invoice Number" :  inv["Customer Part Code"],
            }
            match_data.append(new_entry)
        print("-------------------------------")
        print(match_data)
        # match_data = [{'PO#': 'P01-006452', 'Item Code': 'RBMENSYM VN2004', 'Packing Slip#': '191419', 'Quantity': '5000', 'Batch#': '240239', 'Supplier Name': 'ZUELLIG PHARMA VIETNAM LTD', 'Incoterm': 'CIP', 'Item Description': 'SYMPAL 25MGX20 (VN)', 'Invoice Number': 'SYMPL 25MGX20 (VN)'}, {'PO#': 'P0O1-006792', 'Item Code': 'RBMENSYM VN2004', 'Packing Slip#': '191419', 'Quantity': '8080', 'Batch#': '240662', 'Supplier Name': 'ZUELLIG PHARMA VIETNAM LTD', 'Incoterm': 'CIP', 'Item Description': 'SYMPAL 25MGX20 (VN)', 'Invoice Number': 'SYMPL 25MGX20 (VN)'}]
        ax09_data = []
        unique_po_customer = list({(item["PO#"], item["Item Code"]) for item in match_data})
     
        # print("---------------------------AX09-----------------------------")
        # for po, item_code in unique_po_customer:
        #     df = pd.read_excel(file_path)
        #     filtered_df = df[
        #         (df['Item Code'] == item_code) & 
        #         (df['PO Line Number'] == po)
        #     ]
        #     results = filtered_df.to_json(orient='records', indent=2)
        #     print(results)
        #     # for result in results:
        #     ax09_data.append(results)

        # print("---------------------------")
        # print(ax09_data)
    # for index, file in enumerate(files):
    #     filename = file["name"]  # Extract only the filename
    #     file_id = file["id"]
        
    #     if files_doc_type[index] == "DN":
    #         download_file_from_drive(file_id, filename)
    #         local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
    #         if os.path.exists(local_path):  # Ensure file exists before processing
    #             print(f"Processing file: {local_path}")
    #             # Now process the downloaded file
    #             extract_text_with_positions_from_scanned_pdf(local_path, "output.txt")
    #             po_details = extract_field("output.txt", "output.json")
    
        # extract_text_with_positions_from_scanned_pdf(attachment,"output.txt")
        # po_details = extract_document_field("output.txt", "output.json",4)
    # Download the file first
        # download_file_from_drive(file_id, filename)
        # local_path = os.path.join(DOWNLOAD_FOLDER, sanitize_filename(filename))
        # if os.path.exists(local_path):  # Ensure file exists before processing
        #     print(f"Processing file: {local_path}")
        #     # Now process the downloaded file
        #     extract_text_with_positions_from_scanned_pdf(local_path, "output.txt")
        #     po_details = extract_field("output.txt", "output.json")
            
    #         unique_docs_type = len(set(item["Doc Type"] for item in po_details))
    #         if unique_docs_type == 1:
    #             new_attachment(po_details[0]["Doc Type"], basic_dn)
    #             if isinstance(po_details, str):  # If it's a string, convert it
    #                 po_details = json.loads(po_details)

    #             if po_details[0]["Doc Type"] == "DN":
    #                 dn_data=po_details  
    #             elif po_details[0]["Doc Type"] == "COA" or po_details[0]["Doc Type"] == "Certificate of Analysis":
    #                 coa_data = po_details
    #             elif po_details[0]["Doc Type"] == "INV":
    #                 inv_data = po_details
    #             elif po_details[0]["Doc Type"] == "Bill Of Lading" or po_details[0]["Doc Type"] == "BOL" or po_details[0]["Doc Type"] == "AWB" or po_details[0]["Doc Type"] == "Air Waybill":  # Ensure it matches your document type
    #                 bill_of_lading = po_details  # Store as dictionary
    #         else :
    #             for po_detail in po_details:
    #                 new_attachment(po_detail["Doc Type"], basic_dn)
    #                 if isinstance(po_detail, str):  # If it's a string, convert it
    #                     po_detail = json.loads(po_detail)
    #                 if po_detail["Doc Type"] == "DN":
    #                     dn_data.append(po_detail)  
    #                 elif po_detail["Doc Type"] == "COA" or po_detail["Doc Type"] == "Certificate of Analysis":
    #                     coa_data.append(po_detail)
    #                 elif po_detail["Doc Type"] == "INV":
    #                     inv_data.append(po_detail)
    #                 elif po_detail["Doc Type"] == "Bill Of Lading" or po_detail["Doc Type"] == "BOL" or po_detail["Doc Type"] == "AWB" or po_detail["Doc Type"] == "Air Waybill":  # Ensure it matches your document type
    #                     bill_of_lading.append(po_detail)
    #     else:
    #         print(f"File not found: {local_path}. Skipping processing.")

    # if dn_data[0]["DN#"] != basic_dn:
    #     return -1
    # startOCR = start_ocr(basic_dn)
    # if startOCR == 1:
    #     analysis_data = []
    #     new_dn_data = []
    #     new_inv_data = []
        
    #     unkown_dn_data = []
    #     unkown_inv_data = []
    #     unkown_dn_index = 0
    #     unkown_inv_index = 0
        
    #     basic_dn_data={
    #         "PO#":"",
    #         "Item Code":"",
    #         "Packing Slip#":"",
    #         "Quantity":"",
    #         "Batch#":"",
    #         "Incoterms":"",
    #         "Supplier":"",
    #         "Manufacturing Date":"",
    #         "Expiry Date":"",
    #         "Document Date":"",
    #     }
    #     basic_inv_data={
    #         "PO#":"",
    #         "Item Code":"",
    #         "Packing Slip#":"",
    #         "Quantity":"",
    #         "Batch#":"",
    #         "Incoterms":"",
    #         "INV NO#":"",
    #         "Manufacturing Date":"",
    #         "Expiry Date":"",
    #         "Document Date":"",
    #         "Posting Date":""
    #     }
    #     for dn in dn_data:
    #         if dn.get("PO#") and dn.get("PO#")!="null":
    #             normalized_po = dn["PO#"].replace("P0", "PO").replace("P0O", "PO").replace("PO0", "PO").replace("POO", "PO").replace("P00", "PO")  
    #             dn["PO#"] = normalized_po
    #         else:
    #             unkown_dn_data.append(dn)
    #     for inv in inv_data:
    #         if inv.get("PO#") and inv.get("PO#")!="null":
    #             normalized_po = inv["PO#"].replace("P0", "PO").replace("P0O", "PO").replace("PO0", "PO").replace("POO", "PO").replace("P00", "PO")  
    #             inv["PO#"] = normalized_po
    #         else:
    #             unkown_inv_data.append(inv) 
                
    #     if inv_data!=[] and dn_data!=[]:
    #         for dn in dn_data:
    #             if dn.get("PO#") and dn.get("PO#")!="null":
    #                 filtered_data = [inv for inv in inv_data if inv["PO#"] == dn["PO#"]]
    #                 inv = json.dumps(filtered_data[0], indent=4)
    #                 print("1111111111111111111111111111111111111111111111")
    #                 if len(filtered_data) == 0:
    #                     if unkown_inv_index >= len(unkown_inv_data):
    #                         inv = basic_inv_data
    #                     else:
    #                         inv = unkown_inv_data[unkown_inv_index]
    #                         unkown_inv_index = unkown_inv_index + 1
    #                 else:
    #                     inv = filtered_data[0]
    #                 print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #                 new_entry = {
    #                     "PO#": dn.get("PO#"),
    #                     "Item Code": dn.get("Item Code") or inv.get("Item Code"),
    #                     "Packing Slip#": dn.get("Packing Slip#") or inv.get("Packing Slip#"),
    #                     "Quantity": dn.get("Quantity") or inv.get("Quantity"),
    #                     "Batch#": dn.get("Batch#") or inv.get("Batch#"),
    #                     "INV NO#": inv.get("INV NO#"),
    #                     "Incoterms": dn.get("Incoterms") or inv.get("Incoterms") or (bill_of_lading[0]["Incoterms"] if bill_of_lading and len(bill_of_lading) > 0 else None),
    #                     "Supplier": dn.get("Supplier"),
    #                     "Manufacturing Date": dn.get("Manufacturing Date") or inv.get("Manufacturing Date") or (coa_data[0]["Manufacturing Date"] if coa_data and len(coa_data) > 0 else None),
    #                     "Expiry Date": dn.get("Expiry Date") or inv.get("Expiry Date") or (coa_data[0]["Expiry Date"] if coa_data and len(coa_data) > 0 else None),
    #                     "Document Date": dn.get("Document Date") or inv.get("Document Date"),
    #                     "Posting Date": inv.get("Posting Date") or (bill_of_lading[0]["Posting Date"] if bill_of_lading and len(bill_of_lading) > 0 else None),
    #                 }

    #                 analysis_data.append(new_entry)
    #                 new_dn_data.append(dn)
    #                 new_inv_data.append(inv)
    #         # print("::::::::::::::::::::::::::::::::::::::::::::::::")
    #         # print(analysis_data)
    #         for inv in inv_data:
    #             if inv.get("PO#") and inv.get("PO#")!="null":
    #                 filtered_data = [dn for dn in dn_data if dn["PO#"] == inv["PO#"]]
    #                 if len(filtered_data) == 0:
    #                     if unkown_dn_index >= len(unkown_dn_data):
    #                         dn = basic_dn_data
    #                     else:
    #                         dn = unkown_dn_data[unkown_dn_index]
    #                         unkown_dn_index = unkown_dn_index + 1
    #                         new_entry = {
    #                             "PO#": dn.get("PO#"),
    #                             "Item Code": dn.get("Item Code") or inv.get("Item Code"),
    #                             "Packing Slip#": dn.get("Packing Slip#") or inv.get("Packing Slip#"),
    #                             "Quantity": dn.get("Quantity") or inv.get("Quantity"),
    #                             "Batch#": dn.get("Batch#") or inv.get("Batch#"),
    #                             "INV NO#": inv.get("INV NO#"),
    #                             "Incoterms": dn.get("Incoterms") or inv.get("Incoterms") or (bill_of_lading[0]["Incoterms"] if bill_of_lading and len(bill_of_lading) > 0 else None),
    #                             "Supplier": dn.get("Supplier"),
    #                             "Manufacturing Date": dn.get("Manufacturing Date") or inv.get("Manufacturing Date") or (coa_data[0]["Manufacturing Date"] if coa_data and len(coa_data) > 0 else None),
    #                             "Expiry Date": dn.get("Expiry Date") or inv.get("Expiry Date") or (coa_data[0]["Expiry Date"] if coa_data and len(coa_data) > 0 else None),
    #                             "Document Date": dn.get("Document Date") or inv.get("Document Date"),
    #                             "Posting Date": inv.get("Posting Date") or (bill_of_lading[0]["Posting Date"] if bill_of_lading and len(bill_of_lading) > 0 else None),
    #                         }
    #                     analysis_data.append(new_entry)
    #                     new_dn_data.append(dn)
    #                     new_inv_data.append(inv)
    #         print("::::::::::::::::::::::::::::::::::::::::::::::::")
            
    #         export_unique_to_csv(analysis_data)    
    
    
    
    
    
    
    
    
            # print(analysis_data)
    # doc_type_list=[]
    # inv_data = []
    # dn_data  = []
    # coa_data = []
    # bill_of_lading  = []
    # for attachment in attachments:
    #     try:
    #         extract_text_with_positions_from_scanned_pdf(attachment,"output.txt")
    #         po_details = extract_field("output.txt", "output.json")
    #         # Ensure po_details is always a dictionary
    #         if isinstance(po_details, str):  # If it's a string, convert it
    #             po_details = json.loads(po_details)

    #         if po_details[0]["Doc Type"] == "DN":
    #             dn_data=po_details  
    #         elif po_details[0]["Doc Type"] == "COA":
    #             coa_data = po_details
    #         elif po_details[0]["Doc Type"] == "INV":
    #             inv_data = po_details
    #         elif po_details[0]["Doc Type"] == "Bill Of Lading":  # Ensure it matches your document type
    #             bill_of_lading = po_details  # Store as dictionary

    #     except ValueError as e:
    #         print(f"Skipping unsupported attachment: {attachment} - {e}")
    #     except json.JSONDecodeError as e:
    #         print(f"Error decoding JSON from output.json: {e}")
    # print("-------------------------")
    # print(dn_data)
    # print("-------------------------")
    # print(inv_data)
    # inv_lookup = {}
    # for item in inv_data:
    #     po_key = item["PO#"]
    #     if po_key not in inv_lookup:
    #         inv_lookup[po_key] = []
    #     inv_lookup[po_key].append(item)

    # analysis_output = []
    # for dn in dn_data:
    #     normalized_po = dn["PO#"].replace("P0", "PO")  # Normalize PO format
    #     inv_matches = inv_lookup.get(normalized_po, [])

    #     if inv_matches:
    #         for inv in inv_matches:
    #             new_entry = {
    #                 "DN#": dn.get("DN#"),
    #                 "PO#": dn.get("PO#"),
    #                 "Supplier Item Code": dn.get("Supplier Item Code") or inv.get("Supplier Item Code"),
    #                 "Menarini Item Code": dn.get("Menarini Item Code"),
    #                 "Quantity": f"{inv.get('Quantity', '0')} UNIT",
    #                 "Batch#": inv.get("Batch#"),
    #                 "INV NO#": inv.get("INV NO#"),
    #                 "Incoterms": inv.get("Incoterms"),
    #                 "Date of loading": bill_of_lading[0]["Date of loading"] if bill_of_lading else None,
    #                 "Executed on": bill_of_lading[0]["Executed on"] if bill_of_lading else None,
    #                 "Manufacturing Date": coa_data[0]["Manufacturing Date"] if coa_data else None,
    #                 "Expiry Date": coa_data[0]["Expiry Date"] if coa_data else None,
    #                 "Document Date": dn.get("Document Date"),
    #                 "PO LINE#": dn.get("PO LINE#") if inv.get("PO LINE#") == 'null' else inv.get("PO LINE#"),  # Use DN PO LINE# if INV PO LINE# is 'null'
    #                 "Packing Slip#": dn.get("Packing Slip#"),
    #                 "AX ENTITY": dn.get("AX ENTITY"),
    #                 "VENDOR NAME": dn.get("VENDOR NAME"),
    #                 "VENDOR CODE": dn.get("VENDOR CODE")
    #             }
    #             analysis_output.append(new_entry)
    
    # print(json.dumps(analysis_output, indent=4))
    
    
    
    
    
    # idx = 0
    # rename_date = ""
    # if email_analysis_data["Document Date"] == "" or email_analysis_data["Document Date"] == "null" or email_analysis_data["Document Date"] == None:
    #     rename_date = datetime.now().strftime("%Y%m%d%H%M")
    #     email_analysis_data["Document Date"] = datetime.now().strftime("%m-%d-%Y")


    # check_email_data(email_analysis_data,emailID,subject)
    
    # for attachment in attachments:
        # print("-----------")
        # doc_type = doc_type_list[idx] if idx < len(doc_type_list) else None
        # file_name = os.path.basename(attachment)
        # with open(attachment, 'rb') as f:
        #     file_data = f.read()
        # # Upload the file to Google Drive
        # file_id = rename_and_upload_to_drive("PHAR", email_analysis_data["DN#"], email_analysis_data["PO#"], doc_type, rename_date, file_name, file_data, SERVICE_ACCOUNT_FILE, FOLDER_ID)
        # print(f"File uploaded with ID: {file_id}")
        # print(email_analysis_data)
        # idx = idx + 1

    # return 0
   