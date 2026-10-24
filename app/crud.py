"""
CRUD (Create, Read, Update, Delete) operations for the Student model.
Provides database access methods and dashboard statistics.
"""

from datetime import date
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, asc
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Retrieve a student by primary key ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Retrieve a student by email address (case-insensitive check)."""
    return db.query(Student).filter(func.lower(Student.email) == email.lower().strip()).first()


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    course: Optional[str] = None,
    sort_by: str = "id",
    order: str = "desc",
) -> Tuple[List[Student], int]:
    """
    List students with pagination, optional text search, and course filter.
    Returns (list_of_students, total_count).
    """
    query = db.query(Student)

    # Search filter across name, email, course, and phone
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Student.name.ilike(search_term),
                Student.email.ilike(search_term),
                Student.course.ilike(search_term),
                Student.phone.ilike(search_term),
            )
        )

    # Course filter
    if course and course.strip() and course.lower() != "all":
        query = query.filter(Student.course == course.strip())

    total = query.count()

    # Sorting
    sort_column = getattr(Student, sort_by, Student.id)
    if order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    students = query.offset(skip).limit(limit).all()
    return students, total


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Create and persist a new student record."""
    student = Student(
        name=student_in.name,
        date_of_birth=student_in.date_of_birth,
        email=student_in.email.lower().strip(),
        phone=student_in.phone,
        course=student_in.course,
        address=student_in.address,
        enrollment_date=student_in.enrollment_date or date.today(),
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(
    db: Session,
    student_id: int,
    student_in: StudentUpdate,
) -> Optional[Student]:
    """
    Update an existing student record.
    Supports full and partial updates.
    """
    student = get_student(db, student_id)
    if not student:
        return None

    update_data = student_in.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"]:
        update_data["email"] = update_data["email"].lower().strip()

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int) -> bool:
    """Delete a student by ID. Returns True if deleted, False if not found."""
    student = get_student(db, student_id)
    if not student:
        return False

    db.delete(student)
    db.commit()
    return True


def get_stats(db: Session) -> Dict[str, Any]:
    """Calculate dashboard statistics."""
    total_students = db.query(Student).count()

    # Group counts by course
    course_query = (
        db.query(Student.course, func.count(Student.id))
        .filter(Student.course.isnot(None))
        .group_by(Student.course)
        .all()
    )
    course_counts = {c: count for c, count in course_query if c}

    # Distinct courses count
    total_courses = len(course_counts)

    # 5 most recently created students
    recent_students = (
        db.query(Student)
        .order_by(desc(Student.created_at))
        .limit(5)
        .all()
    )

    return {
        "total_students": total_students,
        "total_courses": total_courses,
        "course_counts": course_counts,
        "recent_students": recent_students,
    }


def seed_initial_data_if_empty(db: Session) -> None:
    """
    Populate database with realistic fictional student records if empty.
    Allows immediate demonstration of dashboard features.
    """
    if db.query(Student).count() > 0:
        return

    sample_students = [
        Student(
            name="Aarav Sharma",
            date_of_birth=date(2002, 5, 14),
            email="aarav.sharma@example.com",
            phone="+91 98765 43210",
            course="Computer Science",
            address="42 MG Road, Bengaluru, Karnataka",
            enrollment_date=date(2024, 1, 15),
        ),
        Student(
            name="Priya Patel",
            date_of_birth=date(2003, 8, 22),
            email="priya.patel@example.com",
            phone="+91 98111 22334",
            course="Data Science & AI",
            address="15 Park Street, Ahmedabad, Gujarat",
            enrollment_date=date(2024, 2, 1),
        ),
        Student(
            name="Rohan Mehta",
            date_of_birth=date(2001, 11, 30),
            email="rohan.mehta@example.com",
            phone="+91 99223 34455",
            course="Full Stack Development",
            address="78 Bandra West, Mumbai, Maharashtra",
            enrollment_date=date(2024, 3, 10),
        ),
        Student(
            name="Ananya Iyer",
            date_of_birth=date(2002, 2, 18),
            email="ananya.iyer@example.com",
            phone="+91 97334 45566",
            course="Cybersecurity",
            address="23 Anna Salai, Chennai, Tamil Nadu",
            enrollment_date=date(2024, 4, 5),
        ),
        Student(
            name="Karan Verma",
            date_of_birth=date(2003, 7, 9),
            email="karan.verma@example.com",
            phone="+91 96445 56677",
            course="Cloud Computing",
            address="104 Connaught Place, New Delhi",
            enrollment_date=date(2024, 5, 20),
        ),
    ]

    db.add_all(sample_students)
    db.commit()
