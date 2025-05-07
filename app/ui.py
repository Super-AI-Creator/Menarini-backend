import threading
from flask import Blueprint, request, jsonify
import json
from .email_handler import extract_email_content
from .iterative_classifier import iterative_classification
from .po_extraction import extract_po_details
from app.test_email import detect_new_emails
from app.email_handle.google_drive import detect_and_process_uploads
# from flask_cors import CORS
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
stop_event = threading.Event()
from app import socketio 

try:
  # socketio.start_background_task(detect_new_emails)
  thread = threading.Thread(target=detect_new_emails)
  thread.daemon = True
  thread.start()
except KeyboardInterrupt:
    print("Stopping...")
    stop_event.set()
    thread.join()

ui_app = Blueprint("ui", __name__)