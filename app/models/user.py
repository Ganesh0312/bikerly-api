from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import uuid4
from beanie import Document

class UserBase(BaseModel):
    uuid: str
    email: EmailStr
    user_name: str
    phone_number: str
    country_code: str
    name: Optional[str] = None
    display_name: str = Field(..., min_length=1, max_length=50)
    role: Literal["rider", "admin"] = "rider"
    is_active: bool = True
    is_verified: bool = False
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    social_links: Optional[dict[str, str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class User(Document):
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr
    user_name: str
    phone_number: str
    country_code: str
    name: Optional[str] = None
    display_name: str = Field(..., min_length=1, max_length=50)
    role: Literal["rider", "admin"] = "rider"
    is_active: bool = True
    is_verified: bool = False
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    social_links: Optional[dict[str, str]] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    hashed_password: str

    class Settings : 
        name = "users"

class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    phone_number: str
    country_code: str
    password: str
    name: Optional[str] = None
    display_name: str = Field(..., min_length=1, max_length=50)
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(UserBase):
    id: str = Field(alias="id")

    class Config:
        populate_by_name = True
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"