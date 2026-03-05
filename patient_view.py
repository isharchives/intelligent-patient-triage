import streamlit as st
import json


def patient_status():

    st.title("🧾 Patient Report")

    patient_id = st.session_state.get("patient_id")

    if not patient_id:
        st.error("No patient ID found")
        return

    try:
        with open("triage_log.json","r") as f:
            logs = json.load(f)
    except:
        st.error("No records found")
        return

    records = [l for l in logs if str(l.get("patient_id")) == str(patient_id)]

    if not records:
        st.warning("No patient found")
        return

    latest = records[-1]

    st.subheader("Patient Information")

    st.write("Name:", latest.get("patient_name"))
    st.write("Phone:", latest.get("patient_phone"))
    st.write("Age:", latest.get("age"))
    st.write("Symptom:", latest.get("symptom"))

    st.subheader("Vitals")

    st.write("Heart Rate:", latest.get("heart_rate"))
    st.write("BP:", latest.get("bp"))
    st.write("SpO2:", latest.get("spo2"))
    st.write("Temperature:", latest.get("temperature"))

    st.subheader("Triage Result")

    st.write("Priority:", latest.get("final_priority"))
    st.write("Confidence:", latest.get("confidence"))