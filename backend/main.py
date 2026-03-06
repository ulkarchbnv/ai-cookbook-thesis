from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
class RecipeRequest(BaseModel):
    ingredients: List[str]
    preferences: List[str] = []
    allergies: List[str] = []

@app.get("/")
def read_root():
    return{"message": "AI Cookbook backend is running"}

@app.post("/generate-recipe")
def generate_recipe(request: RecipeRequest):
    ingredients = request.ingredients
    preferences = request.preferences
    allergies = request.allergies
    print("Request received:", request)
    return {
        "title": f"Recipe with {', '.join(request.ingredients)}",
        "ingredients": request.ingredients,
        "preferences": request.preferences,
        "allergies": request.allergies,
        "steps": [
            "Step 1: Prepare ingredients",
            "Step 2: Cook all of them",
            "Step 3: Serve the meal"
        ],
        "nutrition_estimate": {
            "calories": 500,
            "protein": "20g",
            "carbs": "50g",
            "fat": "15g"
        }
    }