"""
Pydantic schemas for request validation and response serialization.
Strict validation for emails, dates, and string constraints.
"""

from datetime import date, datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class StudentBase(BaseModel):
    """Base fields shared across student schemas."""
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the student")
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    email: EmailStr = Field(..., description="Valid and unique email address")
    phone: Optional[str] = Field(None, max_length=30, description="Contact phone number")
    course: Optional[str] = Field(None, max_length=100, description="Enrolled course name")
    address: Optional[str] = Field(None, max_length=500, description="Residential address")
    enrollment_date: Optional[date] = Field(None, description="Date of course enrollment (YYYY-MM-DD)")

    @field_validator("name", mode="before")
    @classmethod
    def strip_and_validate_name(cls, v: str) -> str:
        if isinstance(v, str):
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Student name cannot be empty or only whitespace")
            return cleaned
        return v

    @field_validator("phone", "course", "address", mode="before")
    @classmethod
    def strip_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            cleaned = v.strip()
            return cleaned if cleaned else None
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class StudentCreate(StudentBase):
    """Schema for creating a new student record."""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating an existing student (PUT / PATCH)."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    enrollment_date: Optional[date] = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_and_validate_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Student name cannot be blank")
            return cleaned
        return v

    @field_validator("phone", "course", "address", mode="before")
    @classmethod
    def strip_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            cleaned = v.strip()
            return cleaned if cleaned else None
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class StudentResponse(StudentBase):
    """Schema for returning a student record with system attributes."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    """Paginated list of students."""
    students: List[StudentResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class StatsResponse(BaseModel):
    """Dashboard statistics summary."""
    total_students: int
    total_courses: int
    course_counts: Dict[str, int]
    recent_students: List[StudentResponse]


class HealthResponse(BaseModel):
    """Health check status response."""
    status: str
    database: str
    version: str
    timestamp: datetime
