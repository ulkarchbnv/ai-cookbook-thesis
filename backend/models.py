from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, index = True, nullable = False)
    password = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import relationship

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    ingredients = Column(Text, nullable=False)
    steps = Column(Text, nullable=False)
    nutrition = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")