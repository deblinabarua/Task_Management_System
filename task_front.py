import streamlit as st
import requests

st.set_page_config(
    initial_sidebar_state="collapsed",
    layout = "wide"
)
'''
if st.session_state.get("logged_in"):
    redirect = st.session_state.get("last_page", "task_front.py")
    st.switch_page(redirect)
'''



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
            username = st.text_input("Enter username: ")
            password = st.text_input("Enter password: ", type = "password")

            login = st.form_submit_button("Login")

            if login:
                if not username or not password:
                    st.error("Please fill all fields.")
                else:
                    send_user = requests.post("render_link", json = {"username": username, "password": password})
                    
                    if send_user.status_code == 200:
                        user = send_user.json()
                        st.session_state.logged_in = True
                        st.session_state.user = user

                        if st.session_state.user['access'] == 'Admin':
                            st.switch_page('pages/admin_dash')
                        elif st.session_state.user['access'] == 'Manager':
                            st.switch_page('pages/manager_dash')
                        elif st.session_state.user['access'] == 'AssistManager':
                            st.switch_page('pages/assist_dash')
                        else:
                            st.switch_page('pages/emp_dash')
                    else:
                        st.error(send_user.json()["message"])