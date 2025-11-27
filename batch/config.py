"""Configuration helpers for batch ETL jobs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env only once (cleaner)
load_dotenv()

@dataclass(frozen=True)
class BatchConfig:
    # Paths
    input_path: Path = Path(os.getenv("BATCH_INPUT_PATH", "data/raw/sensor_log.jsonl"))
    output_dir: Path = Path(os.getenv("PROCESSED_DATA_PATH", "data/processed"))

    # Output filenames
    aggregates_filename: str = os.getenv("BATCH_AGG_FILENAME", "aggregates.parquet")
    cleansed_filename: str = os.getenv("BATCH_CLEANSED_FILENAME", "cleansed.parquet")

    # Validation ranges
    temp_range: tuple[float, float] = (
        float(os.getenv("TEMP_MIN", "-50")),
        float(os.getenv("TEMP_MAX", "120")),
    )
    humidity_range: tuple[float, float] = (
        float(os.getenv("HUMIDITY_MIN", "0")),
        float(os.getenv("HUMIDITY_MAX", "100")),
    )

    # Database (MySQL only)
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "iot_data")
    db_user: str = os.getenv("DB_USER", "iot_user")
    db_password: str = os.getenv("DB_PASSWORD", "iot_password")

    # Kafka (optional)
    use_kafka: bool = os.getenv("USE_KAFKA", "false").lower() == "true"
    kafka_bootstrap: str = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "sensor_events")

    def aggregates_path(self) -> Path:
        return self.output_dir / self.aggregates_filename

    def cleansed_path(self) -> Path:
        return self.output_dir / self.cleansed_filename

    @classmethod
    def from_env(cls) -> "BatchConfig":
        cfg = cls()
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        return cfg

