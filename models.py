from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Date,Table, DateTime, Float
from datetime import datetime,date
from .db import Base
from sqlalchemy.orm import relationship

task_user_association = Table(
    'task_user_association',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String,nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager = relationship("User", remote_side=[id])
    tasks = relationship("Task", secondary=task_user_association, back_populates="assigned_users")



class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="Pending") 
    rating = Column(Float, nullable=True)  
    comments = Column(Text, nullable=True)  
    due_date = Column(Date, nullable=False)
    created_at = Column(Date, default=date.today)

    assigned_users = relationship("User", secondary=task_user_association, back_populates="tasks")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  

  