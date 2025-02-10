from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.config import SECRET_KEY, ALGORITHM
import jwt
import os
from app.db import get_db, User
from datetime import datetime, timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Token expires in 15 minutes
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    new_user = User(username=username, role="viewer")   # Default role
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.check_password(form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    token = create_access_token({"sub": user.username, "role": user.role}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    from jwt import ExpiredSignatureError, DecodeError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload["sub"], "role": payload.get("role", "viewer")}
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_role(*roles: str):
    def role_dependency(user: dict = Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return role_dependency

@router.get("/owner")
def owner_route(user: dict = Depends(require_role("owner"))):
    return {"message": f"Welcome, {user['username']}! You have full access."}

@router.get("/collaborator")
def collaborator_route(user: dict = Depends(require_role("owner", "collaborator"))):
    return {"message": f"Welcome, {user['username']}! You can view and edit content."}

@router.get("/viewer")
def viewer_route(user: dict = Depends(require_role("owner", "collaborator", "viewer"))):
    return {"message": f"Welcome, {user['username']}! You have read-only access."}

@router.delete("/delete/{username}")
def delete_user(username: str, user: dict = Depends(require_role("owner")), db: Session = Depends(get_db)):
    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(target_user)
    db.commit()
    return {"message": f"User {username} deleted successfully."}