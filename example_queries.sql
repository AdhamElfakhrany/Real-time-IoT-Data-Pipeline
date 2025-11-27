-- IoT Data Analysis Queries
-- Database: data/iot_data.db
-- Tables: raw_events, cleaned_events, hourly_aggregates

-- ============================================================================
-- BASIC EXPLORATION
-- ============================================================================

-- 1. Count records in each table
SELECT 'raw_events' as table_name, COUNT(*) as row_count FROM raw_events
UNION ALL
SELECT 'cleaned_events', COUNT(*) FROM cleaned_events
UNION ALL
SELECT 'hourly_aggregates', COUNT(*) FROM hourly_aggregates;

-- 2. View all cleaned events (most recent first)
SELECT * FROM cleaned_events 
ORDER BY timestamp DESC 
LIMIT 10;

-- 3. View hourly aggregates
SELECT * FROM hourly_aggregates
ORDER BY hour_bucket DESC, device_id
LIMIT 10;

-- ============================================================================
-- ALERTS & ANOMALIES
-- ============================================================================

-- 4. View all alerts
SELECT device_id, timestamp, temperature, humidity, 
       is_temp_alert, is_humidity_alert
FROM cleaned_events 
WHERE is_alert = 1
ORDER BY timestamp DESC;

-- 5. Count alerts by device
SELECT device_id, 
       COUNT(*) as total_events,
       SUM(is_alert) as alert_count,
       ROUND(100.0 * SUM(is_alert) / COUNT(*), 2) as alert_percentage
FROM cleaned_events
GROUP BY device_id
ORDER BY alert_count DESC;

-- 6. Temperature alerts only
SELECT device_id, timestamp, temperature
FROM cleaned_events
WHERE is_temp_alert = 1
ORDER BY temperature DESC;

-- 7. Humidity alerts only
SELECT device_id, timestamp, humidity
FROM cleaned_events
WHERE is_humidity_alert = 1
ORDER BY humidity ASC;

-- ============================================================================
-- DEVICE STATISTICS
-- ============================================================================

-- 8. Average temperature and humidity per device
SELECT device_id,
       COUNT(*) as readings,
       ROUND(AVG(temperature), 2) as avg_temp,
       ROUND(MIN(temperature), 2) as min_temp,
       ROUND(MAX(temperature), 2) as max_temp,
       ROUND(AVG(humidity), 2) as avg_humidity,
       ROUND(MIN(humidity), 2) as min_humidity,
       ROUND(MAX(humidity), 2) as max_humidity
FROM cleaned_events
GROUP BY device_id
ORDER BY device_id;

-- 9. Find hottest and coldest devices
SELECT device_id, 
       ROUND(AVG(temperature), 2) as avg_temp
FROM cleaned_events
GROUP BY device_id
ORDER BY avg_temp DESC;

-- 10. Most problematic devices (most alerts)
SELECT device_id,
       SUM(is_temp_alert) as temp_alerts,
       SUM(is_humidity_alert) as humidity_alerts,
       SUM(is_alert) as total_alerts
FROM cleaned_events
GROUP BY device_id
HAVING total_alerts > 0
ORDER BY total_alerts DESC;

-- ============================================================================
-- TIME-BASED ANALYSIS
-- ============================================================================

-- 11. Events per hour
SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
       COUNT(*) as event_count,
       SUM(is_alert) as alert_count
FROM cleaned_events
GROUP BY hour
ORDER BY hour DESC;

-- 12. Recent activity (last hour)
SELECT device_id, timestamp, temperature, humidity, status
FROM cleaned_events
WHERE timestamp >= datetime('now', '-1 hour')
ORDER BY timestamp DESC;

-- 13. Temperature trends over time
SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
       ROUND(AVG(temperature), 2) as avg_temp,
       ROUND(MIN(temperature), 2) as min_temp,
       ROUND(MAX(temperature), 2) as max_temp
FROM cleaned_events
GROUP BY hour
ORDER BY hour;

-- ============================================================================
-- AGGREGATES TABLE QUERIES
-- ============================================================================

-- 14. View all hourly aggregates with details
SELECT device_id,
       hour_bucket,
       ROUND(temperature_avg, 2) as temp_avg,
       ROUND(humidity_avg, 2) as hum_avg,
       alert_count,
       event_count
FROM hourly_aggregates
ORDER BY hour_bucket DESC, device_id;

-- 15. Devices with highest average temperature per hour
SELECT device_id, hour_bucket, 
       ROUND(temperature_avg, 2) as avg_temp
FROM hourly_aggregates
ORDER BY temperature_avg DESC
LIMIT 10;

-- 16. Hours with most alerts
SELECT hour_bucket,
       SUM(alert_count) as total_alerts,
       SUM(event_count) as total_events
FROM hourly_aggregates
GROUP BY hour_bucket
ORDER BY total_alerts DESC;

-- ============================================================================
-- ADVANCED QUERIES
-- ============================================================================

-- 17. Correlation between temperature and humidity
SELECT 
    CASE 
        WHEN temperature >= 40 THEN 'Hot (>=40)'
        WHEN temperature >= 30 THEN 'Warm (30-40)'
        WHEN temperature >= 20 THEN 'Moderate (20-30)'
        ELSE 'Cool (<20)'
    END as temp_range,
    COUNT(*) as readings,
    ROUND(AVG(humidity), 2) as avg_humidity
FROM cleaned_events
GROUP BY temp_range
ORDER BY temp_range;

-- 18. Device status distribution
SELECT status, COUNT(*) as count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM cleaned_events), 2) as percentage
FROM cleaned_events
GROUP BY status
ORDER BY count DESC;

-- 19. Find extreme readings
SELECT 'Highest Temperature' as metric, device_id, timestamp, temperature as value
FROM cleaned_events
ORDER BY temperature DESC
LIMIT 1
UNION ALL
SELECT 'Lowest Temperature', device_id, timestamp, temperature
FROM cleaned_events
ORDER BY temperature ASC
LIMIT 1
UNION ALL
SELECT 'Highest Humidity', device_id, timestamp, humidity
FROM cleaned_events
ORDER BY humidity DESC
LIMIT 1
UNION ALL
SELECT 'Lowest Humidity', device_id, timestamp, humidity
FROM cleaned_events
ORDER BY humidity ASC
LIMIT 1;

-- 20. Data quality check
SELECT 
    'Total Raw Events' as check_name,
    COUNT(*) as value
FROM raw_events
UNION ALL
SELECT 'Total Cleaned Events', COUNT(*) FROM cleaned_events
UNION ALL
SELECT 'Events Removed', 
       (SELECT COUNT(*) FROM raw_events) - (SELECT COUNT(*) FROM cleaned_events)
UNION ALL
SELECT 'Data Quality %',
       ROUND(100.0 * (SELECT COUNT(*) FROM cleaned_events) / (SELECT COUNT(*) FROM raw_events), 2);
