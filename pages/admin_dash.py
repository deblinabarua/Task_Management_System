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

if "search_id" not in st.session_state:
    st.session_state.search_id = None

st.title("Admin Dashboard", text_alignment = "center")
tab1, tab2, tab3, tab4, tab5= st.tabs(["Add Employees", "Update Details", "Employee Logs", "Profile", "Disable Account"])

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
                        st.write(f"Employee's access privileges has been changed to {send_access.json()["access"]}")
                        del st.session_state.search_id
                    else:
                        st.error(f"{make_user.status_code}")
                    
