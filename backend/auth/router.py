
from string import ascii_letters
from random import choice

from passlib.context import CryptContext

from fastapi import APIRouter, Depends
from sqlalchemy import Select
from sqlalchemy.orm import Session

from database import get_db

from auth.schemas import AuthUser, AuthStatus
from auth.models import User


router = APIRouter()

pwd_context = CryptContext(
    schemes=["sha256_crypt"],
)


@router.post("/registration", response_model = AuthStatus)
def post_registration(payload: AuthUser, db: Session = Depends(get_db)):
    query = Select(User).where(User.username == payload.username)
    user = db.scalar(query)
    if user:
        return AuthStatus(
            status = "error",
            token = None,
            error = "User already exists",
        )

    token = "".join(choice(ascii_letters) for _ in range(32))

    user = User(
        username = payload.username,
        password = pwd_context.hash(payload.password),
        token = token,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthStatus(
        status = "ok",
        token = token,
        error = None,
    )


@router.post("/login", response_model = AuthStatus)
def post_login(payload: AuthUser, db: Session = Depends(get_db)):
    query = Select(User).where(User.username == payload.username)
    user = db.scalar(query)
    if not user:
        return AuthStatus(
            status = "error",
            token = None,
            error = "User not found",
        )

    if not pwd_context.verify(payload.password, user.password):
        return AuthStatus(
            status = "error",
            token = None,
            error = "Wrong password",
        )

    return AuthStatus(
        status = "ok",
        token = user.token,
        error = None,
    )
