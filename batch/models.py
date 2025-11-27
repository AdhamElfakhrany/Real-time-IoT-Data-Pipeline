"""SQLAlchemy ORM models for IoT sensor data."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RawEvent(Base):
    """Raw sensor events as ingested from JSONL files."""
    
    __tablename__ = "raw_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    status = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_raw_device_ts", "device_id", "timestamp"),
    )


class CleanedEvent(Base):
    """Cleaned and enriched sensor events."""
    
    __tablename__ = "cleaned_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)
    is_temp_alert = Column(Boolean, default=False, nullable=False)
    is_humidity_alert = Column(Boolean, default=False, nullable=False)
    is_alert = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_cleaned_device_ts", "device_id", "timestamp"),
        Index("idx_cleaned_alert", "is_alert", "timestamp"),
    )


class HourlyAggregate(Base):
    """Hourly aggregated metrics by device."""
    
    __tablename__ = "hourly_aggregates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), nullable=False)
    hour_bucket = Column(DateTime, nullable=False)
    temperature_avg = Column(Float, nullable=False)
    temperature_max = Column(Float, nullable=False)
    temperature_min = Column(Float, nullable=False)
    humidity_avg = Column(Float, nullable=False)
    humidity_max = Column(Float, nullable=False)
    humidity_min = Column(Float, nullable=False)
    alert_count = Column(Integer, default=0, nullable=False)
    event_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_hourly_device_bucket", "device_id", "hour_bucket", unique=True),
        Index("idx_hourly_bucket", "hour_bucket"),
    )
