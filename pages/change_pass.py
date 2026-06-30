import streamlit as st
import requests
from dotenv import load_dotenv
import os
from task_function import api_post

load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(
    initial_sidebar_state="collapsed",
    layout = "wide"
)

if not st.session_state.get("logged_in") or not st.session_state.get("user"):
    st.switch_page("task_front.py")
    st.stop()

curr_user = st.session_state.user["empid"]

with st.form("change_pass"):
    old = st.text_input("Old Password", type = "password").strip()
    new = st.text_input("New Password", type = "password").strip()
    confirm = st.text_input("Confirm Password", type = "password").strip()
    submit = st.form_submit_button("Update")

    if submit:
        if not old or not new or not confirm:
            st.error("Please fill all fields.")
        elif new != confirm:
            st.error("Passwords do not match.")
        elif old == new:
            st.error("New password should not match old password.")
        else:
            update = api_post("/change_password", payload = {"empid": curr_user, "old": old, "new": new})

            if update is None:
                st.error("Server is unreachable. Please try again later.")
                st.stop()

            if update.status_code == 200:
                st.success("Password updated.")
                st.session_state.user["change_pass"] = False
                if (st.session_state.user["access"] == "Admin"):
                    st.switch_page("pages/admin_dash.py")
                    st.stop()
                elif (st.session_state.user["access"] == "Manager"):
                    st.switch_page("pages/manager_dash.py")
                    st.stop()
                else:
                    st.switch_page("pages/emp_dash.py")
                    st.stop()
            else:
                try:
                    st.error(update.json()["message"])
                except:
                    st.error("Something went wrong. Please try again later.")
