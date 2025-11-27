# SQL-Based Batch ETL Migration - README

## Overview

Your IoT batch ETL pipeline has been successfully migrated from pandas DataFrames to SQL-based processing using MySQL.

## What Changed

###  Files Created
- `batch/db.py` - Database connection and session management
- `batch/models.py` - SQLAlchemy ORM models for tables
- `batch/migrate.py` - Database migration script


### Files Modified
- `batch/batch_etl.py` - Complete refactor to use SQL queries
- `batch/config.py` - Added database configuration
- `requirements.txt` - Added SQLAlchemy and PyMySQL
- `infra/docker-compose.yml` - Added MySQL service

## Architecture

### Database Tables

1. **raw_events** - Stores raw sensor data from JSONL files
2. **cleaned_events** - Cleaned, validated, and enriched sensor data
3. **hourly_aggregates** - Hourly aggregations by device

### ETL Pipeline Flow

```
JSONL File → raw_events table
            ↓
     SQL: Cleanse & Validate  
            ↓
      cleaned_events table
            ↓
     SQL: Enrich with Alerts
            ↓
      Update alert flags
            ↓
     SQL: Hourly Aggregation
            ↓
    hourly_aggregates table
            ↓
    Optional: Export to Parquet/CSV
```

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Start MySQL
cd infra
docker-compose up -d mysql

# Wait for MySQL to be ready (10-15 seconds)

# Install dependencies
cd ..
pip install -r requirements.txt

# Create database tables
python -m batch.migrate

# Run ETL pipeline
python -m batch.batch_etl --preview
```

### Option 2: Using Existing MySQL

Set environment variables:
```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=iot_data
export DB_USER=your_user
export DB_PASSWORD=your_password
```

Then run:
```bash
pip install sqlalchemy pymysql
python -m batch.migrate
python -m batch.batch_etl --input data/raw/sensor_log.jsonl --preview
```

## Command Line Options

```bash
python -m batch.batch_etl --help

Options:
  --input PATH          Path to raw JSONL file
  --output-dir PATH     Directory for processed outputs
  --output-format       parquet or csv
  --preview             Print sample rows to stdout
  --skip-export         Skip exporting to files (data stays in DB)
```

## Database Configuration

Set these environment variables or add to `.env`:

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=iot_data
DB_USER=iot_user
DB_PASSWORD=iot_password
```

## Querying the Data

### Connect to MySQL

```bash
# If using Docker
docker exec -it infra-mysql-1 mysql -uiot_user -piot_password iot_data

# Or use MySQL client
mysql -h localhost -u iot_user -p iot_data
```

### Example Queries

```sql
-- View recent cleaned events
SELECT * FROM cleaned_events 
ORDER BY timestamp DESC 
LIMIT 10;

-- View alerts
SELECT device_id, timestamp, temperature, humidity
FROM cleaned_events 
WHERE is_alert = TRUE
ORDER BY timestamp DESC;

-- View hourly aggregates
SELECT device_id, hour_bucket, 
       temperature_avg, humidity_avg,
       alert_count, event_count
FROM hourly_aggregates
ORDER BY hour_bucket DESC, device_id
LIMIT 20;

-- Get device statistics
SELECT device_id,
       COUNT(*) as total_events,
       SUM(is_alert) as total_alerts,
       AVG(temperature) as avg_temp,
       AVG(humidity) as avg_humidity
FROM cleaned_events
GROUP BY device_id;
```

## Benefits of SQL Migration

✅ **Scalability** - Process millions of rows efficiently  
✅ **Data Quality** - Enforce constraints and validation at database level  
✅ **Query Power** - Use SQL for complex analytics  
✅ **Integration** - Easy integration with BI tools and dashboards  
✅ **Persistence** - Data preserved in database between runs  
✅ **ACID Transactions** - Reliable data processing  

## Troubleshooting

### Port 3306 already in use
MySQL is already running on your system. Either:
- Use the existing MySQL instance
- Stop the existing MySQL service
- Change the port in docker-compose.yml

### Connection refused
- Ensure MySQL is running: `docker-compose ps`
- Check credentials in environment variables
- Wait for MySQL to be healthy (check with `docker-compose logs mysql`)

### Python import errors
```bash
pip install --upgrade sqlalchemy pymysql
```

## Next Steps

- Configure dashboard to read from MySQL instead of parquet files
- Add data retention policies
- Implement incremental loading
- Add more complex analytics queries
- Set up automated batch processing schedule

---

**Note**: The original pandas-based implementation is preserved in git history if you need to reference it.
