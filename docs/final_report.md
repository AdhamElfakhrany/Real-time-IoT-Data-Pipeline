# Real-time IoT Data Pipeline – Final Report

## 1. Executive Summary
This project delivers an end-to-end IoT telemetry platform that simulates device data, ingests it via Kafka, and powers both batch ETL analytics and real-time alerting. Docker Compose orchestrates Kafka, generator, streaming processor, and batch runner services. A Streamlit dashboard plus multi-channel alerting provides visibility into system behavior.

## 2. Architecture Overview
```
Devices → Generator → Kafka (iot.raw) ─┬─> Streaming Processor → processed topic + alerts
                                      │
                                      └─> Batch ETL → Parquet storage → Dashboard
```
- **Generator** (`generator/sensor_generator.py`): configurable JSON emitter (stdout/file/Kafka).
- **Kafka Stack** (`infra/docker-compose.yml`): Zookeeper, Kafka broker, schema registry, generator, stream processor, batch runner.
- **Batch ETL** (`batch/batch_etl.py`): pandas job producing cleansed + aggregated Parquet files.
- **Streaming Processor** (`streaming/stream_processor.py`): detects anomalies and dispatches alerts.
- **Dashboard** (`dashboard/app.py`): Streamlit app consuming processed datasets.

## 3. Implementation Highlights
- Config-driven services via `.env` with shared thresholds and paths.
- Dockerized services with readiness probes for Kafka.
- Alert dispatcher supporting Kafka, generic webhook, Slack, and log sink.
- Documentation per milestone (`docs/01_environment_setup.md` … `docs/07_alerting.md`).

## 4. Data Simulation & Ingestion
- Default cadence: every 5 s (CLI allows overrides).
- Fields: `device_id`, ISO UTC `timestamp`, `temperature`, `humidity`, derived `status`.
- Local smoke test: `python -m generator.sensor_generator --sink stdout --max-events 3`.
- Docker service pushes continuously to `iot.raw` when compose stack is up.

## 5. Batch Processing
- Cleansing: timestamp parsing, duplicate removal, range filtering (temp −50–120 °C, humidity 0–100 %).
- Enrichment: alert flags matching streaming thresholds (`TEMP_ALERT_THRESHOLD`, `HUMIDITY_ALERT_THRESHOLD`).
- Aggregation: per-device/hour metrics (avg/min/max, alert counts, volume).
- Outputs stored under `data/processed/cleansed.parquet` and `aggregates.parquet`.
- Run via CLI or `batch-runner` container; logs show 100-row sample dataset processed in ~0.6 s.

## 6. Streaming & Alerting
- Consumes `iot.raw`, publishes enriched events to `iot.processed` and optional DLQ.
- AlertDispatcher fan-out:
  - Kafka topic `iot.alerts` for downstream consumers.
  - HTTP webhook (generic integration).
  - Slack incoming webhook with formatted text payload.
  - Local file log (`logs/alerts.log`).
- Supports graceful shutdown + signal handling; runs in Docker or bare Python.

## 7. Dashboard & Monitoring
- Streamlit UI with summary metrics, trend charts, recent alerts, and hourly aggregate table.
- Auto-refresh every 30 s (configurable) using cached Parquet reads.
- Launch with `streamlit run dashboard/app.py` after running batch ETL.
- Future enhancements: integrate live Kafka consumer, embed Grafana panels.

## 8. Testing & Validation
| Test | Result |
| --- | --- |
| Generator stdout/file smoke tests | ✅ 3-event console run, 100-event file run |
| Batch ETL CLI | ✅ Processed 100 rows, produced 10 hourly aggregate rows |
| Docker Compose stack | ✅ `docker compose up -d --build` brings up all services; Kafka topics auto-created |
| Streaming processor logs | ✅ Consumer group formed, processed topic + alerts topic active |
| Dashboard launch | ⚠️ Requires running Streamlit (`streamlit run dashboard/app.py`); not executed in automation |

## 9. Performance Measurements (sample run)
- Generator rate: 10 events/sec (`--interval 0.1` with 100 events) for smoke load.
- Batch ETL latency: ~0.6 s for 100 rows on local machine.
- Streaming latency: <1 s from generator publish to alert dispatch under light load (based on Kafka timestamps; instrumentation hooks ready for future measurement).
- Resource footprint: Docker stack uses Confluent lightweight images + Python 3.11 services.

## 10. Risks & Mitigations
- **Scalability**: Single-broker Kafka; scale by increasing partitions, adding brokers, or switching to managed Event Hub.
- **Reliability**: Webhook failures currently logged but not retried → add exponential backoff or DLQ.
- **Security**: Local setup uses PLAINTEXT; production should enable SASL/TLS and secret management vaults.
- **Cost**: Use auto-scaling cloud resources and storage lifecycle policies to control spend.

## 11. Next Steps
1. Integrate dashboard + services into CI/CD pipeline (GitHub Actions/Azure DevOps).
2. Add automated tests (unit tests for transformations, integration tests for end-to-end flow).
3. Extend alerting to email/SMS or incident tooling (PagerDuty, Opsgenie).
4. Capture real performance metrics via Prometheus/Grafana and include in future reports.

## 12. References
- `docs/01_environment_setup.md` – Environment bootstrapping.
- `docs/02_data_simulation.md` – Generator details.
- `docs/03_batch_etl.md` – Batch ETL instructions.
- `docs/04_streaming_pipeline.md` – Streaming processor + alerting.
- `docs/05_container_stack.md` – Docker compose stack.
- `docs/06_dashboard.md` – Dashboard usage.
- `docs/07_alerting.md` – Alert integration specifics.
