import streamlit as st
import json

def show_dashboard():

    st.title("📊 Emergency Department Dashboard")

    try:
        with open("triage_log.json", "r") as f:
            logs = json.load(f)
    except:
        logs = []

    if not logs:
        st.info("No triage data available yet.")
        return

    # Metrics
    high = sum(1 for l in logs if l["final_priority"] == "High")
    medium = sum(1 for l in logs if l["final_priority"] == "Medium")
    low = sum(1 for l in logs if l["final_priority"] == "Low")

    st.subheader("Current Triage Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("🔴 Emergency", high)
    col2.metric("🟡 Urgent", medium)
    col3.metric("🟢 Non‑Urgent", low)

    st.divider()

    st.subheader("Recent Triage Cases")
    st.table(logs[-10:])