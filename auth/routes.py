from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from taskApp.db import get_db
from taskApp.models import User
from taskApp.auth.schemas import UserCreate, UserLogin, Token,UserData,UserUpdate
from taskApp.auth.utils import hash_password, verify_password, create_access_token
from taskApp.auth.dependencies import is_admin,get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])



# Register a new user
@router.post("/register/", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(is_admin)):
    # Check if the email or username already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Hash the password
    hashed_password = hash_password(user.password)

    # Create the new user
    new_user = User(
        username=user.email,
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        manager_id=current_user.id if user.role == "user" else None
    )

    # Add user to the database and commit
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

# Login a user
@router.post("/login/", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    print(user)
    if user.email:
        db_user = db.query(User).filter(User.email == user.email).first()
    elif user.username:
        db_user = db.query(User).filter(User.username == user.username).first()
    else:
        raise HTTPException(status_code=400, detail="Either username or email must be provided")

    # If no user is found or password is incorrect, raise an error
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username/email or password")

    access_token = create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me/",response_model=UserData)
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve the current authenticated user's profile
    """
    print(current_user)
    if current_user.role != "admin":
        # Assuming the `User` table has a reference to the manager (manager_id)
        manager = db.query(User).filter(User.id == current_user.manager_id).first()
        if manager:
            return UserData(
                id=current_user.id,
                email=current_user.email,
                name=current_user.name,
                role=current_user.role,
                is_active=current_user.is_active,
                manager_name=manager.name 
            )
        else:
            raise HTTPException(status_code=404, detail="Manager not found")
    
    # If the user is an admin, just return the user data without manager information
    return UserData(
        id=current_user.id,
        name = current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )

@router.put("/me/", response_model=UserData)
def update_user_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update the current authenticated user's profile details.
    """
    # Check if the email or username already exists (except for the current user)
    existing_user = db.query(User).filter((User.email == user_update.email)).first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already taken")

    # Update fields
    if user_update.name :
        current_user.name = user_update.name
    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        current_user.hashed_password = hash_password(user_update.password)

    # Commit the changes to the database
    db.commit()
    db.refresh(current_user)

    return current_user    
