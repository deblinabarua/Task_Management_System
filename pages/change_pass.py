import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(
    initial_sidebar_state="collapsed",
    layout = "wide"
)

if ("logged_in" not in st.session_state):
    st.switch_page("task_front.py")

curr_user = st.session_state.user["empid"]

with st.form("change_pass"):
    old = st.text_input("Old Password", type = "password")
    new = st.text_input("New Password", type = "password")
    confirm = st.text_input("Confirm Password", type = "password")
    submit = st.form_submit_button("Update")

    if submit:
        if new != confirm:
            st.error("Passwords do not match.")
        else:
            update = requests.post(f"{API_URL}/change_password", json = {"empid": curr_user, "old": old, "new": new})
            if update.status_code == 200:
                st.success("Password updated.")
                st.session_state.user["change_pass"] = False
                if (st.session_state.user["access"] == "Admin"):
                    st.switch_page("pages/admin_dash.py")
                elif (st.session_state.user["access"] == "Manager"):
                    st.switch_page("pages/manager_dash.py")
                else:
                    st.switch_page("pages/emp_dash.py")
            else:
                st.error(update.json()["message"])
