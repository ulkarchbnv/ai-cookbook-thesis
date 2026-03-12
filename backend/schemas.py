from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class SavedRecipeCreate(BaseModel):
    title: str
    ingredients: list[str]
    steps: list[str]
    nutrition: dict


class SavedRecipeResponse(BaseModel):
    id: int
    title: str
    ingredients: str
    steps: str
    nutrition: str

    class Config:
        from_attributes = True