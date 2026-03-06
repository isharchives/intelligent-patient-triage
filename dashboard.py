import streamlit as st
import json
import pandas as pd
from pathlib import Path

def show_dashboard():

    st.title("📊 Emergency Department Dashboard")

    log_file = Path("triage_log.json")

    if not log_file.exists():
        st.info("No triage data available yet.")
        return

    try:
        with open(log_file, "r") as f:
            logs = json.load(f)
    except:
        logs = []

    if not logs:
        st.info("No triage data available yet.")
        return

    df = pd.DataFrame(logs)

    # Metrics
    high = (df["final_priority"] == "High").sum()
    medium = (df["final_priority"] == "Medium").sum()
    low = (df["final_priority"] == "Low").sum()

    st.subheader("Current Triage Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("🔴 Emergency", int(high))
    col2.metric("🟡 Urgent", int(medium))
    col3.metric("🟢 Non‑Urgent", int(low))

    st.divider()

    st.subheader("Recent Triage Cases")

    df_recent = df.sort_values("time", ascending=False).head(10)

    st.dataframe(df_recent, use_container_width=True)

    if st.button("🔄 Refresh Dashboard"):
        st.rerun()