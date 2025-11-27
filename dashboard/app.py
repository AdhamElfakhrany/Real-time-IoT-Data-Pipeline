"""Streamlit dashboard for real-time IoT pipeline outputs."""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PROCESSED_DIR = Path(os.getenv("PROCESSED_DATA_PATH", "data/processed"))
CLEANSED_PATH = Path(os.getenv("DASHBOARD_CLEANSED_PATH", PROCESSED_DIR / "cleansed.parquet"))
AGGREGATES_PATH = Path(os.getenv("DASHBOARD_AGGREGATES_PATH", PROCESSED_DIR / "aggregates.parquet"))
REFRESH_SECONDS = int(os.getenv("DASHBOARD_REFRESH_SECONDS", "30"))


@st.cache_data(ttl=REFRESH_SECONDS)
def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path, parse_dates=["timestamp"], infer_datetime_format=True)
    raise ValueError(f"Unsupported file extension: {path.suffix}")


def summarize_alerts(df: pd.DataFrame) -> tuple[int, int]:
    if df.empty or "is_alert" not in df.columns:
        return 0, 0
    # Handle both boolean and integer (0/1) types
    alert_rows = df[df["is_alert"] == 1]
    return len(alert_rows), alert_rows["device_id"].nunique()


def format_timestamp(ts: datetime | pd.Timestamp | None) -> str:
    if ts is None or pd.isna(ts):
        return "N/A"
    if isinstance(ts, pd.Timestamp):
        ts = ts.to_pydatetime()
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def render_header():
    st.set_page_config(page_title="IoT Pipeline Dashboard", layout="wide")
    st.title("🚀 IoT Pipeline Dashboard")
    st.caption("Batch + streaming telemetry insights")


def render_summary_cards(df: pd.DataFrame):
    total_events = len(df)
    total_devices = df["device_id"].nunique() if not df.empty else 0
    alert_count, alert_devices = summarize_alerts(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Events", f"{total_events:,}")
    col2.metric("Devices", f"{total_devices:,}")
    col3.metric("Alerts", f"{alert_count:,}")
    col4.metric("Devices in Alert", f"{alert_devices:,}")


def render_time_series(df: pd.DataFrame):
    if df.empty:
        st.info("No cleansed data available yet. Generate events to populate the dashboard.")
        return
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp")

    st.subheader("Temperature & Humidity Trends")
    chart_df = df.set_index("timestamp")[
        ["temperature", "humidity"]
    ]
    st.line_chart(chart_df)


def render_alert_table(df: pd.DataFrame):
    st.subheader("Recent Alerts")
    if "is_alert" not in df.columns:
        st.info("No alert data available.")
        return
    alerts = df[df["is_alert"] == 1].copy()
    if alerts.empty:
        st.success("No alerts in the current dataset ✅")
        return

    # Derive reason from boolean flags
    def get_reason(row):
        reasons = []
        if row.get("is_temp_alert"):
            reasons.append("Temperature High")
        if row.get("is_humidity_alert"):
            reasons.append("Humidity Low")
        return ", ".join(reasons) if reasons else "Unknown"

    alerts["reason"] = alerts.apply(get_reason, axis=1)

    alerts["timestamp"] = pd.to_datetime(alerts["timestamp"])
    alerts = alerts.sort_values("timestamp", ascending=False).head(25)
    alerts["timestamp"] = alerts["timestamp"].apply(format_timestamp)
    
    st.dataframe(
        alerts[["timestamp", "device_id", "reason", "temperature", "humidity"]], 
        use_container_width=True
    )


def render_aggregates(df: pd.DataFrame):
    st.subheader("Hourly Aggregates")
    if df.empty:
        st.info("Aggregates dataset is empty. Run the batch ETL or ingest more data.")
        return
    df = df.copy()
    df["hour_bucket"] = pd.to_datetime(df["hour_bucket"], utc=True)
    st.dataframe(df.sort_values("hour_bucket", ascending=False).head(20), use_container_width=True)


def main():
    render_header()

    cleansed = load_dataset(CLEANSED_PATH)
    aggregates = load_dataset(AGGREGATES_PATH)

    st.sidebar.header("Settings")
    st.sidebar.write(f"Cleansed file: `{CLEANSED_PATH}`")
    st.sidebar.write(f"Aggregates file: `{AGGREGATES_PATH}`")
    st.sidebar.write(f"Auto-refresh every {REFRESH_SECONDS}s (cache TTL)")

    render_summary_cards(cleansed)
    render_time_series(cleansed)
    render_alert_table(cleansed)
    render_aggregates(aggregates)


if __name__ == "__main__":
    main()
