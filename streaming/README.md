# Streaming Processor

Kafka consumer/producer that performs real-time anomaly detection on sensor events.

## Requirements
- Kafka cluster reachable via `KAFKA_BROKER`.
- Topics in `.env`: `KAFKA_RAW_TOPIC`, `KAFKA_PROCESSED_TOPIC`, `KAFKA_ALERT_TOPIC` (optional).
- Optional HTTP webhook for alerts via `ALERT_WEBHOOK_URL`.

## Run locally
```bash
python -m streaming.stream_processor
```

Environment variables (via `.env`):
- `STREAMING_GROUP_ID`
- `STREAMING_AUTO_OFFSET`
- `STREAMING_POLL_TIMEOUT_MS`
- `STREAMING_BATCH_SIZE`
- Thresholds inherited from generator (`TEMP_ALERT_THRESHOLD`, `HUMIDITY_ALERT_THRESHOLD`).

## Behavior
1. Consume JSON payloads from the raw topic.
2. Flag events that exceed thresholds.
3. Publish enriched events to the processed topic.
4. Emit alerts to Kafka `KAFKA_ALERT_TOPIC` and/or HTTP webhook.
5. Route failures to `KAFKA_DLQ_TOPIC` if defined.

## Next steps
- Deploy via Airflow/Spark Streaming job for scale.
- Integrate with notification channels (Slack, email, SMS).
