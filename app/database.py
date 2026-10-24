"""
Database configuration and session management for StudentHub.
Supports SQLite with persistent storage and configurable connection URL.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env if present
load_dotenv()

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database URL configuration
# On Vercel Serverless, the root filesystem is read-only, so SQLite must reside in /tmp
if os.getenv("VERCEL") == "1":
    DEFAULT_DB_PATH = Path("/tmp/students.db")
else:
    DEFAULT_DB_PATH = BASE_DIR / "students.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# SQLite requires specific connect args for multi-threaded FastAPI apps
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency yielding a database session per request.
    Ensures sessions are closed reliably after each request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
