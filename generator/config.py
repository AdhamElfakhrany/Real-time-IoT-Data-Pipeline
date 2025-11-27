"""Configuration helpers for the IoT sensor generator."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple
import os

from dotenv import load_dotenv


try:
    load_dotenv(encoding='latin-1')
except Exception:
    try:
        load_dotenv(encoding='utf-8')
    except Exception:
        pass


def _parse_float_range(raw: str | None, fallback: Tuple[float, float]) -> Tuple[float, float]:
    if not raw:
        return fallback
    try:
        low, high = [float(part.strip()) for part in raw.split(",", maxsplit=1)]
    except (ValueError, AttributeError):
        return fallback
    if low >= high:
        return fallback
    return low, high


@dataclass(frozen=True)
class GeneratorConfig:
    interval_seconds: float = float(os.getenv("GEN_INTERVAL_SECONDS", "5"))
    device_count: int = int(os.getenv("GEN_DEVICE_COUNT", "10"))
    temp_range: Tuple[float, float] = _parse_float_range(os.getenv("TEMP_RANGE"), (20.0, 55.0))
    humidity_range: Tuple[float, float] = _parse_float_range(os.getenv("HUMIDITY_RANGE"), (20.0, 90.0))
    raw_data_path: Path = Path(os.getenv("RAW_DATA_PATH", "data/raw"))
    kafka_broker: str | None = os.getenv("KAFKA_BROKER")
    kafka_topic: str = os.getenv("KAFKA_RAW_TOPIC", "iot.raw")
    kafka_security: str | None = os.getenv("KAFKA_SECURITY_PROTOCOL")
    alert_log_path: str | None = os.getenv("ALERT_LOG_PATH")

    @classmethod
    def from_env(cls) -> "GeneratorConfig":
        return cls()


@dataclass(frozen=True)
class Thresholds:
    temp_alert: float = float(os.getenv("TEMP_ALERT_THRESHOLD", "50"))
    humidity_alert: float = float(os.getenv("HUMIDITY_ALERT_THRESHOLD", "25"))

    @classmethod
    def from_env(cls) -> "Thresholds":
        return cls()