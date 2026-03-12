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
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserResponse
from security import hash_password
from models import User
from security import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

Base.metadata.create_all(bind = engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

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

@app.post("/signup", response_model = UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code = 400, detail = "Email already registered")
    new_user = User(
        email = user.email,
        password = hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": existing_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credentials_exception

    return user
    
@app.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/token", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == form_data.username).first()

    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(form_data.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": existing_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }