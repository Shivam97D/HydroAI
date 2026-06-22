"""Auth endpoints: register, login, me."""
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from database.mongo import get_mongo_db
from services.auth_service import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth")
bearer = HTTPBearer(auto_error=False)


class RegisterBody(BaseModel):
    name: str
    email: EmailStr
    password: str
    location: str = ""


class LoginBody(BaseModel):
    email: EmailStr
    password: str


async def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
):
    if not creds:
        raise HTTPException(401, "Not authenticated")
    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")
    db = get_mongo_db()
    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(401, "User not found")
    return user


@router.post("/register", status_code=201)
async def register(body: RegisterBody):
    if len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    db = get_mongo_db()
    existing = await db.users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(409, "Email already registered")
    doc = {
        "name": body.name.strip(),
        "email": body.email.lower(),
        "password_hash": hash_password(body.password),
        "location": body.location.strip(),
        "created_at": datetime.now(timezone.utc),
        "role": "user",
    }
    result = await db.users.insert_one(doc)
    token = create_access_token({"sub": str(result.inserted_id), "email": doc["email"]})
    return {
        "token": token,
        "user": {
            "id": str(result.inserted_id),
            "name": doc["name"],
            "email": doc["email"],
            "location": doc["location"],
            "role": doc["role"],
        },
    }


@router.post("/login")
async def login(body: LoginBody):
    db = get_mongo_db()
    user = await db.users.find_one({"email": body.email.lower()})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})
    return {
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "location": user.get("location", ""),
            "role": user.get("role", "user"),
        },
    }


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "email": current_user["email"],
        "location": current_user.get("location", ""),
        "role": current_user.get("role", "user"),
    }
