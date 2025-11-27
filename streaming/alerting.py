"""Alert dispatching utilities for streaming processor."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
from kafka import KafkaProducer


@dataclass
class AlertDispatcher:
    producer: Optional[KafkaProducer]
    kafka_topic: Optional[str]
    webhook_url: Optional[str]
    slack_webhook: Optional[str]
    log_path: Optional[Path]

    def emit(self, payload: dict) -> None:
        self._send_kafka(payload)
        self._send_webhook(payload)
        self._send_slack(payload)
        self._write_log(payload)

    def _send_kafka(self, payload: dict) -> None:
        if not (self.producer and self.kafka_topic):
            return
        self.producer.send(self.kafka_topic, payload)

    def _send_webhook(self, payload: dict) -> None:
        if not self.webhook_url:
            return
        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=5)
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            print(f"[alert-dispatch] Webhook failed: {exc}")

    def _send_slack(self, payload: dict) -> None:
        if not self.slack_webhook:
            return
        message = self._format_slack_payload(payload)
        try:
            resp = requests.post(self.slack_webhook, json=message, timeout=5)
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            print(f"[alert-dispatch] Slack webhook failed: {exc}")

    def _format_slack_payload(self, payload: dict) -> dict:
        device = payload.get("device_id", "unknown")
        reason = payload.get("reason", "threshold")
        temp = payload.get("temperature")
        humidity = payload.get("humidity")
        timestamp = payload.get("timestamp")
        text = (
            f"í´¥ IoT Alert on {device}\n"
            f"Reason: {reason}\n"
            f"Temperature: {temp}Â°C, Humidity: {humidity}%\n"
            f"Timestamp: {timestamp}"
        )
        return {"text": text}

    def _write_log(self, payload: dict) -> None:
        if not self.log_path:
            return
        path = Path(self.log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{payload}\n")
