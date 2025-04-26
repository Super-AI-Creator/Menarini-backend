import sys
import os
from app import app, socketio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

if __name__ == "__main__":
    socketio.run(app,
                 debug=True,
                 use_reloader=False,
                 allow_unsafe_werkzeug=True)  # For development only