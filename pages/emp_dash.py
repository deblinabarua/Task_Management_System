
#Projects
    #Abstract tasks
        #Smaller tasks

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

curr_user = st.session_state.user["empid"]

st.title("Employee Dashboard", text_alignment = "center")
tab1, tab2, tab3= st.tabs(["Projects", "Add Tasks", "Profile"])

with tab1:
    view_projects = requests.get(f"{API_URL}/view_projects", json = {"empid": curr_user})
    if view_projects.status_code == 200: 
        for project in view_projects:
            st.header(project["title"])
            st.write("Members:")
            st.write(", ".join(project["members"]))
            st.write("Tasks")
            for task in project["tasks"]:
                st.write(task["task"])
                st.caption(", ".join(task["members"]))
    else:
        st.error("Couldn't load projects")

with tab2:
    curr_user = (st.session_state.user["empid"])
    get_projects = requests.post(f"{API_URL}/employee_projects", json = {"empid": curr_user}).json()
    with st.form("Add Task"):
        selected_project = st.selectbox("Choose Project", options = get_projects, format_func = lambda x: x["title"])
        task_title = st.text_input("Task")
        description = st.text_area("Description")
        add = st.form_submit_button("Add Task")
        
        if add:
            requests.post(f"{API_URL}/create_task", json = {"projectid": selected_project["projectid"], "created_by": curr_user, "title": task_title, "description": description})
            st.success("Task created")                       