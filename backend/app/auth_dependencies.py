import os
from datetime import datetime, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User

SECRET_KEY = os.getenv("SCRAPSYNC_SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="Authentication is not configured",
        )

    credentials_error = HTTPException(
        status_code=401,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")
        business_id = payload.get("business_id")
        expires_at = payload.get("exp")

        if not user_id or not business_id or not expires_at:
            raise credentials_error

        if datetime.fromtimestamp(
            expires_at, tz=timezone.utc
        ) <= datetime.now(timezone.utc):
            raise credentials_error

        user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )

        if not user or user.business_id != int(business_id):
            raise credentials_error

        return user

    except (jwt.InvalidTokenError, ValueError, TypeError, OverflowError):
        raise credentials_error