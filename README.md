# Real-time IoT Data Pipeline

Comprehensive, end-to-end project that simulates IoT sensor telemetry, ingests it into streaming infrastructure, and powers both batch ETL analytics and real-time alerting with dashboards.

## Project Goals
- Generate realistic IoT sensor messages (temperature, humidity, status) at configurable intervals.
- Ingest raw events into Kafka (or equivalent) for both streaming and batch consumers.
- Build a structured batch ETL flow that produces curated aggregates (Parquet/SQL).
- Implement a low-latency streaming processor that fires alerts on threshold violations.
- Provide monitoring & dashboards plus a final report summarizing performance.

## Repository Layout
```
.
├── batch/              # Batch ETL scripts (pandas / PySpark)
├── dashboard/          # Streamlit / Grafana configs and assets
├── data/
│   ├── processed/      # Processed outputs (gitignored)
│   └── raw/            # Landing zone for raw dumps (gitignored)
├── docs/               # Architecture diagrams, final report
├── generator/          # Sensor data generator + utilities
├── infra/              # Docker Compose, IaC, orchestration manifests
├── streaming/          # Streaming jobs (Spark/Flink/ASA)
├── .env.example        # Template for secrets & config
├── requirements.txt    # Python dependencies for core services
└── README.md           # You are here
```

## Step 1 – Environment Setup
1. **Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. **Copy environment template**
   ```bash
   cp .env.example .env
   # populate broker endpoints, thresholds, alert targets
   ```
3. **Local infrastructure** (optional for now)
   - Install Docker Desktop.
   - Ensure ports 9092 (Kafka) and 2181 (Zookeeper) are available.

## Next Steps
- **Milestone 1** ✔️ `generator/sensor_generator.py` and ingestion targets (stdout/file/Kafka).
- **Milestone 2** ✔️ pandas batch ETL (`batch/batch_etl.py`) producing cleansed + aggregated datasets.
- **Milestone 3** 🚧 streaming processor + alerting sink (`streaming/stream_processor.py`) and Docker stack (`infra/docker-compose.yml`).
- **Milestone 4** 🚧 dashboard (`streamlit run dashboard/app.py`) and final report in `docs/`.

Each milestone will be captured in dedicated documentation inside `docs/` along with testing artifacts.
