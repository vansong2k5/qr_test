from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..deps import get_current_user, get_db, require_role
from ..models.user import User
from ..schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, Token, UserOut
from .security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, password_hash=get_password_hash(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshRequest):
    try:
        decoded = jwt.decode(payload.refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        sub = int(decoded.get("sub"))
    except (JWTError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    return Token(access_token=create_access_token(sub), refresh_token=create_refresh_token(sub))


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user
