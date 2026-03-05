import streamlit as st
import json
from datetime import datetime
from login import login_screen
from risk_logic import calculate_risk
from dashboard import show_dashboard

st.set_page_config(page_title="Patient Triage MVP")

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ---------------- SIDEBAR ----------------

page = st.sidebar.radio(
    "Navigation",
    ["Triage Assessment", "Dashboard"],
    key="nav"
)

if page == "Dashboard":
    show_dashboard()
    st.stop()

st.title("🩺 Intelligent Patient Triage System")
st.caption("Clinical decision-support tool (MVP)")

st.sidebar.success(f"👤 {st.session_state.role}")
st.sidebar.caption(f"ID: {st.session_state.staff_id}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------- LOAD LOGS ----------------

try:
    with open("triage_log.json", "r") as f:
        logs = json.load(f)
except:
    logs = []

# ---------------- PATIENT SELECTION ----------------

st.subheader("Patient Selection")

patient_type = st.radio(
    "Select Patient Type",
    ["New Patient", "Existing Patient"],
    key="patient_type"
)

existing_ids = sorted(list(set(
    [log.get("patient_id") for log in logs if log.get("patient_id") is not None]
)))

selected_patient = None
existing_data = None

if patient_type == "Existing Patient" and existing_ids:

    selected_patient = st.selectbox(
    "Select Existing Patient ID",
    existing_ids,
    key="existing_patient"
    )

    patient_records = [
        log for log in logs if log.get("patient_id") == selected_patient
    ]

    if patient_records:
        existing_data = patient_records[-1]

        st.info(
            f"Loaded Patient: Age {existing_data.get('age')} | Symptom: {existing_data.get('symptom')}"
        )

        # ✅ FIX: Update session state so widgets populate correctly
        st.session_state.age_input = existing_data.get("age", 0)
        st.session_state.symptom_input = existing_data.get("symptom", "Fever")

# ---------------- BASIC INFO ----------------

if patient_type == "New Patient":

    p_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1,
        key="patient_id_new"
    )

    if p_id in existing_ids:
        st.error("⚠️ Patient ID already exists. Please use 'Existing Patient' option.")
        st.stop()

else:
    p_id = selected_patient
    st.write("Patient ID:", p_id)

# ---------------- AGE INPUT ----------------

age = st.number_input(
    "Age",
    min_value=0,
    max_value=120,
    key="age_input"
)

# ---------------- SYMPTOM INPUT ----------------

symptom_list = ["Fever", "Chest Pain", "Breathlessness", "General Discomfort"]

symptom = st.selectbox(
    "Primary Symptom",
    symptom_list,
    key="symptom_input"
)

if p_id is None:
    st.error("Please select or create a patient first.")
    st.stop()

# ---------------- TRIAGE FORM ----------------

st.subheader("Vital Signs")

with st.form("triage_form"):

    heart_rate = st.number_input(
        "Heart Rate (bpm)",
        min_value=30,
        max_value=220,
        key="heart_rate"
    )

    bp = st.number_input(
        "Systolic Blood Pressure",
        min_value=60,
        max_value=250,
        key="bp"
    )

    spo2 = st.number_input(
        "Oxygen Saturation (SpO₂ %)",
        min_value=50,
        max_value=100,
        key="spo2"
    )

    temperature = st.number_input(
        "Temperature (°C)",
        min_value=30.0,
        max_value=45.0,
        key="temperature"
    )

    pain = st.slider(
        "Pain Severity (1–10)",
        1,
        10,
        key="pain"
    )

    submit = st.form_submit_button("Assess Priority")

# ---------------- TRIAGE RESULT ----------------

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
            "⚠️ Missing data: "
            + ", ".join(result["missing"])
            + ". Risk may be underestimated."
        )

    # ---------------- OVERRIDE ----------------

    system_priority = result["priority"]

    if system_priority == "Low":
        override_options = ["No Override", "Medium", "High"]
    elif system_priority == "Medium":
        override_options = ["No Override", "High"]
    else:
        override_options = ["No Override"]
        st.info("🚨 High-risk cases cannot be downgraded.")

    st.subheader("Staff Override (Optional)")

    final_override = st.selectbox(
        "Override Priority",
        override_options,
        key="override"
    )

    reason = None

    if final_override != "No Override":
        reason = st.text_input(
            "Reason for override (mandatory)",
            key="override_reason"
        )

    if final_override != "No Override" and not reason:
        st.error("Override requires a reason.")
        st.stop()

    final_priority = system_priority

    if final_override != "No Override":
        final_priority = final_override

    # ---------------- LOGGING ----------------

    log_entry = {
    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "patient_id": p_id,
    "age": age,
    "symptom": symptom,
    "heart_rate": heart_rate,
    "bp": bp,
    "spo2": spo2,
    "temperature": temperature,
    "pain": pain,
    "score": result["score"],
    "original_priority": system_priority,
    "final_priority": final_priority,
    "override_by": st.session_state.role if final_override != "No Override" else None,
    "override_reason": reason if final_override != "No Override" else None,
    "confidence": result["confidence"]
    }

    logs.append(log_entry)

    with open("triage_log.json", "w") as f:
        json.dump(logs, f, indent=2)

    st.success("Triage result saved successfully.")

    st.caption(
        "⚠️ This system is a decision-support tool and does not replace professional medical judgment."
    )