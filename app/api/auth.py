from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.utils.hashing import Hasher
from app.db.models import User
from app.schemas.user import UserCreate, UserResponse, GoogleLoginRequest
from app.schemas.token import Token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import secrets

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = User(
        email=user_in.email,
        password_hash=Hasher.get_password_hash(user_in.password),
        role="user" 
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not Hasher.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(
            data={"sub": user.email}
        ),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(deps.get_db)
) -> Any:
    # Simplified refresh logic
    try:
        payload = security.jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
    except security.jwt.JWTError:
         raise HTTPException(status_code=403, detail="Invalid refresh token")
         
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        ),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/google", response_model=Token)
def google_login(
    login_data: GoogleLoginRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    try:
        # Verify token
        # Specify the CLIENT_ID of the app that accesses the backend:
        id_info = id_token.verify_oauth2_token(
            login_data.token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        # userid = id_info['sub']
        email = id_info['email']
    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create user
        # Generate a random password since they use Google
        random_password = secrets.token_urlsafe(16)
        user = User(
            email=email,
            password_hash=Hasher.get_password_hash(random_password),
            role="user" 
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(
            data={"sub": user.email}
        ),
        "token_type": "bearer",
    }
