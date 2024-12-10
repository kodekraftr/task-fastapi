from sqlalchemy.orm import Session
from ..models import Task, User
from .schemas import TaskCreate
from datetime import date,datetime

def create_task(db: Session, task_data: TaskCreate, created_by_id: int):
    # Create the task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        created_by=created_by_id,
    )

    # Add assigned users
    assigned_users = db.query(User).filter(User.id.in_(task_data.assigned_users)).all()
    if not assigned_users:
        raise ValueError("Invalid user IDs provided")
    task.assigned_users = assigned_users

    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_tasks_for_user_by_date(db: Session, user_id: int, target_date: date):
    tasks = (
        db.query(Task)
        .filter(
            Task.assigned_users.any(id=user_id),
            Task.due_date >= target_date,
            Task.created_at <= target_date
          
        )
        .all()
    )
    for task in tasks:
        task.created_by = db.query(User).filter(User.id == task.created_by ).first().name
    return tasks    

def get_tasks_for_admin_by_date(db: Session, target_date: date):
    return (
        db.query(Task)
        .filter(
            Task.due_date >= target_date,
            Task.created_at <= target_date
        )
        .all()
    )