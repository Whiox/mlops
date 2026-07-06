
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Select
from sqlalchemy.orm import Session

from database import get_db
from auth.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    query = Select(User).where(User.token == token)
    user = db.scalar(query)

    if not user:
        raise HTTPException(401, detail="Invalid auth token")

    return user
