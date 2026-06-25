
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

if ("logged_in" not in st.session_state):
    st.switch_page("task_front.py")

curr_user = st.session_state.user["empid"]

st.title("Manager Dashboard", text_alignment = "center")
tab1, tab2, tab3= st.tabs(["Projects", "Add Projects", "Add Tasks"])

with tab1:
    view_projects = requests.post(f"{API_URL}/view_projects", json = {"empid": curr_user})
    
    
    if view_projects.status_code == 200: 
        if not view_projects.json():   #Make json in one variable otherwise it will parse twice
            st.info("No projects.")
        else:
            for project in view_projects.json():
                st.header(project["title"])
                st.write("Members:")
                st.write(", ".join(project["members"]))
                st.write("Tasks")
                for task in project["tasks"]:
                    st.write(task["task"])
                    prefix = "↳ " if task["parent"] else ""
                    st.write(f'{prefix}{task["position"]}. {task["task"]}')
                    st.caption(", ".join(task["members"]))
    else:
        st.error("Couldn't load projects")

with tab2:
    employees = requests.post(f"{API_URL}/employee_list").json()
    with st.form("Add Project"):
        st.header("Add New Project")
        
        title = st.text_input("Project Title")
        description = st.text_area("Description")

        available_members = [emp for emp in employees if emp["empid"] != curr_user]
        selected_members = st.multiselect("Assign Members", options = [emp["empid"] for emp in available_members], format_func = lambda x: next(emp["firstname"] + " " + emp["lastname"] for emp in employees if emp["empid"] == x))
        create = st.form_submit_button("Create")
        if create:
            create_project = requests.post(f"{API_URL}/add_project", json = {"created_by": curr_user, "title": title, "description": description, "members": selected_members})
            if create_project.status_code == 200:
                st.success("Project Created") 
                st.rerun()                    
                    
with tab3:
    projects = requests.post(f"{API_URL}/employee_projects", json = {"empid": curr_user}).json()
    employees = requests.post(f"{API_URL}/employee_list").json()

    with st.form("add_task"):
        st.header("Add Task")
        project = st.selectbox("Project", projects, format_func = lambda x:x["title"])
        title = st.text_input("Task Title")
        description = st.text_area("Description")
        position = st.number_input("Position",min_value = 1, value = 1)
        parent = st.text_input("Parent Task ID (optional)")
        members = st.multiselect("Assign Employees", options = [e["empid"]for e in employees], format_func = lambda x:next(f'{e["firstname"]} {e["lastname"]}' for e in employees if e["empid"] == x))
        submit = st.form_submit_button("Create Task")
        if submit:
            add = requests.post(f"{API_URL}/create_task", json = {"projectid": project["projectid"], "title": title, "description": description, "position": position, "parent_task": int(parent) if parent else None, "created_by": curr_user, "members": members})
            if add.status_code == 200:
                st.success("Task added")
                st.rerun()
            else:
                st.error(add.json()["message"])