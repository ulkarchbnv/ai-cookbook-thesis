from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class NutritionEstimate(BaseModel):
    calories: int = Field(ge=0)
    protein: str
    carbs: str
    fat: str


class RecipeRequest(BaseModel):
    ingredients: list[str]
    preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)


class RecipeResponse(BaseModel):
    title: str
    ingredients: list[str]
    preferences: list[str]
    allergies: list[str]
    steps: list[str]
    nutrition_estimate: NutritionEstimate


class SavedRecipeCreate(BaseModel):
    title: str
    ingredients: list[str]
    preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    steps: list[str]
    nutrition: NutritionEstimate


class SavedRecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    ingredients: list[str]
    preferences: list[str]
    allergies: list[str]
    steps: list[str]
    nutrition: NutritionEstimate
    created_at: datetime
