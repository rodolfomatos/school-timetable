"""Schemas Pydantic para autenticação e utilizadores."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field

IntPK = Annotated[int, Field(gt=0)]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
    type: str | None = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: str = "student"
    institution_id: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    institution_id: str | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
