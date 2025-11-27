# Step 2 – Data Simulation & Ingestion

This milestone delivers the IoT sensor generator and the first ingestion targets (file/stdout/Kafka).

## 1. Objectives
- Produce realistic telemetry: timestamp, device id, temperature, humidity, status.
- Emit events every *N* seconds (default 5s) for any number of devices.
- Support multiple sinks so the same generator powers both streaming and batch paths.

## 2. Implementation Highlights
- Module: `generator/sensor_generator.py` with CLI flags for sink, interval, seed, and event cap.
- Configuration: `generator/config.py` loads `.env` values (interval, device count, ranges, Kafka endpoints).
- Sinks supported:
  - **stdout**: quick inspection/debugging.
  - **file**: appends JSON Lines to `data/raw/sensor_log.jsonl` (default).
  - **Kafka**: produces to `KAFKA_RAW_TOPIC` via `kafka-python`.
- Alert status logic toggles to `ALERT` whenever `temperature >= TEMP_ALERT_THRESHOLD` or `humidity <= HUMIDITY_ALERT_THRESHOLD`.

## 3. Running the Generator
```bash
python -m generator.sensor_generator --sink file --output data/raw/devices.jsonl
```
Optional parameters:
- `--max-events 100`: stop after 100 records.
- `--kafka-broker host:port`: override `.env` when testing remote brokers.
- `--seed 42`: deterministic stream for unit tests.

## 4. Validating Output
- Inspect sample lines: `head data/raw/devices.jsonl`.
- Quick schema check:
  ```bash
  python - <<'PY'
  import json
  from itertools import islice
  with open('data/raw/devices.jsonl') as fh:
      for line in islice(fh, 3):
          print(json.loads(line))
  PY
  ```
- Kafka consumers (e.g., `kafka-console-consumer`) can confirm publishing.

## 5. Next Up
Proceed to **Step 3 – Batch ETL**: ingest the raw JSON Lines (or Kafka dump) into pandas/PySpark, clean them, and store curated aggregates under `data/processed/` or the target warehouse.
