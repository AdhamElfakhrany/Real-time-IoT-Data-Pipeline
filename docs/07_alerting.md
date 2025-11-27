# Step 7 – Alerting Integrations

## Overview
The streaming processor now fans out alerts to multiple channels via `streaming/alerting.py`:
- Kafka topic (`KAFKA_ALERT_TOPIC`)
- Generic HTTP webhook (`ALERT_WEBHOOK_URL`)
- Slack Incoming Webhook (`ALERT_SLACK_WEBHOOK_URL`)
- Local log file (`ALERT_LOG_PATH`)

## Configuration
Update `.env` (or docker-compose env vars):
```
ALERT_WEBHOOK_URL=https://example.com/webhook
ALERT_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/.../...
ALERT_LOG_PATH=logs/alerts.log
```
If a field is omitted it is skipped. All channels can run simultaneously.

## Slack Payload
Alerts render a short text message including device id, reason, readings, and timestamp. Customize formatting inside `AlertDispatcher._format_slack_payload` if needed (e.g., add emojis, blocks, or channel tags).

## Local Testing
1. Ensure Kafka stack is running (`docker compose up -d`).
2. Start the streaming processor (either container or `python -m streaming.stream_processor`).
3. Trigger alerts by raising generator temperature range.
4. Verify outputs:
   - `docker compose logs stream-processor`
   - `kafka-console-consumer --topic iot.alerts`
   - Inspect `logs/alerts.log`
   - Check Slack/webhook endpoints.

## Hardening Ideas
- Add retry/backoff for webhooks (currently best-effort logging).
- Support email/SMS providers (Twilio/SendGrid).
- Persist alert history in a database for auditing.
