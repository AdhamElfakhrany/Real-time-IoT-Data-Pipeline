# Step 5 – Containerized Stack

## 1. Components
- **Kafka/Zookeeper**: Confluent images for quick local messaging.
- **Schema Registry**: optional but included for future Avro/Protobuf support.
- **Generator service**: Dockerized `generator.sensor_generator` producing to Kafka.
- **Stream processor**: Dockerized alerting pipeline.
- **Batch runner**: container capable of running `batch.batch_etl` (mounted `data/`).

## 2. Files
- `infra/docker-compose.yml`: orchestrates all services.
- `infra/dockerfiles/Dockerfile.generator`
- `infra/dockerfiles/Dockerfile.streaming`
- `infra/dockerfiles/Dockerfile.batch`

## 3. Usage
```bash
cd infra
docker compose up --build
```
This boots Kafka stack plus generator + streaming processor. Batch runner can be triggered manually:
```bash
docker compose run --rm batch-runner python -m batch.batch_etl \
  --input data/raw/sensor_log.jsonl \
  --output-dir data/processed
```

## 4. Environment mapping
- Services use container-internal broker `kafka:29092` while host access remains `localhost:9092`.
- `.env` still drives thresholds and topics; override via compose `environment` fields.

## 5. Next enhancements
- Add dashboard container (Streamlit/Grafana) reading `data/processed` or Kafka.
- Persist Kafka data via volumes for durability.
- Integrate alert webhooks (Slack/email) with secrets injected via compose.
