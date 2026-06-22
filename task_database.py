from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum, Boolean
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL) #stores connection to postgres

SessionLocal = sessionmaker(bind = engine) 

class Base(DeclarativeBase):
    pass

class Employee(Base):
    __tablename__ = "employee"
    empid: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    firstname: Mapped[str] = mapped_column(String(40), nullable = False)
    lastname: Mapped[str] = mapped_column(String(40))
    username: Mapped[str] = mapped_column(String(40), unique = True, nullable = False)
    password: Mapped[str] = mapped_column(String(225), nullable = False)
    last_pass_update: Mapped[datetime] = mapped_column(DateTime, default = lambda: datetime.now(timezone.utc))
    change_pass: Mapped[bool] = mapped_column(Boolean, default = True)
    access: Mapped[str] = mapped_column(Enum('Admin', 'Manager', 'AssistManager', 'Employee', name = 'access_enum'), nullable = False)
    email: Mapped[str] = mapped_column(String(100), nullable = False)
    mobile: Mapped[str] = mapped_column(String(20), nullable = False)
    created_on: Mapped[datetime] = mapped_column(DateTime, default = lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default = True) 

class Tasks(Base):
    __tablename__ = "tasks"
    taskid: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    parent_task: Mapped[int | None] = mapped_column(ForeignKey("tasks.taskid"), nullable = True)
    position: Mapped[int] = mapped_column(nullable = False)
    title: Mapped[str] = mapped_column(String(50), nullable  = False)
    description: Mapped[str] = mapped_column(String(1000), nullable = True)
    status: Mapped[str] = mapped_column(Enum('Not started', 'Just started', 'In the middle of doing', 'Almost done', 'Completed', name = 'task_stat'), nullable = False)
    created_on: Mapped[datetime] = mapped_column(DateTime, default = lambda: datetime.now(timezone.utc))
    created_by: Mapped[int] = mapped_column(ForeignKey("employee.empid"), nullable = False)
    assigned_to: Mapped[int] = mapped_column(ForeignKey("employee.empid"), nullable = True)
    updated_on: Mapped[datetime] = mapped_column(DateTime, default = lambda: datetime.now(timezone.utc), onupdate = lambda: datetime.now(timezone.utc)) #updates automatically when user updates and doesn't have to be manually coded
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable = True)
    completed_on: Mapped[datetime | None] = mapped_column(DateTime, nullable = True)

class Logs(Base):
    __tablename__ = "logs"
    logid: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    task_changed: Mapped[int | None] = mapped_column(ForeignKey("tasks.taskid"), nullable = True)
    changed_by: Mapped[int] = mapped_column(ForeignKey("employee.empid"), nullable = False)
    event: Mapped[str] = mapped_column(Enum("LOGIN", "LOGOUT", "CREATE_TASK", "UPDATE_TASK", "DELETE_TASK", "CHANGE_STATUS", "CHANGE_PASSWORD", name = "change_event"))
    details: Mapped[str | None] = mapped_column(String(500), nullable = True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default = lambda: datetime.now(timezone.utc), nullable = False)
