from fastapi import FastAPI
from taskApp.auth.routes import router as auth_router
from .db import Base, engine,SessionLocal
from .models import User
from taskApp.auth.utils import hash_password
import uvicorn

app = FastAPI(title="Task Management System")

# Create database tables
Base.metadata.create_all(bind=engine)

def create_admin_user():
    db = SessionLocal()
    try:
        existing_user = db.query(User).first()
        if not existing_user: 
            admin = User(
                username="admin@test.com",
                email="admin@test.com",
                name="Master",
                hashed_password=hash_password("12345"),  
                role="admin", 
                manager_id=None 
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Admin user created!")
    finally:
        db.close()

create_admin_user()

# Include routes
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8080,reload=True)