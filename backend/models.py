from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    preferences = Column(Text, nullable=False, default="[]")
    allergies = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recipes = relationship("Recipe", back_populates="owner", cascade="all, delete-orphan")
    ocr_extractions = relationship(
        "OcrExtraction",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    ingredients = Column(Text, nullable=False)
    preferences = Column(Text, nullable=False, default="[]")
    allergies = Column(Text, nullable=False, default="[]")
    steps = Column(Text, nullable=False)
    nutrition = Column(Text, nullable=False)
    image_cache_key = Column(String, nullable=True, index=True)
    image_path = Column(String, nullable=True)
    image_prompt = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="recipes")


class OcrExtraction(Base):
    __tablename__ = "ocr_extractions"

    id = Column(Integer, primary_key=True, index=True)
    source_filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    structured_nutrition = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="ocr_extractions")
