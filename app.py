import streamlit as st
from login import login_screen
from risk_logic import calculate_risk

st.set_page_config(page_title="Patient Triage MVP")

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login gate
if not st.session_state.logged_in:
    login_screen()
    st.stop()

# Header
st.title("🩺 Intelligent Patient Triage System")
st.caption("Clinical decision-support tool (MVP)")

st.sidebar.success(f"👤 {st.session_state.role}")
st.sidebar.caption(f"ID: {st.session_state.staff_id}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# Triage form
with st.form("triage_form"):
    age = st.number_input("Age", 0, 120)
    symptom = st.selectbox(
        "Primary Symptom",
        ["Fever", "Chest Pain", "Breathlessness", "General Discomfort"]
    )

    heart_rate = st.number_input("Heart Rate (bpm)", 0)
    bp = st.number_input("Systolic Blood Pressure", 0)
    spo2 = st.number_input("Oxygen Saturation (SpO₂ %)", 0, 100)
    temperature = st.number_input("Temperature (°C)", 0.0)
    pain = st.slider("Pain Severity (1–10)", 1, 10)

    submit = st.form_submit_button("Assess Priority")

if submit:
    data = {
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
    override = st.selectbox("Override Priority", override_options)

    if override != "No Override":
        reason = st.text_input("Reason for override (mandatory)")

        if reason:
            st.warning(
                f"⚠️ Priority overridden from **{system_priority}** to **{override}**"
            )
            st.write("Reason:", reason)
        else:
            st.info("Please provide a reason to apply override.")

    st.caption(
        "⚠️ This system is a decision-support tool and does not replace "
        "professional medical judgment."
    )