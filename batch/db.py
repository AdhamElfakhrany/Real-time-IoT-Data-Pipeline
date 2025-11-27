"""Database connection and session management for batch ETL (MySQL only)."""
from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Load env variables
from dotenv import load_dotenv
load_dotenv(encoding='utf-8')


def get_database_url() -> str:
    """Construct MySQL database URL from environment variables."""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "iot_data")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "#*kareem123halawa*#")

    # MySQL connection string using pymysql driver
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def create_db_engine():
    """Create SQLAlchemy engine with connection pooling."""
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,  # True if you want query logs
    )
    return engine


# Global engine instance
_engine = None

def get_engine():
    """Get or create the global database engine."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

@contextmanager
def get_db_session():
    """
    Context manager for database sessions with automatic commit/rollback.
    Usage:
        with get_db_session() as session:
            session.execute(...)
    """
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection() -> bool:
    """Test MySQL database connection."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
