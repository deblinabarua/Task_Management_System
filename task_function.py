from task_database import SessionLocal, Employee
from sqlalchemy import select
import secrets
import string


def generate_username(firstname, lastname):
    with SessionLocal() as db:
        base = (firstname.lower() + lastname[0].lower())
        counter = 2
        check_name = base
        while db.execute(select(Employee).where(Employee.username == check_name))).scalar_one_or_none():
            check_name = f"{base}{counter}"
            counter += 1
    return check_name

def generate_temp_pass():
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(chars) for _ in range(10))