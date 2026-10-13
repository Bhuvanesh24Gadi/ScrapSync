import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Business, User

router = APIRouter(prefix="/auth", tags=["Authentication"])

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SCRAPSYNC_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SCRAPSYNC_SECRET_KEY environment variable is not configured"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class RegisterRequest(BaseModel):
    business_name: str = Field(min_length=2, max_length=150)
    industry: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "business_id": user.business_id,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", status_code=201)
def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = str(body.email).strip().lower()

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists",
        )

    try:
        business = Business(
            name=body.business_name.strip(),
            industry=body.industry.strip(),
            location=body.location.strip(),
        )
        db.add(business)
        db.flush()

        user = User(
            email=email,
            password_hash=password_hash.hash(body.password),
            business_id=business.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "message": "Account registered successfully",
            "user_id": user.id,
            "business_id": user.business_id,
            "email": user.email,
        }

    except Exception:
        db.rollback()
        raise


@router.post("/login")
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    email = str(body.email).strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user or not password_hash.verify(
        body.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_MINUTES * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "business_id": user.business_id,
            "business_name": user.business.name,
        },
    }