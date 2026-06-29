from task_database import SessionLocal, Employee
from sqlalchemy import select
import secrets
import string
import time
import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL")

def generate_username(firstname, lastname):
    with SessionLocal() as db:
        base = (firstname.lower() + lastname[0].lower())
        counter = 2
        check_name = base
        while db.execute(select(Employee).where(Employee.username == check_name)).scalar_one_or_none():
            check_name = f"{base}{counter}"
            counter += 1
    return check_name

def generate_temp_pass():
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(chars) for _ in range(10))

def api_post(endpoint, payload = None, retries = 2):
    for attempt in range(retries):
        try:
            with st.spinner("Starting server, please wait."):
                response = requests.post(f"{API_URL}{endpoint}", json = payload, timeout = 30)
                return response
        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                st.warning("Server is waking up. Please wait.")
                time.sleep(5)

    st.error("Server is taking longer than expected. Please try again later.")
    return None