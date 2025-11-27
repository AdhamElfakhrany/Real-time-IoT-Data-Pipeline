"""Database migration script - creates all required tables (MySQL/Docker)."""
from __future__ import annotations

import logging
import argparse

from batch.db import get_engine, test_connection
from batch.models import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("migrate")


def create_tables() -> None:
    """Create all tables defined in models."""
    logger.info("Testing database connection...")
    if not test_connection():
        raise RuntimeError("Cannot connect to database. Check your DB_* environment variables.")
    
    logger.info("Database connection successful!")
    
    engine = get_engine()
    logger.info("Creating tables...")
    
    Base.metadata.create_all(bind=engine)
    
    logger.info("✓ Tables created successfully: raw_events, cleaned_events, hourly_aggregates")


def drop_tables() -> None:
    """Drop all tables (use with caution!)."""
    logger.warning("Dropping all tables... (This will delete all data!)")
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    logger.info("✓ Tables dropped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables before creating (WARNING: deletes all data)"
    )
    args = parser.parse_args()
    
    if args.drop:
        drop_tables()
    
    create_tables()
