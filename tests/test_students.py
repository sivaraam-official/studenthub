"""
Comprehensive automated tests for StudentHub API.
Uses a separate isolated SQLite database to verify all CRUD operations,
error handling, validations, persistence, and health checks.
"""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app import crud

# In-memory SQLite with StaticPool so all connections share the same memory DB in thread
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh tables for every test and teardown afterwards."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Override get_db dependency with test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==========================================
# TEST CASES
# ==========================================

def test_health_check(client):
    """Test health endpoint returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data


def test_create_student_success(client):
    """Test successful creation of a new student."""
    payload = {
        "name": "Jane Doe",
        "date_of_birth": "2001-04-12",
        "email": "jane.doe@example.com",
        "phone": "+1-555-0199",
        "course": "Computer Science",
        "address": "123 University Ave, Silicon Valley, CA",
        "enrollment_date": "2024-09-01",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane.doe@example.com"
    assert data["course"] == "Computer Science"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_student_duplicate_email(client):
    """Test duplicate email rejection with 409 Conflict."""
    payload = {
        "name": "Alex Mercer",
        "date_of_birth": "2000-01-01",
        "email": "alex.mercer@example.com",
        "course": "Robotics",
    }
    # First creation should succeed
    res1 = client.post("/students", json=payload)
    assert res1.status_code == 201

    # Second creation with identical email should fail with 409
    res2 = client.post("/students", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_create_student_invalid_email(client):
    """Test invalid email format rejection with 422 Unprocessable Entity."""
    payload = {
        "name": "Bad Email Student",
        "date_of_birth": "2002-05-15",
        "email": "not-an-email",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_create_student_future_date_of_birth(client):
    """Test future date of birth is rejected with 422."""
    payload = {
        "name": "Time Traveler",
        "date_of_birth": "2099-01-01",
        "email": "traveler@example.com",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_list_students_and_pagination(client):
    """Test listing students with pagination and totals."""
    # Seed 3 students
    for i in range(1, 4):
        client.post(
            "/students",
            json={
                "name": f"Student {i}",
                "date_of_birth": "2000-01-01",
                "email": f"student{i}@example.com",
                "course": "Mathematics" if i % 2 == 0 else "Physics",
            },
        )

    # Fetch page 1 with limit 2
    response = client.get("/students?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["students"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total_pages"] == 2

    # Fetch page 2
    res_page2 = client.get("/students?page=2&limit=2")
    assert res_page2.status_code == 200
    data2 = res_page2.json()
    assert len(data2["students"]) == 1


def test_search_and_filter_students(client):
    """Test searching students by keyword and filtering by course."""
    client.post(
        "/students",
        json={
            "name": "Devin AI",
            "date_of_birth": "2001-06-15",
            "email": "devin@example.com",
            "course": "Software Engineering",
        },
    )
    client.post(
        "/students",
        json={
            "name": "Sara Connor",
            "date_of_birth": "1999-11-20",
            "email": "sara@example.com",
            "course": "Cybersecurity",
        },
    )

    # Search by name query "Sara"
    search_res = client.get("/students?search=sara")
    assert search_res.status_code == 200
    assert search_res.json()["total"] == 1
    assert search_res.json()["students"][0]["name"] == "Sara Connor"

    # Filter by course "Software Engineering"
    course_res = client.get("/students?course=Software Engineering")
    assert course_res.status_code == 200
    assert course_res.json()["total"] == 1
    assert course_res.json()["students"][0]["name"] == "Devin AI"


def test_get_single_student_success(client):
    """Test retrieving student by ID."""
    create_res = client.post(
        "/students",
        json={
            "name": "John Wick",
            "date_of_birth": "1998-03-25",
            "email": "john.wick@example.com",
            "course": "Tactical Ops",
        },
    )
    student_id = create_res.json()["id"]

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "John Wick"


def test_get_nonexistent_student_returns_404(client):
    """Test requesting a missing student ID returns 404."""
    response = client.get("/students/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_student_details(client):
    """Test updating student information via PUT and PATCH."""
    create_res = client.post(
        "/students",
        json={
            "name": "Alice Smith",
            "date_of_birth": "2002-10-10",
            "email": "alice@example.com",
            "course": "Biology",
        },
    )
    student_id = create_res.json()["id"]

    # Update course and phone
    update_res = client.put(
        f"/students/{student_id}",
        json={"course": "Biotechnology", "phone": "+91-9988776655"},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["course"] == "Biotechnology"
    assert updated["phone"] == "+91-9988776655"
    assert updated["name"] == "Alice Smith"  # Untouched fields remain intact


def test_delete_student(client):
    """Test deleting a student."""
    create_res = client.post(
        "/students",
        json={
            "name": "Temporary Student",
            "date_of_birth": "2000-01-01",
            "email": "temp@example.com",
        },
    )
    student_id = create_res.json()["id"]

    # Delete
    del_res = client.delete(f"/students/{student_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Verify student is now 404
    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 404

    # Deleting again should return 404
    del_again = client.delete(f"/students/{student_id}")
    assert del_again.status_code == 404


def test_stats_endpoint(client):
    """Test dashboard stats endpoint calculation."""
    client.post(
        "/students",
        json={
            "name": "Student A",
            "date_of_birth": "2000-01-01",
            "email": "sta@example.com",
            "course": "AI & ML",
        },
    )
    client.post(
        "/students",
        json={
            "name": "Student B",
            "date_of_birth": "2001-02-02",
            "email": "stb@example.com",
            "course": "AI & ML",
        },
    )
    client.post(
        "/students",
        json={
            "name": "Student C",
            "date_of_birth": "2002-03-03",
            "email": "stc@example.com",
            "course": "Web Dev",
        },
    )

    stats_res = client.get("/stats")
    assert stats_res.status_code == 200
    data = stats_res.json()
    assert data["total_students"] == 3
    assert data["total_courses"] == 2
    assert data["course_counts"]["AI & ML"] == 2
    assert data["course_counts"]["Web Dev"] == 1
    assert len(data["recent_students"]) == 3


def test_database_persistence(db_session):
    """Test direct database persistence using SQLAlchemy CRUD."""
    from app.schemas import StudentCreate

    student_in = StudentCreate(
        name="Persistent Student",
        date_of_birth="2000-05-10",
        email="persist@example.com",
        course="Data Analytics",
    )
    student = crud.create_student(db_session, student_in)
    assert student.id is not None

    # Query afresh from DB
    retrieved = crud.get_student(db_session, student.id)
    assert retrieved is not None
    assert retrieved.name == "Persistent Student"
    assert retrieved.email == "persist@example.com"
