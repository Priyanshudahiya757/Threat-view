import sys
import os

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import create_app, db
from services.seed_service import seed_if_empty

app = create_app(os.environ.get("FLASK_ENV", "production"))

# Initialize database tables on cold start if needed
with app.app_context():
    try:
        db.create_all()
        seed_if_empty()
    except Exception as e:
        print("Vercel DB initialization note:", e)
