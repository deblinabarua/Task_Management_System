from flask import Flask, request, jsonify
from task_database import SessionLocal, Employee
from werkzeug.security import generate_password_hash, check_password_hash 

db = SessionLocal()

app = Flask(__name__)
@app.route("/homepage", methods = ["POST"])
def login():
    user_data = request.get_json()
    username = user_data["username"]
    password = user_data["password"]
    
    user_exist = db.execute(db.select(Employee).where(Employee.username == username)).scalar_one_or_none()
    if user_exist and check_password_hash(user_exist.password, password):
        return jsonify({"empid": user_exist.empid, "access": user_exist.access, "firstname": user_exist.firstname}), 200
    return jsonify({"message": "Wrong username or password."}), 401
