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

if "search_id" not in st.session_state:
    st.session_state.search_id = None

st.title("Admin Dashboard", text_alignment = "center")
tab1, tab2, tab3 = st.tabs(["Add Employees", "Update Access", "Disable Account"])

with tab1:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("Add Employees"):
            st.header("Add Employees")
            firstname = st.text_input("Enter first name: ")
            lastname = st.text_input("Enter last name: ")
            access = st.radio("Access privileges: ", ["Admin", "Manager", "Employee"])
            email = st.text_input("Enter email: ")
            mobile = st.text_input("Enter mobile number: ")
            add_emp = st.form_submit_button("Add")

            if add_emp:
                if not firstname or not lastname or not access or not email or not mobile:
                    st.error("Please fill all fields.")
                make_user = requests.post(f"{API_URL}/addemp", json = {"firstname": firstname, "lastname": lastname, "access": access, "email": email, "mobile": mobile})
                if make_user.status_code == 200:
                    st.success(make_user.json()["message"])
                    st.write(f"Employee username is {make_user.json()["username"]} and the password is {make_user.json()["temp_password"]}")
                else:
                    st.error(f"{make_user.status_code}")

with tab2:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.search_id:
            with st.form("Search Employee"):
                st.header("Search Employee")
                empid = st.text_input("Enter employee ID: ")
                get_emp = st.form_submit_button("Search")
                if get_emp:
                    get_access = requests.post(f"{API_URL}/getaccess", json = {"empid": empid})
                    if get_access.status_code == 200:
                        st.session_state.search_id = get_access.json()
                    else:
                        st.error(f"{make_user.status_code}")

        else:
            with st.form("Update Employee Details"):
                options = ["Admin", "Manager", "Employee"]
                select_access = st.radio("Access privileges: ", options, index = options.index(st.session_state.search_id["access"]))
                new_access = st.form_submit_button("Update Access")
                if new_access:
                    send_access = requests.post(f"{API_URL}/sendaccess", json = {"access": select_access, "empid": st.session_state.search_id["empid"]})
                    if send_access.status_code == 200:
                        st.success(send_access.json()["message"])
                        st.write(f"Employee's access privileges has been changed to {send_access.json()['access']}")
                        del st.session_state.search_id
                    else:
                        st.error(f"{make_user.status_code}")
                    
with tab3:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("disable"):
            empid = st.text_input("Employee ID")
            disable = st.form_submit_button("Disable")

            if disable:
                disable_emp = requests.post(f"{API_URL}/disable_account", json = {"empid": empid, "changed_by": st.session_state.user["empid"]})
                st.write(disable_emp.json()["message"])