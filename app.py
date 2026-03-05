import streamlit as st
import json
from datetime import datetime
from login import login_screen
from register import register_user
from risk_logic import calculate_risk
from dashboard import show_dashboard
from patient_view import patient_status
from sms_alert import send_sms



st.set_page_config(page_title="Patient Triage MVP")

# ---------------- SESSION INIT ----------------


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "staff_id" not in st.session_state:
    st.session_state.staff_id = None

# ---------------- LOGIN / REGISTER ----------------

if not st.session_state.logged_in:

    option = st.radio(
        "Select Option",
        ["Login", "Register"]
    )

    if option == "Login":
        login_screen()
    else:
        register_user()

    st.stop()

# ---------------- SIDEBAR ----------------
if st.session_state.role == "Patient":
    page = "View Patient Status"

else:
    page = st.sidebar.radio(
        "Navigation",
        ["Triage Assessment", "Dashboard", "View Patient Status"]
    )

st.sidebar.success(f"👤 {st.session_state.role}")
st.sidebar.caption(f"ID: {st.session_state.staff_id}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

if page == "Dashboard":
    show_dashboard()
    st.stop()

if page == "View Patient Status":
    patient_status()
    st.stop()



# ---------------- TITLE ----------------

st.title("🩺 Intelligent Patient Triage System")
st.caption("Clinical decision-support tool (MVP)")

# ---------------- LOAD LOGS ----------------

try:
    with open("triage_log.json", "r") as f:
        logs = json.load(f)
except:
    logs = []

# ---------------- EXISTING PATIENT IDS ----------------

existing_ids = sorted(
    list(set([log.get("patient_id") for log in logs if log.get("patient_id")]))
)

# ---------------- PATIENT TYPE ----------------

st.subheader("Patient Selection")

patient_type = st.radio(
    "Select Patient Type",
    ["New Patient", "Existing Patient"]
)

selected_patient = None
existing_data = None

# ---------------- EXISTING PATIENT ----------------

if patient_type == "Existing Patient":

    if not existing_ids:
        st.warning("No existing patients found.")
        st.stop()

    selected_patient = st.selectbox(
        "Select Patient ID",
        existing_ids
    )

    patient_records = [
        log for log in logs if log.get("patient_id") == selected_patient
    ]

    if patient_records:

        existing_data = patient_records[-1]

        st.info(
            f"Loaded Patient: {existing_data.get('patient_name')} | Age {existing_data.get('age')} | Symptom {existing_data.get('symptom')}"
        )

# ---------------- PATIENT DETAILS ----------------

st.subheader("Patient Details")

if patient_type == "New Patient":

    p_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1
    )

    if p_id in existing_ids:
        st.error("⚠️ Patient ID already exists. Use 'Existing Patient'.")
        st.stop()

    patient_name = st.text_input("Patient Name")
    patient_phone = st.text_input("Patient Phone")
    relative_name = st.text_input("Relative Name")
    relative_phone = st.text_input("Relative Phone")

else:

    p_id = selected_patient
    st.write("Patient ID:", p_id)

    patient_name = st.text_input(
        "Patient Name",
        value=existing_data.get("patient_name", "")
    )

    patient_phone = st.text_input(
        "Patient Phone",
        value=existing_data.get("patient_phone", "")
    )

    relative_name = st.text_input(
        "Relative Name",
        value=existing_data.get("relative_name", "")
    )

    relative_phone = st.text_input(
        "Relative Phone",
        value=existing_data.get("relative_phone", "")
    )

# ---------------- BASIC MEDICAL INFO ----------------

age = st.number_input(
    "Age",
    min_value=0,
    max_value=120,
    value=existing_data.get("age", 0) if existing_data else 0
)

symptom_list = [
    "Fever",
    "Chest Pain",
    "Breathlessness",
    "General Discomfort"
]

symptom_index = 0

if existing_data and existing_data.get("symptom") in symptom_list:
    symptom_index = symptom_list.index(existing_data.get("symptom"))

symptom = st.selectbox(
    "Primary Symptom",
    symptom_list,
    index=symptom_index
)

# ---------------- TRIAGE FORM ----------------

st.subheader("Vital Signs")

with st.form("triage_form"):

    heart_rate = st.number_input(
        "Heart Rate (bpm)",
        min_value=30,
        max_value=220
    )

    bp = st.number_input(
        "Systolic Blood Pressure",
        min_value=60,
        max_value=250
    )

    spo2 = st.number_input(
        "Oxygen Saturation (SpO₂ %)",
        min_value=50,
        max_value=100
    )

    temperature = st.number_input(
        "Temperature (°C)",
        min_value=30.0,
        max_value=45.0
    )

    pain = st.slider(
        "Pain Severity (1–10)",
        1,
        10
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

    st.write("Risk Score:", result["score"])
    st.write("System Confidence:", f"{result['confidence']}%")
    st.write("Triage Category:", result["category"])

    st.subheader("Explanation")

    for r in result["reasons"]:
        st.write("•", r)

    # ---------------- LOGGING ----------------

    log_entry = {

        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),

        "patient_id": p_id,
        "patient_name": patient_name,
        "patient_phone": patient_phone,
        "relative_name": relative_name,
        "relative_phone": relative_phone,

        "age": age,
        "symptom": symptom,

        "heart_rate": heart_rate,
        "bp": bp,
        "spo2": spo2,
        "temperature": temperature,
        "pain": pain,

        "score": result["score"],
        "original_priority": result["priority"],
        "final_priority": result["priority"],

        "confidence": result["confidence"]
    }

    logs.append(log_entry)

    with open("triage_log.json", "w") as f:
        json.dump(logs, f, indent=2)

    st.success("Triage result saved successfully.")

    if result["priority"] == "High":

        alert = f"""
    🚨 EMERGENCY ALERT

    Patient: {patient_name}
    Symptom: {symptom}

    Priority: HIGH
    Immediate hospital visit required.
    """

        send_sms(relative_phone, alert)

    st.caption(
        "⚠️ This system supports clinical decisions and does not replace medical judgment."
    )