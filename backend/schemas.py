from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserProfileUpdate(BaseModel):
    preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)


class NutritionEstimate(BaseModel):
    calories: int = Field(ge=0)
    protein: str
    carbs: str
    fat: str


class RecipeRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1, max_length=25)
    preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)

    @field_validator("ingredients", "preferences", "allergies")
    @classmethod
    def validate_string_list(cls, values: list[str]) -> list[str]:
        cleaned_values: list[str] = []
        for value in values:
            cleaned = value.strip()
            if not cleaned:
                continue
            if len(cleaned) > 80:
                raise ValueError("Each item must be 80 characters or fewer.")
            cleaned_values.append(cleaned)
        return cleaned_values

    @field_validator("preferences", "allergies")
    @classmethod
    def validate_optional_list_size(cls, values: list[str]) -> list[str]:
        if len(values) > 10:
            raise ValueError("No more than 10 entries are allowed.")
        return values


class RecipeResponse(BaseModel):
    generated_recipe_id: int | None = None
    title: str
    ingredients: list[str]
    preferences: list[str]
    allergies: list[str]
    steps: list[str]
    nutrition_estimate: NutritionEstimate
    image_url: str | None = None
    image_cache_key: str | None = None
    warnings: list[str] = Field(default_factory=list)


class SavedRecipeCreate(BaseModel):
    generated_recipe_id: int


class SavedRecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    ingredients: list[str]
    preferences: list[str]
    allergies: list[str]
    steps: list[str]
    nutrition: NutritionEstimate
    image_url: str | None = None
    image_cache_key: str | None = None
    saved_at: datetime | None = None
    created_at: datetime


class GeneratedRecipeHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fingerprint: str
    title: str
    ingredients: list[str]
    preferences: list[str]
    allergies: list[str]
    steps: list[str]
    nutrition: NutritionEstimate
    warnings: list[str]
    image_url: str | None = None
    image_cache_key: str | None = None
    is_saved: bool
    saved_at: datetime | None = None
    created_at: datetime


class NutritionLabelData(BaseModel):
    product_name: str | None = None
    serving_size: str | None = None
    calories: int | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    sugar_g: float | None = None
    sodium_mg: float | None = None
    fiber_g: float | None = None


class OcrExtractionResponse(BaseModel):
    raw_text: str
    structured_nutrition: NutritionLabelData


class SavedOcrExtractionCreate(BaseModel):
    source_filename: str
    raw_text: str
    structured_nutrition: NutritionLabelData


class SavedOcrExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_filename: str
    raw_text: str
    structured_nutrition: NutritionLabelData
    created_at: datetime
