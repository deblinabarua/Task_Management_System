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

if st.session_state.get("logged_in"):
    user = st.session_state.get("user", {})
    access = user.get("access")
    if access == "Admin":
        st.switch_page("pages/admin_dash.py")
    elif access == "Manager":
        st.switch_page("pages/manager_dash.py")
    else:
        st.switch_page("pages/emp_dash.py")
    st.stop()

st.title("Task Management System", text_alignment = "center")
tab1, tab2= st.tabs(["Homepage", "Login"])

with tab1:
    st.header("Home")
    st.text("Keep track of all your and others' tasks here.")

with tab2:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("Login User"):
            st.header("Log in to your Account")
            username = st.text_input("Enter username:").strip()
            password = st.text_input("Enter password:", type = "password").strip()

            login = st.form_submit_button("Login")

            if login:
                if not username or not password:
                    st.error("Please fill all fields.")
                else:
                    send_user = api_post("/homepage", payload = {"username": username, "password": password})
                    
                    if send_user is None:
                        st.error("Server is unreachable. Try again later.")
                        st.stop()

                    if send_user.status_code == 200:
                        user = send_user.json()
                        st.session_state.logged_in = True
                        st.session_state.user = user

                        if user["change_pass"]:
                            st.switch_page("pages/change_pass.py")
                            st.stop()
                        elif user['access'] == 'Admin':
                            st.switch_page('pages/admin_dash.py')
                            st.stop()
                        elif user['access'] == 'Manager':
                            st.switch_page('pages/manager_dash.py')
                            st.stop()
                        else:
                            st.switch_page('pages/emp_dash.py')
                            st.stop()
                    else:
                        try:
                            st.error(send_user.json()["message"])
                        except:
                            st.error("Something went wrong. Please try again later.") 
                           