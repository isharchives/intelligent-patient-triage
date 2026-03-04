import streamlit as st

def login_screen():
    st.title("🔐 Staff Login")

    role = st.selectbox(
        "Select Role",
        ["Nurse", "Doctor"]
    )

    staff_id = st.text_input("Staff ID")

    login_btn = st.button("Login")

    if login_btn:
        if staff_id.strip() == "":
            st.error("Please enter Staff ID")
        else:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.staff_id = staff_id
            st.success(f"Logged in as {role}")
            st.rerun()