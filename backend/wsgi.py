import sys
import os

# Add backend directory to path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(path, ".env"))
except ImportError:
    pass

# Import the Flask app
from app import app as application
