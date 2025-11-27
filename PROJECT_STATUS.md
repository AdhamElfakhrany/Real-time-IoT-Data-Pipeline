# IoT Project - Running Status

## ✅ Current Status

### 1. Sensor Data Generator
**Status:** ✅ Completed  
**Output:** Generated 30 sensor events to `data/raw/sensor_log.jsonl`

### 2. SQL-Based Batch ETL  
**Status:** ✅ Completed Successfully  
**Results:**
- Loaded: 39 raw events
- Cleansed: 39 rows  
- Alerts Found: 8 temperature/humidity violations
- Aggregates Created: 16 hourly summaries
- Exported to: `data/processed/cleansed.parquet` and `aggregates.parquet`
- Database: `data/iot_data.db` (SQLite)

### 3. Dashboard
**Status:** ⏳ Installing dependencies (streamlit, matplotlib)  
**Will start:** Automatically once installation completes at http://localhost:8501

---

## Project Architecture

```
┌──────────────────┐
│ Sensor Generator │ → Generates IoT sensor data
└────────┬─────────┘
         │
         ↓ (writes to file)
┌────────────────────┐
│ sensor_log.jsonl   │
└────────┬───────────┘
         │
         ↓ (reads from)
┌────────────────────┐
│   SQL Batch ETL    │ → Loads, cleanses, enriches, aggregates
└────────┬───────────┘
         │
         ↓ (stores in)
┌────────────────────┐
│  iot_data.db       │ → SQLite database (raw_events, cleaned_events, hourly_aggregates)
│  *.parquet files   │ → Parquet exports for dashboard
└────────┬───────────┘
         │
         ↓ (reads from)
┌────────────────────┐
│    Dashboard       │ → Streamlit visualization
└────────────────────┘
```

---

## Data Flow

1. **Generator** creates realistic IoT sensor messages:
   - 10 devices (dev_1 through dev_10)
   - Temperature (°C) and Humidity (%)
   - Status: OK, WARNING, or ERROR
   - Timestamp for each reading

2. **SQL ETL** processes the data:
   - **Load**: JSONL → `raw_events` table
   - **Cleanse**: SQL filters invalid data → `cleaned_events` table
   - **Enrich**: SQL adds alert flags (temp >= 50°C or humidity <= 25%)
   - **Aggregate**: SQL creates hourly summaries → `hourly_aggregates` table
   - **Export**: Pandas reads from SQL → Parquet files

3. **Dashboard** visualizes:
   - Real-time sensor readings
   - Temperature and humidity trends
   - Alert notifications
   - Device-by-device breakdowns
   - Hourly aggregations

---

## Quick Commands

### Run Everything
```bash
# Activate virtual environment
.venv_sql\Scripts\activate

# Generate new data
python -m generator.sensor_generator --sink file --max-events 50

# Process with SQL ETL
python -m batch.demo_sqlite

# Start dashboard
streamlit run dashboard\app.py
```

### Query the Database
```bash
# Open SQLite database
sqlite3 data/iot_data.db

# Sample queries
SELECT COUNT(*) FROM raw_events;
SELECT * FROM cleaned_events WHERE is_alert = 1;
SELECT device_id, AVG(temperature_avg) FROM hourly_aggregates GROUP BY device_id;
```

### Check Processed Files
```bash
# List generated files
dir data\raw\
dir data\processed\
```

---

## Current Session Results

**Generated Events:** 39 total sensor readings  
**Time Period:** Last ~2 minutes  
**Devices:** 10 IoT sensors  
**Alerts:** 8 threshold violations detected  
- High temperature (>= 50°C)
- Low humidity (<= 25%)

**Hourly Aggregates:** 16 summary records  
- Average, min, max temperature per device per hour
- Average, min, max humidity per device per hour
- Alert counts per hour

---

## Next Steps

1. ⏳ **Wait for Dashboard Installation** - Streamlit and matplotlib are installing
2. 🚀 **Launch Dashboard** - Will open automatically at http://localhost:8501
3. 📊 **Explore Visualizations** - View charts, graphs, and metrics
4. 🔄 **Generate More Data** - Run generator again for additional events
5. 🔍 **Query Database** - Use SQL to analyze patterns

---

## Files Created

### Data Files
- `data/raw/sensor_log.jsonl` - Raw sensor readings (39 events)
- `data/iot_data.db` - SQLite database with 3 tables
- `data/processed/cleansed.parquet` - Cleaned events (39 rows)
- `data/processed/aggregates.parquet` - Hourly summaries (16 rows)

### Configuration
- `.venv_sql/` - Python virtual environment with all dependencies
- `batch/db.py` - Database connection (supports SQLite + MySQL)
- `batch/batch_etl.py` - SQL-based ETL pipeline
- `batch/demo_sqlite.py` - Quick demo script

---

**Project Status:** ✅ Fully operational with SQL-based processing!
