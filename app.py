import streamlit as st
import json
from datetime import datetime
from login import login_screen
from risk_logic import calculate_risk
from dashboard import show_dashboard

st.set_page_config(page_title="Patient Triage MVP")

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login gate
if not st.session_state.logged_in:
    login_screen()
    st.stop()


page = st.sidebar.radio(
    "Navigation",
    ["Triage Assessment", "Dashboard"]
)
if page == "Dashboard":
    show_dashboard()
    st.stop()

# Header
if page == "Triage Assessment":
    st.title("🩺 Intelligent Patient Triage System")
    st.caption("Clinical decision-support tool (MVP)")

    st.sidebar.success(f"👤 {st.session_state.role}")
    st.sidebar.caption(f"ID: {st.session_state.staff_id}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# Triage form
with st.form("triage_form"):
    p_id = st.number_input("Patient ID", min_value=1)
    age = st.number_input("Age", 0, 120)
    symptom = st.selectbox(
        "Primary Symptom",
        ["Fever", "Chest Pain", "Breathlessness", "General Discomfort"]
    )
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=220)
    bp = st.number_input("Systolic Blood Pressure", min_value=60, max_value=250)
    spo2 = st.number_input("Oxygen Saturation (SpO₂ %)", min_value=50, max_value=100)
    temperature = st.number_input("Temperature (°C)", min_value=30.0, max_value=45.0)
    pain = st.slider("Pain Severity (1–10)", 1, 10)

    submit = st.form_submit_button("Assess Priority")

if submit:
    data = {
        "patient_id": p_id,
        "age": age,
        "symptom": symptom,
        "heart_rate": heart_rate or None,
        "bp": bp or None,
        "spo2": spo2 or None,
        "temperature": temperature or None,
        "pain": pain
    }

    result = calculate_risk(data)

    st.subheader("Triage Result")

    if result["priority"] == "High":
        st.error("🔴 HIGH PRIORITY")
    elif result["priority"] == "Medium":
        st.warning("🟡 MEDIUM PRIORITY")
    else:
        st.success("🟢 LOW PRIORITY")

    st.write("**Risk Score:**", result["score"])
    st.write("**System Confidence:**", f"{result['confidence']}%")
    st.write("**Triage Category:**", result["category"])

    st.subheader("Explanation")
    for r in result["reasons"]:
        st.write("•", r)

    if result["missing"]:
        st.info(
            "⚠️ Missing data: " + ", ".join(result["missing"]) +
            ". Risk may be underestimated."
        )

    # --- Staff Override Logic ---
    system_priority = result["priority"]

    if system_priority == "Low":
        override_options = ["No Override", "Medium", "High"]
    elif system_priority == "Medium":
        override_options = ["No Override", "High"]
    else:
        override_options = ["No Override"]
        st.info(
            "🚨 High-risk cases cannot be downgraded to ensure patient safety."
        )

    st.subheader("Staff Override (Optional)")
    final_override = st.selectbox("Override Priority", override_options)
   

    reason = None

    if final_override != "No Override":
        reason = st.text_input("Reason for override (mandatory)")

    if reason:
        st.warning(
            f"⚠️ Priority overridden from **{system_priority}** to **{final_override}**"
        )
        st.write("Reason:", reason)
    else:
        st.info("Please provide a reason to apply override.")

    final_priority = system_priority

    if final_override != "No Override" and reason:
        final_priority = final_override

    if final_override != "No Override" and not reason:
        st.error("Override requires a reason.")
        st.stop()

    log_entry = {
    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "patient_id": p_id,
    "age": age,
    "symptom": symptom,
    "pain": pain,
    "score": result["score"],

    "original_priority": system_priority,
    "final_priority": final_priority,

    "override_by": st.session_state.role if final_override != "No Override" else None,
    "override_reason": reason if final_override != "No Override" else None,

    "confidence": result["confidence"]
}


    try:
        with open("triage_log.json", "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(log_entry)

    with open("triage_log.json", "w") as f:
        json.dump(logs, f, indent=2)

    st.caption(
        "⚠️ This system is a decision-support tool and does not replace "
        "professional medical judgment."
    )