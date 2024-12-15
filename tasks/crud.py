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

def review_task(db: Session, task_id: int, rating: int, comments: str):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.rating = rating
    task.comments = comments
    db.commit()
    db.refresh(task)
    return task

def update_task_status(db: Session, task_id: int, user_id: int, status: str, details: Optional[str] = None):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.assigned_users.any(id=user_id))
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or user is not assigned to this task")
    task.status = status
    task.details = details
    db.commit()
    db.refresh(task)
    return task

def create_self_task(db: Session, user_id: int, title: str, description: str, date: date):
    # Check if any tasks are already assigned to the user for the given date
    existing_tasks = (
        db.query(Task)
        .filter(
            Task.due_date == date,
            Task.assigned_users.any(id=user_id),
        )
        .count()
    )
    if existing_tasks > 0:
        raise HTTPException(
            status_code=400,
            detail="You cannot create a self-task because tasks are already assigned for this date.",
        )

    # Create the self-task
    self_task = Task(
        title=title,
        description=description,
        status="pending",
        due_date=date,
        created_at=datetime.utcnow(),
        created_by=user_id,
        assigned_users=[],
    )
    self_task.assigned_users.append(db.query(User).get(user_id))  # Assign to current user

    db.add(self_task)
    db.commit()
    db.refresh(self_task)
    return self_task