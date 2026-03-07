import streamlit as st
from patient_view import patient_status
import json

def login_screen():

    st.title("🔐 Hospital Staff Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    staff_id = st.text_input("Login ID")
    role = st.selectbox("Role", ["Doctor", "Nurse", "Patient"])

    if st.button("Login"):

        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except:
            st.error("No users registered.")
            return

        user_found = False

        for u in users:

            if (
                u["username"] == username and
                u["password"] == password and
                str(u["staff_id"]) == staff_id and
                u["role"] == role
            ):

                user_found = True

                st.session_state.logged_in = True
                st.session_state.role = u["role"]

                # ✅ FIXED HERE
                st.session_state.staff_id = u["staff_id"]

                st.session_state.username = u["username"]
                st.session_state.phone = u["phone"]

                st.success("Login successful")

                # Patient login
                if u["role"] == "Patient":
                    st.session_state.patient_id = u["staff_id"]
                    st.rerun()

                # Doctor/Nurse login
                else:
                    st.rerun()

        if not user_found:
            st.error("Invalid username, password, role, or ID")