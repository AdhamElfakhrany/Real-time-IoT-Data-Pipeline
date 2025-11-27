# Step 4 – Streaming Pipeline & Alerts

## 1. Objectives
- Process sensor telemetry in real time.
- Detect threshold breaches immediately and fan out alerts.
- Keep a processed topic/table synchronized for dashboards and analytics.

## 2. Architecture
```
Generator → Kafka topic (`iot.raw`) → Streaming processor →
    ├── Kafka processed topic (`iot.processed`)
    ├── Kafka alerts topic (`iot.alerts`)
    ├── Slack / HTTP Webhooks
    └── Local alert log
```

## 3. Implementation Highlights
- Module: `streaming/stream_processor.py`.
- Alert dispatching handled by `streaming/alerting.py` supporting Kafka topic, generic webhook, Slack, and file logging.
- Config: `streaming/config.py` loads Kafka broker/topics, consumer group, webhook settings.
- Uses `kafka-python` to consume from raw topic, enrich messages, and publish to processed + alert sinks.
- Alert payloads include device ID, timestamp, readings, and reason codes (`temperature_high`, `humidity_low`).
- Optional dead-letter topic for unhandled failures.

## 4. Running Locally
```bash
python -m streaming.stream_processor
```
Prerequisites:
- Kafka broker available at `KAFKA_BROKER`.
- Topics created (`iot.raw`, `iot.processed`, `iot.alerts`).
- `.env` configured with thresholds and optional webhook/log URLs (`ALERT_WEBHOOK_URL`, `ALERT_SLACK_WEBHOOK_URL`, `ALERT_LOG_PATH`).

## 5. Validation Checklist
- Start generator and processor; confirm processed topic receives enriched messages (e.g., `kafka-console-consumer`).
- Trigger alerts by increasing generator temperature range; verify `iot.alerts` messages, log file content, and Slack/webhook deliveries.
- Monitor consumer lag and retry behavior under load.

## 6. Next Steps
- Package processor into Docker + docker-compose (already available under `infra/`).
- Add observability (metrics, dashboards for lag/throughput).
- Integrate with downstream alert channels (email/SMS) or incident management tools.
