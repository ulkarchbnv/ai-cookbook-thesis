from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from database import engine 
from models import Base

Base.metadata.create_all(bind = engine)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key= OPENAI_API_KEY)

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

class NutritionEstimate(BaseModel):
    calories: int
    protein: str
    carbs: str
    fat: str

class RecipeResponse(BaseModel):
    title: str
    ingredients: List[str]
    preferences: List[str]
    allergies: List[str]
    steps: List[str]
    nutrition_estimate: NutritionEstimate

@app.get("/")
def read_root():
    return{"message": "AI Cookbook backend is running",
           "openai_key_loaded": OPENAI_API_KEY is not None}

def generate_structured_recipe(request: RecipeRequest):
    prompt = f"""
    Create one recipe using these ingredients: {", ".join(request.ingredients)}.
    Dietary preferences: {", ".join(request.preferences) if request.preferences else "none"}.
    Allergies to avoid: {", ".join(request.allergies) if request.allergies else "none"}.

    Return ONLY valid JSON in this exact structure:
    {{
      "title": "string",
      "ingredients": ["string", "string"],
      "preferences": ["string"],
      "allergies": ["string"],
      "steps": ["string", "string", "string"],
      "nutrition_estimate": {{
        "calories": 0,
        "protein": "string",
        "carbs": "string",
        "fat": "string"
      }}
    }}

    Rules:
    - Return only JSON
    - No markdown
    - No explanation text
    - Respect dietary preferences and allergies
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    recipe_text = response.output_text
    print("LLM structured response:", recipe_text)

    return json.loads(recipe_text)



@app.post("/generate-recipe", response_model = RecipeResponse)
def generate_recipe(request: RecipeRequest):
    ingredients = request.ingredients
    preferences = request.preferences
    allergies = request.allergies
    print("Request received:", request)
    recipe_data = generate_structured_recipe(request)
    return recipe_data
    