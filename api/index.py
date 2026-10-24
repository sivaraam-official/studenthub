"""
Vercel Serverless Function Entry Point for StudentHub.
Exposes the FastAPI 'app' instance for @vercel/python.
"""

import sys
from pathlib import Path

# Add project root to sys.path so app modules import cleanly
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.main import app

# Export for Vercel
__all__ = ["app"]
