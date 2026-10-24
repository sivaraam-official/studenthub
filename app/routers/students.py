"""
Student CRUD API Endpoints.
Provides endpoints for creating, reading, updating, and deleting student records.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Register a new student with required personal details. Validates email format and ensures uniqueness.",
)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
):
    # Check for duplicate email
    existing = crud.get_student_by_email(db, student_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A student with email '{student_in.email}' already exists.",
        )

    student = crud.create_student(db, student_in)
    return student


@router.get(
    "",
    response_model=StudentListResponse,
    summary="List students with pagination & search",
    description="Retrieve a paginated list of students. Supports optional text search across name, email, course, and phone, plus course-specific filtering.",
)
def list_students(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name, email, phone, or course"),
    course: Optional[str] = Query(None, description="Filter by course name"),
    sort_by: str = Query("id", pattern="^(id|name|email|course|enrollment_date|created_at)$", description="Field to sort by"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    students, total = crud.get_students(
        db,
        skip=skip,
        limit=limit,
        search=search,
        course=course,
        sort_by=sort_by,
        order=order,
    )
    total_pages = math.ceil(total / limit) if total > 0 else 1

    return StudentListResponse(
        students=students,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student by ID",
    description="Fetch complete details of a specific student by primary key.",
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update an existing student (Full update)",
    description="Update all or selected fields of an existing student. Verifies email uniqueness if modified.",
)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
):
    existing = crud.get_student(db, student_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )

    # Check email conflict if email is being changed
    if student_in.email and student_in.email.lower().strip() != existing.email.lower():
        email_taken = crud.get_student_by_email(db, student_in.email)
        if email_taken:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{student_in.email}' is already in use by another student.",
            )

    updated = crud.update_student(db, student_id, student_in)
    return updated


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Partially update a student",
    description="Partially update one or more fields of an existing student.",
)
def patch_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
):
    return update_student(student_id=student_id, student_in=student_in, db=db)


@router.delete(
    "/{student_id}",
    summary="Delete a student",
    description="Permanently delete a student record by ID.",
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    return {
        "success": True,
        "message": f"Student with ID {student_id} has been successfully deleted.",
        "deleted_id": student_id,
    }
