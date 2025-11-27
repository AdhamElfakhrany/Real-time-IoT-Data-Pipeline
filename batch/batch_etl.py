"""Batch ETL job for IoT sensor data using SQL."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from io import StringIO

import pandas as pd
from sqlalchemy import text

from batch.config import BatchConfig
from batch.db import get_engine, get_db_session
from batch.models import RawEvent
from generator.config import Thresholds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("batch-etl")


def load_raw_to_db(path: Path, encoding: str = "utf-8") -> int:
    """Load raw JSONL file into raw_events table, preserving legacy encodings."""
    if not path.exists():
        raise FileNotFoundError(f"Input file {path} not found")

    logger.info("Loading raw events from %s into database", path)

    df = pd.read_json(path, lines=True, encoding=encoding)
    logger.info("Read %d raw events from file", len(df))

    raw_events = []
    for _, row in df.iterrows():
        ts = pd.to_datetime(row.get('timestamp'), errors='coerce', utc=True)
        ts = ts.to_pydatetime().replace(tzinfo=None) if pd.notna(ts) else None

        raw_events.append(
            RawEvent(
                device_id=str(row.get("device_id")) if pd.notna(row.get("device_id")) else None,
                timestamp=ts,
                temperature=float(row.get("temperature")) if pd.notna(row.get("temperature")) else None,
                humidity=float(row.get("humidity")) if pd.notna(row.get("humidity")) else None,
                status=str(row.get("status")) if pd.notna(row.get("status")) else None,
            )
        )

    with get_db_session() as session:
        # Clear old data before insert
        session.execute(text("DELETE FROM raw_events"))
        session.commit()

        # Bulk insert
        session.add_all(raw_events)
        session.commit()

    logger.info("✓ Loaded %d raw events into database", len(raw_events))
    return len(raw_events)


def cleanse_data(cfg: BatchConfig) -> int:
    """Clean raw data and insert into cleaned_events, preserving DISTINCT rows."""
    logger.info("Cleansing data with SQL...")

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM cleaned_events"))

        # Use DISTINCT to avoid duplicates
        conn.execute(text("""
            INSERT INTO cleaned_events
                (device_id, timestamp, temperature, humidity, status,
                 is_temp_alert, is_humidity_alert, is_alert, created_at)
            SELECT DISTINCT
                device_id,
                timestamp,
                temperature,
                humidity,
                status,
                FALSE,
                FALSE,
                FALSE,
                CURRENT_TIMESTAMP
            FROM raw_events
            WHERE device_id IS NOT NULL
              AND timestamp IS NOT NULL
              AND temperature BETWEEN :temp_low AND :temp_high
              AND humidity BETWEEN :hum_low AND :hum_high
        """), {
            "temp_low": cfg.temp_range[0],
            "temp_high": cfg.temp_range[1],
            "hum_low": cfg.humidity_range[0],
            "hum_high": cfg.humidity_range[1],
        })

        count = conn.execute(text("SELECT COUNT(*) FROM cleaned_events")).scalar()

    logger.info("✓ Cleansed %d rows into cleaned_events table", count)
    return count


def enrich_anomalies(thresholds: Thresholds) -> int:
    """Set anomaly flags based on thresholds."""
    logger.info("Enriching data with anomaly flags...")

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE cleaned_events
            SET 
                is_temp_alert = (temperature >= :temp_threshold),
                is_humidity_alert = (humidity <= :humidity_threshold),
                is_alert = (temperature >= :temp_threshold 
                            OR humidity <= :humidity_threshold)
        """), {
            "temp_threshold": thresholds.temp_alert,
            "humidity_threshold": thresholds.humidity_alert,
        })

        alert_count = conn.execute(text(
            "SELECT COUNT(*) FROM cleaned_events WHERE is_alert = TRUE"
        )).scalar()

    logger.info("✓ Found %d rows with alerts", alert_count)
    return alert_count


def aggregate_hourly() -> int:
    """Aggregate readings by device per hour, with ORDER BY for readability."""
    logger.info("Creating hourly aggregates...")

    engine = get_engine()

    hour_expr = "DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00')"  # MySQL only

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM hourly_aggregates"))

        conn.execute(text(f"""
            INSERT INTO hourly_aggregates
                (device_id, hour_bucket,
                 temperature_avg, temperature_max, temperature_min,
                 humidity_avg, humidity_max, humidity_min,
                 alert_count, event_count, created_at)
            SELECT
                device_id,
                {hour_expr} AS hour_bucket,
                AVG(temperature),
                MAX(temperature),
                MIN(temperature),
                AVG(humidity),
                MAX(humidity),
                MIN(humidity),
                SUM(CASE WHEN is_alert THEN 1 ELSE 0 END),
                COUNT(*),
                CURRENT_TIMESTAMP
            FROM cleaned_events
            GROUP BY device_id, {hour_expr}
            ORDER BY device_id, hour_bucket
        """))

        count = conn.execute(
            text("SELECT COUNT(*) FROM hourly_aggregates")
        ).scalar()

    logger.info("✓ Created %d hourly aggregates", count)
    return count


def export_to_files(output_dir: Path, output_format: str) -> None:
    """Export cleaned_events and hourly_aggregates to Parquet/CSV files."""
    logger.info("Exporting data to %s files...", output_format)

    engine = get_engine()

    cleaned_df = pd.read_sql("SELECT * FROM cleaned_events ORDER BY device_id, timestamp", engine)
    cleansed_path = output_dir / f"cleansed.{output_format}"

    if output_format == "parquet":
        cleaned_df.to_parquet(cleansed_path, index=False)
    else:
        cleaned_df.to_csv(cleansed_path, index=False)

    logger.info("✓ Exported %d cleaned events to %s", len(cleaned_df), cleansed_path)

    agg_df = pd.read_sql("SELECT * FROM hourly_aggregates ORDER BY device_id, hour_bucket", engine)
    agg_path = output_dir / f"aggregates.{output_format}"

    if output_format == "parquet":
        agg_df.to_parquet(agg_path, index=False)
    else:
        agg_df.to_csv(agg_path, index=False)

    logger.info("✓ Exported %d aggregates to %s", len(agg_df), agg_path)


def preview_results() -> None:
    """Print sample data from cleaned_events and hourly_aggregates."""
    engine = get_engine()

    print("\n" + "="*80)
    print("CLEANED EVENTS SAMPLE (First 10 rows)")
    print("="*80)
    df = pd.read_sql("SELECT * FROM cleaned_events ORDER BY timestamp DESC LIMIT 10", engine)
    print(df.to_string(index=False))

    print("\n" + "="*80)
    print("HOURLY AGGREGATES SAMPLE (First 10 rows)")
    print("="*80)
    df = pd.read_sql("SELECT * FROM hourly_aggregates ORDER BY hour_bucket DESC LIMIT 10", engine)
    print(df.to_string(index=False))
    print("="*80 + "\n")


def parse_args(cfg: BatchConfig) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SQL-based Batch ETL for IoT sensor data")
    parser.add_argument("--input", type=Path, default=cfg.input_path, help="Path to raw JSONL file")
    parser.add_argument("--output-dir", type=Path, default=cfg.output_dir, help="Directory for processed outputs")
    parser.add_argument("--output-format", choices=["parquet", "csv"], default="parquet")
    parser.add_argument("--preview", action="store_true", help="Print sample rows to stdout")
    parser.add_argument("--skip-export", action="store_true", help="Skip exporting to files (data stays in DB)")
    return parser.parse_args()


def main() -> None:
    cfg = BatchConfig.from_env()
    args = parse_args(cfg)
    thresholds = Thresholds.from_env()

    logger.info("="*80)
    logger.info("SQL-BASED BATCH ETL PIPELINE")
    logger.info("="*80)

    load_raw_to_db(args.input, encoding="latin-1")
    cleanse_data(cfg)
    enrich_anomalies(thresholds)
    aggregate_hourly()

    if not args.skip_export:
        export_to_files(args.output_dir, args.output_format)

    if args.preview:
        preview_results()

    logger.info("="*80)
    logger.info("✓ ETL PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("="*80)


if __name__ == "__main__":
    main()
