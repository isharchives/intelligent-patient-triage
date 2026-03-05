import streamlit as st
import json
import os

def register_user():

    st.title("📝 Staff Registration")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    role = st.selectbox(
        "Role",
        ["Doctor", "Nurse", "Patient"]
    )

    staff_id = st.text_input("Staff ID")

    phone = st.text_input("Phone Number")

    if st.button("Register"):

        if not username or not password or not staff_id:
            st.error("Please fill all required fields.")
            return

        # Load existing users
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                users = json.load(f)
        else:
            users = []

        # Check duplicate username
        for u in users:
            if u["username"] == username:
                st.error("Username already exists.")
                return

        new_user = {
            "username": username,
            "password": password,
            "role": role,
            "staff_id": staff_id,
            "phone": phone
        }

        users.append(new_user)

        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)

        st.success("Registration successful. Please login.")