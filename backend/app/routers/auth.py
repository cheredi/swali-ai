"""Authentication endpoints for JWT-based identity."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.storage import get_store

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: EmailStr


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest) -> AuthResponse:
    store = get_store()
    existing = await asyncio.to_thread(store.get_user_by_email, request.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    password_hash = hash_password(request.password)
    user = await asyncio.to_thread(store.create_user, request.email, password_hash)
    token = create_access_token(user_id=user["id"], email=user["email"])
    return AuthResponse(access_token=token, user_id=user["id"], email=user["email"])


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    store = get_store()
    user = await asyncio.to_thread(store.get_user_by_email, request.email)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user_id=user["id"], email=user["email"])
    return AuthResponse(access_token=token, user_id=user["id"], email=user["email"])


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user
