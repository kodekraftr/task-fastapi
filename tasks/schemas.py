from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date,datetime

class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_users: List[int]  
    due_date: date

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    due_date: date
    created_at: datetime  
    assigned_users: List[str]  

    class Config:
        from_attributes = True 


# Schema for updating task status and providing task details
class TaskUpdate(BaseModel):
    status: Optional[str] = None  # "Pending", "In Progress", "Completed", etc.
    comment: Optional[str] = None


# Basic information about a task
class TaskBasicInfo(BaseModel):
    id: int
    title: str
    description: str
    status: str
    due_date: date
    rating:Optional[float] 
    status:str
    comments:Optional[str] 
    class Config:
        from_attributes = True

# Schema for tasks grouped by user (Admin View)
class TasksByUser(BaseModel):
    username: str  # Username of the user to whom tasks are assigned
    tasks: List[TaskBasicInfo]  # List of tasks assigned to the user


# Response schema for tasks grouped by users (Admin View)
class AdminTasksResponse(BaseModel):
    date: date
    tasks: List[TasksByUser]

    class Config:
        from_attributes = True


# Response schema for tasks for the current user (User View)
class UserTasksResponse(BaseModel):
    date: date
    tasks: List[TaskResponse]

    class Config:
        from_attributes = True   

class TaskReview(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating should be between 1 and 5")
    comments: str = Field(..., max_length=255, description="Comments about the task")

class TaskReviewResponse(BaseModel):
    message: str
    task_id: int
    rating: int
    comments: str

class TaskStatusUpdate(BaseModel):
    status: str = Field(..., regex="^(pending|in-progress|completed)$", description="Valid status values are 'pending', 'in-progress', or 'completed'")
    details: Optional[str] = Field(None, max_length=255, description="Additional details about the status update")

class TaskStatusResponse(BaseModel):
    message: str
    task_id: int
    status: str
    details: Optional[str]

    class Config:
        from_attributes = True