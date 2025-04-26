import time
from app.email_handler import connect_to_email, fetch_emails, extract_email_content
from app.email_handle.new_email_handler import check_new_email, analysis_email, google_drive_check_for_new_turn
from app.email_handle.google_drive import detect_drive_changes, authenticate_gdrive, rename_matching_drive_files, rename_supplier_folder
from app.email_handle.database_handler import domain_name_from_emailId, get_all_admin_info
from app import socketio 
import json

IMAP_SERVER = "imap.gmail.com"

# Global state for Drive change detection
drive_service = None
last_page_token = None
seen_changes = set()

@socketio.on('update_multi_doc_google_drive')
def handle_update_multi_doc(data):
    print("Received update_multi_doc_google_drive event:")
    print("Data:", data)

    service = authenticate_gdrive()
    updated_doc_list = data.get("updated_doc_list")
    for item in updated_doc_list:
        old_doc_list = item['old_doc_list'].strip()
        new_doc_list = item['doc_list'].strip()
        vendor_id = item['vendor_id']
        dn = item['DN#']
        supplier_domain, supplier_name = domain_name_from_emailId(vendor_id)
        print(supplier_domain, supplier_name)
        rename_matching_drive_files(service, supplier_domain, supplier_name, dn, old_doc_list, new_doc_list)
    
    print("Updated doc list:", updated_doc_list)
@socketio.on('update_supplier_name_google_drive')
def update_supplier_name_google_drive(data):
    print("Received update_multi_doc_google_drive event:")
    print("Data:", data)

    service = authenticate_gdrive()
    update_supplier_name = data.get("updated_supplier")
    print(update_supplier_name)
    rename_supplier_folder(service, update_supplier_name["domain"], update_supplier_name["old_vendor_name"], update_supplier_name["vendor_name"])
    print("update_supplier_name:", update_supplier_name)

def detect_new_emails(interval=60):
    global drive_service, last_page_token, seen_changes
    
    # Initialize Drive service once
    if drive_service is None:
        drive_service = authenticate_gdrive()
        last_page_token = None  # Will get fresh token on first run
    
    last_checked_email_ids = set()
    
    try:
        while True:
            print("\n" + "="*50)
            print("Starting new check cycle...")
            
            # Email checking section
            print("\nChecking for new emails...")
            admin_list = get_all_admin_info()
            
            if admin_list:
                for admin in admin_list:
                    USERNAME = admin["email"]
                    PASSWORD = admin["password"]
                    IMAP_SERVER = admin["server"]
                    try:
                        mail = connect_to_email(USERNAME, PASSWORD, IMAP_SERVER)
                        print(f"Connected to {USERNAME} email server.")
                        
                        emails = fetch_emails(mail)
                        current_email_ids = {email["Message-ID"] for email in emails if "Message-ID" in email}
                        new_email_ids = current_email_ids - last_checked_email_ids
                        
                        if new_email_ids:
                            print(f"Detected {len(new_email_ids)} new email(s) in {USERNAME}.")
                            
                            for email_msg in emails:
                                if email_msg["Message-ID"] in new_email_ids:
                                    subject, sender, body, attachments = extract_email_content(email_msg)
                                    data_attachment = json.dumps(attachments) if isinstance(attachments, list) else attachments
                                    
                                    result = check_new_email(
                                        email_msg["Message-ID"], 
                                        subject, 
                                        sender, 
                                        body, 
                                        data_attachment,
                                        USERNAME,
                                        email_msg["date"]
                                    )
                                    
                                    if result == 1:  # PROCESS_EMAIL
                                        excerpt = body[:30] + '...' if len(body) > 30 else body
                                        socketio.emit("new_email", {
                                            "subject": subject,
                                            "sender": sender,
                                            "body": body,
                                            "attachments": attachments,
                                            "id": email_msg["Message-ID"],
                                            "date": email_msg["date"],
                                            "excerpt": excerpt
                                        })
                                        analysis_email(
                                            subject, 
                                            sender, 
                                            body, 
                                            attachments, 
                                            email_msg["Message-ID"],
                                            USERNAME,
                                            email_msg["date"]
                                        )
                                    else:
                                        print(f"Skipping email {email_msg['Message-ID']}")
                        
                        last_checked_email_ids = current_email_ids
                        mail.logout()
                        
                    except Exception as e:
                        print(f"Error processing {USERNAME} mailbox: {e}")
            
            # Drive checking section
            print("\nChecking for Google Drive changes...")
            print(f"Using page token: {last_page_token}")
            
            drive_results, new_page_token = detect_drive_changes(drive_service, last_page_token)
            
            if new_page_token and new_page_token != last_page_token:
                print(f"New page token received: {new_page_token}")
                last_page_token = new_page_token
            
            if drive_results and drive_results[0]:
                unique_items = list({tuple(item) for item in drive_results if len(item) == 3})
                print(f"Found {len(unique_items)} new Drive items to process")
                
                for item in unique_items:
                    supplier_domain, supplier_name, dn = item
                    if supplier_domain != "Menarini" and supplier_name and dn:
                        google_drive_check_for_new_turn(supplier_domain, supplier_name, dn)
            
            # Wait for next cycle
            print(f"\nCompleted cycle. Waiting {interval} seconds...")
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\nFatal error: {e}")
    finally:
        # Cleanup if needed
        pass

if __name__ == "__main__":
    detect_new_emails(interval=300)  # 5 minute intervals by default