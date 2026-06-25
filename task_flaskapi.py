from flask import Flask, request, jsonify
from task_database import SessionLocal, Employee, Tasks, Projects, ProjectAssignment, TaskAssignment
from werkzeug.security import generate_password_hash, check_password_hash 
from sqlalchemy import select
from task_function import generate_temp_pass, generate_username


app = Flask(__name__)
@app.route("/homepage", methods = ["POST"])
def login():
    
    with SessionLocal() as db:
        user_data = request.get_json()
        username = user_data["username"]
        password = user_data["password"]
        
        user_exist = db.execute(select(Employee).where(Employee.username == username)).scalar_one_or_none()
        if user_exist and check_password_hash(user_exist.password, password):
            return jsonify({"empid": user_exist.empid, "access": user_exist.access, "firstname": user_exist.firstname}), 200
        return jsonify({"message": "Wrong username or password."}), 401
    

@app.route("/addemp", methods = ["POST"])
def add_emp():
    with SessionLocal() as db:

        new_user = request.get_json() #check user existence later
        temp_pass = generate_temp_pass()
        user_adding = Employee(firstname = new_user["firstname"], lastname = new_user["lastname"], access = new_user["access"], email = new_user["email"], mobile = new_user["mobile"], username = generate_username(new_user["firstname"], new_user["lastname"]), password = generate_password_hash(temp_pass))
        db.add(user_adding)
        db.commit()
        return jsonify({"message": "Employee has been added", "username": user_adding.username, "temp_password": temp_pass}), 200

@app.route("/getaccess", methods = ["POST"])
def get_emp_access():
    with SessionLocal() as db:
        get_empid = request.get_json()
        get_access = db.execute(select(Employee).where(Employee.empid == get_empid["empid"])).scalar_one_or_none()
        if get_access:
            return jsonify({"message": "Employee found.", "access": get_access.access, "empid": get_access.empid}), 200
        return jsonify({"message": "Wrong employee ID."}), 400

@app.route("/sendaccess", methods = ["POST"])
def update_emp_access():
    with SessionLocal() as db:
        new_access = request.get_json()
        update_access = db.execute(select(Employee).where(Employee.empid == new_access["empid"]))
        if update_access:
            update_access.access = new_access["access"]
            db.commit()
            return jsonify({"message": "Access privilege updated.", "access": new_access["access"]})
        else:
            return jsonify({"message": "Employee not found"}), 404

@app.route("/view_projects", methods = ["POST"])
def view_projects():
    with SessionLocal() as db:
        get_empid = request.get_json()
        projects = db.execute(select(Projects).join(ProjectAssignment, Projects.projectid == ProjectAssignment.projectid).where(ProjectAssignment.empid == get_empid["empid"])).scalars().all()
        project_api = []
        for project in projects:
            members = db.execute(select(Employee.firstname, Employee.lastname).join(ProjectAssignment, Employee.empid == ProjectAssignment.empid).where(ProjectAssignment.projectid == project.projectid)).all()
            members_list = []
            for first, last in members:
                members_list.append(f"{first} {last}")
            tasks = db.execute(select(Tasks).where(Tasks.projectid == project.projectid)).scalars().all()
            task_list = []
            for task in tasks:
                assigned = db.execute(select(Employee.firstname, Employee.lastname).join(TaskAssignment, Employee.empid == TaskAssignment.empid).where(TaskAssignment.taskid == task.taskid).order_by(Tasks.position.is_(None), Tasks.position)).all()
                assigned_list = []
                for first, last in assigned:
                    assigned_list.append(f"{first} {last}")
                task_list.append({"task": task.title, "members": assigned_list})
            project_api.append({"title": project.title, "members": members_list, "tasks": task_list})
        return jsonify(project_api)

@app.route("/employee_list", methods = ["POST"])
def employee_list():
    with SessionLocal() as db:
        emp = db.execute(select(Employee.empid, Employee.firstname, Employee.lastname)).all()
        emp_list = []
        for empid, firstname, lastname in emp:
            emp_list.append({"empid": empid, "firstname": firstname, "lastname": lastname})
        return jsonify(emp_list)

@app.route("/add_project", methods = ["POST"])
def create_project():
    with SessionLocal() as db:
        project_details = request.get_json()
        project = Projects(title = project_details["title"], description = project_details["description"], created_by = project_details["created_by"])
        db.add(project)
        db.flush()
        for member in project_details["members"]:
            db.add(ProjectAssignment(projectid = project.projectid, empid = int(member), role = "Member"))
        db.add(ProjectAssignment(projectid = project.projectid, empid = project_details["created_by"], role = "Owner"))

        if project_details["tasks"]:
            for i, task in enumerate(project_details["tasks"], start = 1):
                new_task = Tasks(title = task.strip(), position = i, status = "Not started", created_by = project_details["created_by"], projectid = project.projectid)
                db.add(new_task)
                db.flush()
        db.commit()
        return jsonify({"message": "Project created"})
    
@app.route("/employee_projects", methods = ["POST"])
def employee_projects():
     with SessionLocal() as db:
        emp_id = request.get_json()
        projects = db.execute(select(Projects.projectid, Projects.title, Projects.description).join(ProjectAssignment, Projects.projectid == ProjectAssignment.projectid).where(ProjectAssignment.empid == emp_id["empid"])).all()
        project_list = []
        for pid, title, description in projects:
            project_list.append({"projectid": pid, "title": title, "description": description})
        return jsonify(project_list)
    
@app.route("/create_task", methods = ["POST"])
def create_task():
    with SessionLocal() as db:
        new_task = request.get_json()
        task = Tasks(projectid = new_task["projectid"], title = new_task["title"], description = new_task["description"], status = "Not started", created_by = new_task["created_by"], position = 0)
        db.add(task)
        db.commit()
        return jsonify({"message": "Task created"})