# Sensor Generator

Python CLI that simulates IoT devices and delivers JSON events to stdout, a local file, or a Kafka topic.

## Usage
```bash
python -m generator.sensor_generator --sink file --output data/raw/sensor_log.jsonl
```

### Common Flags
- `--sink [stdout|file|kafka]`: destination for the generated events (`file` by default).
- `--output <path>`: custom file path when using the file sink.
- `--kafka-broker <host:port>` / `--kafka-topic <name>`: override `.env` settings when producing to Kafka.
- `--interval <seconds>`: delay between two consecutive messages (defaults to `GEN_INTERVAL_SECONDS`).
- `--max-events <N>`: stop after `N` events (helpful for tests).
- `--seed <value>`: seed RNG for reproducible datasets.

## Environment Variables
Values come from `.env` (see `.env.example`). Key ones for this module:
- `GEN_INTERVAL_SECONDS`
- `GEN_DEVICE_COUNT`
- `TEMP_RANGE`
- `HUMIDITY_RANGE`
- `RAW_DATA_PATH`
- `KAFKA_BROKER`, `KAFKA_RAW_TOPIC`

## Example Workflows
1. **Smoke test to console**
   ```bash
   python -m generator.sensor_generator --sink stdout --max-events 3
   ```
2. **Write to rolling file**
   ```bash
   python -m generator.sensor_generator --sink file --output data/raw/devices.jsonl
   ```
3. **Produce to Kafka**
   ```bash
   python -m generator.sensor_generator --sink kafka --kafka-broker localhost:9092 --kafka-topic iot.raw
   ```

## Next Steps
Feed the generated events into the streaming processor or batch ETL modules as outlined in the project roadmap.
