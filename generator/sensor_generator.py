"""IoT sensor simulator capable of writing to stdout, file, or Kafka."""
from __future__ import annotations

import argparse
import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Protocol

from generator.config import GeneratorConfig, Thresholds

logger = logging.getLogger("sensor-generator")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class Sink(Protocol):
    def send(self, payload: dict) -> None:  # pragma: no cover - interface
        ...

    def close(self) -> None:  # pragma: no cover - interface
        ...


class StdoutSink:
    def send(self, payload: dict) -> None:
        print(json.dumps(payload), flush=True)

    def close(self) -> None:  # noqa: D401 - nothing to release
        return


class FileSink:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.file_path.open("a", encoding="utf-8")
        logger.info("Writing events to %s", self.file_path)

    def send(self, payload: dict) -> None:
        self._handle.write(json.dumps(payload) + "\n")
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()


class KafkaSink:
    def __init__(self, broker: str, topic: str) -> None:
        from kafka import KafkaProducer
        from kafka.errors import NoBrokersAvailable

        self.topic = topic
        self.producer = None
        
        retries = 10
        for i in range(retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=broker,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
                logger.info("Producing to Kafka topic '%s' at %s", topic, broker)
                break
            except NoBrokersAvailable:
                if i == retries - 1:
                    raise
                logger.warning("Kafka broker %s not available yet. Retrying in 2s... (%d/%d)", broker, i + 1, retries)
                time.sleep(2)

    def send(self, payload: dict) -> None:
        self.producer.send(self.topic, payload)

    def close(self) -> None:
        self.producer.flush()
        self.producer.close()


@dataclass
class SensorGenerator:
    config: GeneratorConfig
    thresholds: Thresholds

    def generate(self) -> dict:
        temp = round(random.uniform(*self.config.temp_range), 2)
        humidity = round(random.uniform(*self.config.humidity_range), 2)
        status = "ALERT" if (temp >= self.thresholds.temp_alert or humidity <= self.thresholds.humidity_alert) else "OK"
        payload = {
            "device_id": f"dev_{random.randint(1, self.config.device_count)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "status": status,
        }
        return payload


class CompositeSink:
    def __init__(self, sinks: list[Sink]) -> None:
        self.sinks = sinks

    def send(self, payload: dict) -> None:
        for sink in self.sinks:
            sink.send(payload)

    def close(self) -> None:
        for sink in self.sinks:
            sink.close()


def build_sink(args: argparse.Namespace, cfg: GeneratorConfig) -> Sink:
    sinks = []
    requested_sinks = args.sink.split(",")
    
    for s in requested_sinks:
        s = s.strip()
        if s == "stdout":
            sinks.append(StdoutSink())
        elif s == "file":
            file_path = Path(args.output or cfg.raw_data_path / "sensor_log.jsonl")
            sinks.append(FileSink(file_path))
        elif s == "kafka":
            broker = args.kafka_broker or cfg.kafka_broker
            if not broker:
                raise SystemExit("Kafka broker not provided. Set KAFKA_BROKER or pass --kafka-broker.")
            topic = args.kafka_topic or cfg.kafka_topic
            sinks.append(KafkaSink(broker, topic))
        else:
            raise SystemExit(f"Unsupported sink '{s}'.")
            
    return CompositeSink(sinks)


def parse_args(cfg: GeneratorConfig) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate IoT sensor telemetry events.")
    parser.add_argument("--sink", default="file", help="Where to emit events (comma-separated: file,kafka,stdout).")
    parser.add_argument("--output", help="File path for --sink file (defaults to data/raw/sensor_log.jsonl)")
    parser.add_argument("--kafka-broker", help="Kafka bootstrap servers; overrides env config.")
    parser.add_argument("--kafka-topic", help="Kafka topic name; overrides env config.")
    parser.add_argument("--interval", type=float, default=cfg.interval_seconds, help="Delay between events (seconds).")
    parser.add_argument("--max-events", type=int, default=0, help="Stop after N events (0 = run forever).")
    parser.add_argument("--seed", type=int, help="Optional random seed for deterministic output.")
    return parser.parse_args()


def event_stream(gen: SensorGenerator) -> Iterable[dict]:
    while True:
        yield gen.generate()


def main() -> None:
    cfg = GeneratorConfig.from_env()
    thresholds = Thresholds.from_env()
    args = parse_args(cfg)
    if args.seed is not None:
        random.seed(args.seed)

    gen = SensorGenerator(cfg, thresholds)
    sink = build_sink(args, cfg)
    max_events = args.max_events if args.max_events and args.max_events > 0 else None
    emitted = 0

    logger.info(
        "Starting generator | sink=%s interval=%.2fs devices=%d",
        args.sink,
        args.interval,
        cfg.device_count,
    )

    try:
        for payload in event_stream(gen):
            sink.send(payload)
            
            # Direct alert logging (bypass Kafka/Streaming)
            if payload["status"] == "ALERT" and cfg.alert_log_path:
                log_path = Path(cfg.alert_log_path)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Determine reason
                reasons = []
                if payload['temperature'] >= thresholds.temp_alert:
                    reasons.append("Temperature High")
                if payload['humidity'] <= thresholds.humidity_alert:
                    reasons.append("Humidity Low")
                reason_str = ", ".join(reasons) if reasons else "Unknown"

                with log_path.open("a", encoding="utf-8") as f:
                    # Format: timestamp | LEVEL | message | reason
                    msg = f"{payload['timestamp']} | ALERT | Device {payload['device_id']} | Reason: {reason_str} | Temp: {payload['temperature']}, Humidity: {payload['humidity']}"
                    f.write(msg + "\n")

            emitted += 1
            if max_events and emitted >= max_events:
                logger.info("Reached max events (%d). Stopping.", emitted)
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Generator interrupted by user after %d events.", emitted)
    finally:
        sink.close()


if __name__ == "__main__":
    main()
