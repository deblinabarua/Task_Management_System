
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

if "logged_in" not in st.session_state:
    st.switch_page("task_front.py")

if st.session_state.user["access"] != "Employee":
    st.switch_page("task_front.py")

col1, col2 = st.columns([6,1])
with col1:
    st.title("Employee Dashboard")
with col2:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("task_front.py")

curr_user = st.session_state.user["empid"]


tab1, tab2 = st.tabs(["Projects", "Add Tasks"])

with tab1:
    view_projects = requests.post(f"{API_URL}/view_projects", json = {"empid": curr_user})
    
    
    if view_projects.status_code == 200: 
        projects = view_projects.json()
        if not projects:   
            st.info("No projects.")
        else:
            for project in projects:
                st.header(project["title"])
                st.write("Members:")
                st.write(", ".join(project["members"]))
                st.write("Tasks")
                for task in project["tasks"]:
                    
                    prefix = "↳ " if task["parent"] else ""
                    st.write(f'{prefix}{task["position"]}. {task["task"]}')
                    st.caption(", ".join(task["members"]))
    else:
        st.error("Couldn't load projects")

with tab2:
    curr_user = (st.session_state.user["empid"])
    get_projects = requests.post(f"{API_URL}/employee_projects", json = {"empid": curr_user}).json()
    with st.form("Add Task"):
        project_name = st.selectbox("Project", get_projects, format_func = lambda x:x["title"])
        title = st.text_input("Task Title")
        description = st.text_area("Description")
        position = st.number_input("Position",min_value = 1, value = 1)
        parent = st.text_input("Parent Task ID (optional)")
        
        submit = st.form_submit_button("Create Task")
        if submit:
            add = requests.post(f"{API_URL}/create_task", json = {"projectid": project_name["projectid"], "title": title, "description": description, "position": position, "parent_task": int(parent) if parent else None, "created_by": curr_user, "members": [curr_user]})
            if add.status_code == 200:
                st.success("Task added")
                st.rerun()
            else:
                st.error(add.json()["message"])        