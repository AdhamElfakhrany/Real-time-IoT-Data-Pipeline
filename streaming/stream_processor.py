"""Kafka streaming processor that detects anomalies and emits alerts."""
from __future__ import annotations

import json
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from kafka import KafkaConsumer, KafkaProducer

from generator.config import Thresholds
from streaming.alerting import AlertDispatcher
from streaming.config import StreamingConfig

logger = logging.getLogger("stream-processor")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


class StreamProcessor:
    def __init__(self, config: StreamingConfig, thresholds: Thresholds) -> None:
        self.config = config
        self.thresholds = thresholds
        self.consumer = KafkaConsumer(
            config.raw_topic,
            bootstrap_servers=config.kafka_broker,
            group_id=config.group_id,
            auto_offset_reset=config.auto_offset_reset,
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self.alert_dispatcher = AlertDispatcher(
            producer=self.producer if config.alert_topic else None,
            kafka_topic=config.alert_topic,
            webhook_url=config.alert_webhook,
            slack_webhook=config.alert_slack_webhook,
            log_path=Path(config.alert_log_path) if config.alert_log_path else None,
        )
        logger.info(
            "Streaming processor ready (raw=%s processed=%s alert=%s)",
            config.raw_topic,
            config.processed_topic,
            config.alert_topic,
        )

    def _is_alert(self, record: dict) -> bool:
        temp = record.get("temperature")
        humidity = record.get("humidity")
        return bool(temp is not None and temp >= self.thresholds.temp_alert) or bool(
            humidity is not None and humidity <= self.thresholds.humidity_alert
        )

    def _build_alert_payload(self, record: dict) -> dict:
        return {
            "device_id": record.get("device_id"),
            "timestamp": record.get("timestamp"),
            "temperature": record.get("temperature"),
            "humidity": record.get("humidity"),
            "status": "ALERT",
            "reason": self._alert_reason(record),
        }

    def _alert_reason(self, record: dict) -> str:
        reasons = []
        if record.get("temperature") is not None and record["temperature"] >= self.thresholds.temp_alert:
            reasons.append("temperature_high")
        if record.get("humidity") is not None and record["humidity"] <= self.thresholds.humidity_alert:
            reasons.append("humidity_low")
        return ",".join(reasons) or "threshold"

    def _process_record(self, record: dict) -> None:
        try:
            is_alert = self._is_alert(record)
            record["is_alert"] = is_alert
            record["reason"] = self._alert_reason(record) if is_alert else None
            self.producer.send(self.config.processed_topic, record)
            if is_alert:
                alert_payload = self._build_alert_payload(record)
                self.alert_dispatcher.emit(alert_payload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to process record: %s", exc)
            if self.config.dead_letter_topic:
                self.producer.send(self.config.dead_letter_topic, record)

    def run(self) -> None:
        logger.info("Consuming events... press Ctrl+C to exit")
        for message in self.consumer:
            if not isinstance(message.value, dict):
                logger.debug("Skipping non-dict payload: %s", message.value)
                continue
            self._process_record(message.value)

    def close(self) -> None:
        logger.info("Shutting down stream processor")
        self.consumer.close()
        self.producer.flush()
        self.producer.close()


_processor: Optional[StreamProcessor] = None


def _handle_shutdown(signum, frame):  # noqa: D401 - signal handler
    logger.info("Received signal %s", signum)
    if _processor:
        _processor.close()
    sys.exit(0)


def main() -> None:
    global _processor  # noqa: PLW0603 - needed to close on signals
    cfg = StreamingConfig.from_env()
    thresholds = Thresholds.from_env()
    _processor = StreamProcessor(cfg, thresholds)

    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    try:
        _processor.run()
    finally:
        _processor.close()


if __name__ == "__main__":
    main()
