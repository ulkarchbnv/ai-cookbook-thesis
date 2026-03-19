import ast
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User
from backend.schemas import TokenResponse, UserCreate, UserLogin, UserProfileUpdate, UserResponse
from backend.security import create_access_token, hash_password, verify_password


router = APIRouter()


def _load_list(raw_value: str) -> list[str]:
    if not raw_value:
        return []

    try:
        value = json.loads(raw_value)
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        try:
            value = ast.literal_eval(raw_value)
            return value if isinstance(value, list) else []
        except (ValueError, SyntaxError):
            return []


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        preferences=_load_list(user.preferences),
        allergies=_load_list(user.allergies),
        created_at=user.created_at,
    )


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        preferences="[]",
        allergies="[]",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return _user_to_response(new_user)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user or not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": existing_user.email})
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    existing_user = db.query(User).filter(User.email == form_data.username).first()
    if not existing_user or not verify_password(form_data.password, existing_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": existing_user.email})
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    return _user_to_response(current_user)


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    profile: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    current_user.preferences = json.dumps(profile.preferences)
    current_user.allergies = json.dumps(profile.allergies)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return _user_to_response(current_user)
