from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd1eacbf89c705ef49c1b4ff65d9e1c9a44097b861a589b2d720b13e0f6f89bcb'
app.config['UPLOAD_FOLDER'] = 'tests/sample files'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin requests

# Register blueprints
from app.ui import ui_app
app.register_blueprint(ui_app)

__all__ = [
    "email_handler",
    "file_parser",
    "po_extraction",
    "iterative_classifier",
    "ui",
    "test_email",
    "google_docs_parser"
]