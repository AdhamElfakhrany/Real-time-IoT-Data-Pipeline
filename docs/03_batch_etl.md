# Step 3 – Batch ETL

This milestone introduces the batch processing flow that cleans, enriches, and aggregates the raw IoT telemetry into curated datasets.

## 1. Objectives
- Transform JSON Lines raw dumps into analytically ready tables.
- Standardize timestamps, enforce schema, and remove invalid readings.
- Compute per-device/hour metrics to feed dashboards and periodic reporting.

## 2. Implementation Overview
- Module: `batch/batch_etl.py` (pandas-based CLI job).
- Config: `batch/config.py` defines default input/output paths plus valid value ranges.
- Stages:
  1. **Read** raw JSONL file (`--input` flag, defaults to `data/raw/sensor_log.jsonl`).
  2. **Cleanse** rows: parse timestamps, drop nulls/duplicates, filter out-of-range temperature/humidity values.
  3. **Enrich** rows with alert flags (uses the same thresholds as the generator).
  4. **Aggregate** metrics per `device_id + hour_bucket` (avg/min/max, event counts, alert counts).
  5. **Load** outputs as Parquet (default) or CSV into `data/processed/`.

## 3. Running the Job
```bash
python -m batch.batch_etl --input data/raw/sensor_log.jsonl --output-dir data/processed --output-format parquet --preview
```
Flags:
- `--output-format csv` to write CSV.
- `--preview` prints a small sample of both cleansed rows and aggregates.

## 4. Output Files
- `data/processed/cleansed.parquet`: row-level dataset with alert flags.
- `data/processed/aggregates.parquet`: per-device/hour metrics.

## 5. Validation Checklist
- Confirm schemas with `parquet-tools` or pandas `read_parquet`.
- Spot-check aggregated values for a few devices/hours.
- Compare alert counts with expectations from the generator thresholds.

## 6. Next Steps
- Orchestrate this script via cron/Airflow/ADF.
- Feed the aggregates into the dashboard data source.
- Parallel development: Streaming pipeline (Milestone 3).
