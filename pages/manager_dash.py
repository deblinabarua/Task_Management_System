
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

st.title("Manager Dashboard", text_alignment = "center")
tab1, tab2, tab3= st.tabs(["Projects", "Add Projects", "Profile"])

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
                    st.caption(", ".join(task["members"]))
    else:
        st.error("Couldn't load projects")

with tab2:
    employees = requests.post(f"{API_URL}/employee_list").json()
    with st.form("Add Project"):
        st.header("Add New Project")
        
        title = st.text_input("Project Title")
        description = st.text_area("Description")

        selected_members = st.multiselect("Assign Members", options = [emp["empid"] for emp in employees], format_func = lambda x: next(emp["firstname"] + " " + emp["lastname"] for emp in employees if emp["empid"] == x))
        num_tasks = st.number_input("Number of Tasks", min_value = 0, step = 1)
        tasks = []
        for i in range(num_tasks):
            tasks.append(st.text_input(f"Task {i + 1}"))
        create = st.form_submit_button("Create")
        if create:
            create_project = requests.post(f"{API_URL}/add_project", json = {"created_by": curr_user, "title": title, "description": description, "members": selected_members, "tasks": tasks})
            if create_project.status_code == 200:
                st.success("Project Created")                     
                    

                    

