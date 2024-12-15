from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from taskApp.auth.dependencies import get_db, get_current_user
from .schemas import *
from .crud import *
from ..models import User

router = APIRouter()

from fastapi.encoders import jsonable_encoder

@router.post("/task", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin-only endpoint to create a new task.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")

    try:
        created_task = create_task(db=db, task_data=task, created_by_id=current_user.id)
        
        # Transform the task into the expected response
        response = jsonable_encoder(created_task)
        response["assigned_users"] = [user.username for user in created_task.assigned_users]  # Extract usernames
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/task/user/")
def get_user_tasks(
    target_date: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch tasks for the current user on a specific date.
    """
    tasks = get_tasks_for_user_by_date(db, current_user.id, target_date)
    return {
        "date": target_date,
        "tasks": tasks  # Each task automatically serialized as `TaskResponse`
    }

@router.get("/task/admin/",response_model=AdminTasksResponse)
def get_admin_tasks(
    target_date: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch tasks for all users grouped by user for a specific date.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")

    tasks = get_tasks_for_admin_by_date(db, target_date)

    # Group tasks by username
    grouped_tasks = {}
    for task in tasks:
        for user in task.assigned_users:
            if user.username not in grouped_tasks:
                grouped_tasks[user.username] = []
            grouped_tasks[user.username].append(task)

    return {
        "date": target_date,
        "tasks": [
            {"username": username, "tasks": user_tasks}
            for username, user_tasks in grouped_tasks.items()
        ],
    }

@router.post("/{task_id}/review/", response_model=TaskReviewResponse, status_code=status.HTTP_200_OK)
def review_task_endpoint(
    task_id: int,
    review: TaskReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admin reviews a task by providing a rating and comments.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can review tasks")
    
    task = review_task(db, task_id, review.rating, review.comments)
    return {
        "message": "Task reviewed successfully",
        "task_id": task.id,
        "rating": task.rating,
        "comments": task.comments,
    }

@router.put("/{task_id}/status/", response_model=TaskStatusResponse, status_code=status.HTTP_200_OK)
def update_task_status_endpoint(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the status of a task assigned to the current user.
    """
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Only users can update task status")
    
    updated_task = update_task_status(
        db,
        task_id=task_id,
        user_id=current_user.id,
        status=status_update.status,
        details=status_update.details,
    )
    return {
        "message": "Task status updated successfully",
        "task_id": updated_task.id,
        "status": updated_task.status,
        "details": updated_task.details,
    }

@router.post("/self-task/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_self_task_endpoint(
    self_task: SelfTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint for users to create a self-task if no tasks are assigned for the given date.
    """
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Only users can create self-tasks")

    created_task = create_self_task(
        db, 
        user_id=current_user.id, 
        title=self_task.title, 
        description=self_task.description, 
        date=self_task.date
    )
    return created_task
