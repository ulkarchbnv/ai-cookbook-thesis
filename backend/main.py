from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import os

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

@app.get("/")
def read_root():
    return{"message": "AI Cookbook backend is running",
           "openai_key_loaded": OPENAI_API_KEY is not None}

def generate_text_recipe(request: RecipeRequest):
    prompt = f""" Create one simple recipe using these ingredients I have:
    {", ".join(request.ingredients)}. 
    Dietary preferences: {", ".join(request.preferences) if request.preferences else "none"}.
    Allergies to be careful!: {", ".join(request.allergies) if request.allergies else "none"}.
    Return:
    1. A recipe title
    2. A short ingredient list
    3. 3 short cooking instructions
    4. A rough nutrition estimate
    """
    response = client.responses.create(
        model = "gpt-4.1-mini",
        input = prompt
    )
    return response.output_text



@app.post("/generate-recipe")
def generate_recipe(request: RecipeRequest):
    ingredients = request.ingredients
    preferences = request.preferences
    allergies = request.allergies
    print("Request received:", request)
    ai_text = generate_text_recipe(request)
    print("LLM response: ", ai_text)
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