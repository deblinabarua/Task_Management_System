from flask import Flask, request, jsonify
from task_database import SessionLocal, Employee, Tasks, Projects, ProjectAssignment, TaskAssignment, Logs
from werkzeug.security import generate_password_hash, check_password_hash 
from sqlalchemy import select
from task_function import generate_temp_pass, generate_username
from datetime import datetime, timezone, timedelta


app = Flask(__name__)
@app.route("/homepage", methods = ["POST"])
def login():
    
    with SessionLocal() as db:
        user_data = request.get_json()
        username = user_data["username"]
        password = user_data["password"]
        
        user_exist = db.execute(select(Employee).where(Employee.username == username)).scalar_one_or_none()

        if not user_exist:
            return jsonify({"message": "Wrong username or password."}), 401
        if not user_exist.is_active:
            return jsonify({"message": "Account disabled. Contact admin."}), 403
        if not check_password_hash(user_exist.password, password):
            return jsonify({"message": "Wrong username or password."}), 401
        else:
            db.add(Logs(changed_by = user_exist.empid, event = "LOGIN", details = "User logged in."))
            last_update = user_exist.last_pass_update
            if last_update.tzinfo is None:
                last_update = last_update.replace(tzinfo = timezone.utc)
            days = datetime.now(timezone.utc) - last_update
            if days >= timedelta(days = 30):
                user_exist.change_pass = True
            db.commit()
            return jsonify({"empid": user_exist.empid, "access": user_exist.access, "firstname": user_exist.firstname, "change_pass": user_exist.change_pass}), 200
    

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
        update_access = db.execute(select(Employee).where(Employee.empid == new_access["empid"])).scalar_one_or_none()
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
            tasks = db.execute(select(Tasks).where(Tasks.projectid == project.projectid).order_by(Tasks.position.is_(None), Tasks.position)).scalars().all()
            task_list = []
            for task in tasks:
                assigned = db.execute(select(Employee.firstname, Employee.lastname).join(TaskAssignment, Employee.empid == TaskAssignment.empid).where(TaskAssignment.taskid == task.taskid)).all()
                assigned_list = []
                for first, last in assigned:
                    assigned_list.append(f"{first} {last}")
                task_list.append({"task": task.title, "parent": task.parent_task, "position": task.position, "members": assigned_list})
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

        db.add(ProjectAssignment(projectid = project.projectid, empid = project_details["created_by"], role = "Owner"))
        for member in project_details["members"]:
            db.add(ProjectAssignment(projectid = project.projectid, empid = int(member), role = "Member"))
        
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
    
@app.route("/create_task", methods=["POST"])
def create_task():
    with SessionLocal() as db:
        new_task = request.get_json()
        task = Tasks(projectid = new_task["projectid"], title = new_task["title"], description = new_task["description"], parent_task = new_task["parent_task"], position = new_task["position"], status = "Not started", created_by = new_task["created_by"])
        db.add(task)
        db.flush()

        for member in new_task["members"]:
            db.add(TaskAssignment(taskid = task.taskid, empid = member))

        db.commit()
        return jsonify({"message": "Task created"})
    
@app.route("/change_password", methods = ["POST"])
def change_pass():
    with SessionLocal() as db:
        emp = request.get_json()
        search_emp = db.execute(select(Employee).where(Employee.empid == emp["empid"])).scalar_one_or_none()
        if not search_emp:
            return jsonify({"message": "Employee not found."}), 404
        if not check_password_hash(search_emp.password, emp["old"]):
            return jsonify({"message": "Old password is incorrect."}), 401
        else:
            search_emp.password = generate_password_hash(emp["new"])
            search_emp.last_pass_update = datetime.now(timezone.utc)
            search_emp.change_pass = False
            db.add(Logs(changed_by = search_emp.empid, event = "CHANGE_PASSWORD", details = "Password changed."))
            db.commit()
            return jsonify({"message": "Password updated."}), 200
        
@app.route("/disable_account", methods = ["POST"])
def disable_account():
    with SessionLocal() as db:
        get_emp = request.get_json()
        emp = db.execute(select(Employee).where(Employee.empid == get_emp["empid"])).scalar_one_or_none()
        if not emp:
            return jsonify({"message": "Employee not found."}), 404
        if emp.username == "admin":
            return jsonify({"message": "Cannot disable admin."}), 400
        
        emp.is_active = False
        db.add(Logs(changed_by = get_emp["changed_by"], event = "UPDATE_TASK", details = f"Disabled employee {emp.empid}"))
        db.commit()
        return jsonify({"message": "Account disabled."})