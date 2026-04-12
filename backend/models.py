from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
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

    generated_recipes = relationship(
        "GeneratedRecipe",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    ocr_extractions = relationship(
        "OcrExtraction",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class GeneratedRecipe(Base):
    __tablename__ = "generated_recipes"

    id = Column(Integer, primary_key=True, index=True)
    fingerprint = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    ingredients = Column(Text, nullable=False)
    preferences = Column(Text, nullable=False, default="[]")
    allergies = Column(Text, nullable=False, default="[]")
    steps = Column(Text, nullable=False)
    nutrition = Column(Text, nullable=False)
    warnings = Column(Text, nullable=False, default="[]")
    image_url = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    image_cache_key = Column(String, nullable=True, index=True)
    image_prompt = Column(Text, nullable=True)
    is_saved = Column(Boolean, nullable=False, default=False, server_default="false")
    saved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="generated_recipes")


class OcrExtraction(Base):
    __tablename__ = "ocr_extractions"

    id = Column(Integer, primary_key=True, index=True)
    source_filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    structured_nutrition = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="ocr_extractions")