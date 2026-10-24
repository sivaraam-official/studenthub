"""
SQLAlchemy ORM models for StudentHub.
Defines the Student database schema with constraints and timestamps.
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, func
from app.database import Base


class Student(Base):
    """
    Student model representing a student record in the database.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True)
    course = Column(String(100), nullable=True, index=True)
    address = Column(Text, nullable=True)
    enrollment_date = Column(Date, nullable=True, default=date.today)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.name}', email='{self.email}', course='{self.course}')>"
