"""Configuration for the streaming processor."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


try:
    load_dotenv(encoding='latin-1')
except Exception:
    try:
        load_dotenv(encoding='utf-8')
    except Exception:
        pass


@dataclass(frozen=True)
class StreamingConfig:
    kafka_broker: str = os.getenv("KAFKA_BROKER", "localhost:9092")
    raw_topic: str = os.getenv("KAFKA_RAW_TOPIC", "iot.raw")
    processed_topic: str = os.getenv("KAFKA_PROCESSED_TOPIC", "iot.processed")
    alert_topic: Optional[str] = os.getenv("KAFKA_ALERT_TOPIC", "iot.alerts")
    group_id: str = os.getenv("STREAMING_GROUP_ID", "stream-processor")
    auto_offset_reset: str = os.getenv("STREAMING_AUTO_OFFSET", "latest")
    alert_webhook: Optional[str] = os.getenv("ALERT_WEBHOOK_URL")
    alert_slack_webhook: Optional[str] = os.getenv("ALERT_SLACK_WEBHOOK_URL")
    alert_log_path: Optional[str] = os.getenv("ALERT_LOG_PATH")
    dead_letter_topic: Optional[str] = os.getenv("KAFKA_DLQ_TOPIC")
    poll_timeout_ms: int = int(os.getenv("STREAMING_POLL_TIMEOUT_MS", "1000"))
    batch_size: int = int(os.getenv("STREAMING_BATCH_SIZE", "100"))

    @classmethod
    def from_env(cls) -> "StreamingConfig":
        return cls()