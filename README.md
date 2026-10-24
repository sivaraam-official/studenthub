# StudentHub — Student Database Management System

> **EWB Edu Tech Pvt. Ltd. — Python Backend Development Internship Project Assignment**

StudentHub is a production-ready, full-stack Student Records Management System designed to handle academic registration, student directories, search, pagination, and real-time dashboard analytics. Built with a high-performance **FastAPI** backend, **SQLAlchemy ORM**, persistent **SQLite** database, and a clean, responsive **HTML5/CSS3/JavaScript** dashboard served directly under a unified single-host architecture.

---

## 📌 Project Overview

- **Application Name**: StudentHub
- **Developer Role**: Full-Stack Python Backend Development Intern
- **Organization**: EWB Edu Tech Pvt. Ltd.
- **Project Directory**: `D:\mine\students-crud-app`
- **Frontend Architecture**: Responsive Single-Page Application (HTML5, Vanilla JS, CSS3)
- **Backend Architecture**: RESTful API with FastAPI and Uvicorn
- **Database Engine**: SQLite 3 with SQLAlchemy ORM (persistent disk storage)
- **API Documentation**: Interactive OpenAPI / Swagger UI at `/docs` and ReDoc at `/redoc`

---

## ✨ Key Features

### 1. Complete RESTful CRUD Operations
- **Create**: Add new students with full field validation (Name, DOB, unique Email, Phone, Course, Address, Enrollment Date).
- **Read / List**: Paginated student table with dynamic search (name, email, course, phone) and course-based filtering.
- **Read / Detail**: Modal profile card displaying complete student records, timestamps, and status badges.
- **Update**: Full (`PUT`) and partial (`PATCH`) student information updates with conflict detection.
- **Delete**: Permanent deletion with a safety confirmation modal.

### 2. Frontend User Interface & Experience
- **Sidebar & Dashboard Overview**: Live counters for total students, active courses, and system status.
- **Search & Filtering**: Real-time debounced search bar and dynamic course filter dropdown.
- **Interactive Modals**: Add Student, Edit Student, View Profile, and Delete Confirmation.
- **Double-Submission Protection**: Buttons display animated spinners and disable during active API requests.
- **Toast Notifications**: Feedback messages (success, warning, error) with auto-dismissal.
- **Mobile Responsive**: Adapts to desktop, tablet, and mobile screens with a collapsible sidebar drawer.

### 3. Data Integrity & Validation
- Pydantic v2 schemas validating format, length, email uniqueness, and future date rejections.
- Case-insensitive email uniqueness checks preventing duplicate records.
- Standard HTTP status codes (`200 OK`, `201 Created`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Content`, `500 Internal Error`).
- Automatic table generation and fictional seed data on initial startup for instant demonstration.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (0.110+) | High-performance asynchronous Python API |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) (0.28+) | Production-grade ASGI server |
| **ORM & Database** | [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 + SQLite 3 | Relational database modeling and persistence |
| **Validation** | [Pydantic](https://docs.pydantic.dev/) v2 + Email-Validator | Strict data schema parsing and error handling |
| **Frontend UI** | HTML5, CSS3 (Modern Flex/Grid), Vanilla JavaScript | Responsive user interface without external framework bloat |
| **Testing** | [Pytest](https://docs.pytest.org/) 8.0 + FastAPI TestClient | Automated unit and integration test suite |
| **Config / Environment**| [Python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable management (`.env`) |

---

## 📁 Project Structure

```
students-crud-app/
├── app/
│   ├── __init__.py          # Package initializer with version
│   ├── main.py              # FastAPI app, CORS, routes, static mount & lifespan
│   ├── database.py          # SQLAlchemy engine, session maker & get_db dependency
│   ├── models.py            # Student ORM model definition
│   ├── schemas.py           # Pydantic validation and serialization schemas
│   ├── crud.py              # Database query functions, filters & data seeder
│   └── routers/
│       ├── __init__.py      # Routers package
│       ├── students.py      # /students CRUD endpoints
│       └── stats.py         # /stats and /health monitoring endpoints
├── frontend/
│   ├── index.html           # Dashboard UI with modals and responsive layout
│   ├── css/
│   │   └── style.css        # Custom responsive styling and theme variables
│   └── js/
│       ├── config.js        # Centralized frontend API configuration
│       ├── api.js           # Fetch API client handling backend requests
│       └── app.js           # State management, DOM events, and modal controllers
├── tests/
│   ├── __init__.py          # Test suite package
│   └── test_students.py     # 13 automated pytest test cases with isolated DB
├── .env.example             # Template for configuration environment variables
├── .env                     # Local environment settings (git-ignored)
├── .gitignore               # Ignored files (venv, DB, pycache, secrets)
├── Procfile                 # Production process command for Render/Heroku
├── render.yaml              # Render Blueprints Infrastructure-as-Code specification
├── requirements.txt         # Pinned production Python dependencies
├── students.db              # Persistent SQLite database file
└── README.md                # Comprehensive documentation and deployment guide
```

---

## 🚀 Getting Started (Local Setup)

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your machine.
- Git installed.

### 2. Navigate to Project Directory
```powershell
cd D:\mine\students-crud-app
```

### 3. Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on Windows (Command Prompt)
.\venv\Scripts\activate.bat

# Activate on macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Setup Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(The default settings point to `sqlite:///./students.db` on port `8000`)*

### 6. Run the Application
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
- **Frontend Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Running Automated Tests

A dedicated test suite is included in `tests/test_students.py`. Tests use an isolated in-memory SQLite database, guaranteeing that test runs never alter your local development or production database.

Run the test suite:
```powershell
pytest -v
```

### Test Coverage Highlights:
1. `test_health_check`: Verifies the `/health` endpoint status and database connectivity.
2. `test_create_student_success`: Validates record creation and status code `201 Created`.
3. `test_create_student_duplicate_email`: Confirms duplicate emails return `409 Conflict`.
4. `test_create_student_invalid_email`: Verifies malformed emails are rejected with `422`.
5. `test_create_student_future_date_of_birth`: Validates future birth dates are rejected.
6. `test_list_students_and_pagination`: Tests pagination calculations, limits, and pages.
7. `test_search_and_filter_students`: Tests text search queries and course filters.
8. `test_get_single_student_success`: Tests retrieval of a specific student ID.
9. `test_get_nonexistent_student_returns_404`: Validates nonexistent IDs return `404 Not Found`.
10. `test_update_student_details`: Validates `PUT` updates and preservation of unmodified fields.
11. `test_delete_student`: Verifies removal and subsequent 404 responses.
12. `test_stats_endpoint`: Confirms dashboard metrics and course distributions.
13. `test_database_persistence`: Tests direct SQLAlchemy persistence and query retrieval.

---

## 📡 REST API Reference

| Method | Endpoint | Description | Request Body | Status Code |
|---|---|---|---|---|
| `GET` | `/health` | Server & DB health check | None | `200 OK` |
| `GET` | `/stats` | Dashboard statistics & counts | None | `200 OK` |
| `GET` | `/students` | List students (paginated & filtered) | Query params: `page`, `limit`, `search`, `course`, `sort_by`, `order` | `200 OK` |
| `POST` | `/students` | Create a new student | JSON (`name`, `date_of_birth`, `email`, optional: `phone`, `course`, `address`, `enrollment_date`) | `201 Created` / `409 Conflict` / `422` |
| `GET` | `/students/{id}` | Retrieve single student by ID | None | `200 OK` / `404 Not Found` |
| `PUT` | `/students/{id}` | Full update of student details | JSON (`StudentUpdate` schema) | `200 OK` / `404 Not Found` / `409 Conflict` |
| `PATCH` | `/students/{id}` | Partial update of student details | JSON (`StudentUpdate` schema) | `200 OK` / `404 Not Found` |
| `DELETE` | `/students/{id}` | Permanently delete student record | None | `200 OK` / `404 Not Found` |

---

## 💻 Example API Calls

### 1. Create a Student (cURL)
```bash
curl -X POST "http://127.0.0.1:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Arjun Patel",
    "date_of_birth": "2002-06-18",
    "email": "arjun.patel@example.com",
    "phone": "+91 98765 12345",
    "course": "Full Stack Development",
    "address": "Ahmedabad, Gujarat",
    "enrollment_date": "2024-04-01"
  }'
```

### 2. Search Students with Filter
```bash
curl -X GET "http://127.0.0.1:8000/students?search=Patel&course=Full%20Stack%20Development&page=1&limit=10"
```

### 3. Update Student Information
```bash
curl -X PUT "http://127.0.0.1:8000/students/1" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+91 99999 00000",
    "course": "Data Science & AI"
  }'
```

### 4. Delete Student
```bash
curl -X DELETE "http://127.0.0.1:8000/students/1"
```

---

## 🌐 Public Live Deployment Guide (Render)

The application is structured to serve both the backend API and frontend UI from a single unified service. This makes hosting simple and eliminates CORS issues.

### Deploying to Render.com (Recommended Free Tier)

1. **Push your code to GitHub**:
   ```bash
   cd D:\mine\students-crud-app
   git init
   git add .
   git commit -m "Initial commit: StudentHub CRUD application"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Create Web Service on Render**:
   - Go to [https://render.com](https://render.com) and log in.
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository.
   - Configure the service settings:
     - **Name**: `studenthub-crud-app`
     - **Runtime**: `Python 3`
     - **Region**: Closest to you (e.g., Singapore or Frankfurt)
     - **Branch**: `main`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Instance Type**: `Free`

3. **Configure Environment Variables in Render**:
   - In the Render dashboard, navigate to **Environment**:
     - `PYTHON_VERSION`: `3.12.10`
     - `ALLOWED_ORIGINS`: `*`
     - `DATABASE_URL`: `sqlite:///./students.db`

4. **Persistent Disk (Optional for Free Tier)**:
   - On the Free tier, Render runs on an ephemeral disk (database resets when inactive).
   - For permanent persistence across server sleep cycles, attach a Render Disk at `/var/data` and set `DATABASE_URL=sqlite:////var/data/students.db`, or use a hosted PostgreSQL database (by changing `DATABASE_URL` to the Postgres connection string; SQLAlchemy supports both without code changes).

5. **Access Your Live Application**:
   - Once deployed, your web app will be live at: `https://studenthub-crud-app.onrender.com`
   - Interactive API docs will be at: `https://studenthub-crud-app.onrender.com/docs`

---

## 📋 Submission Checklist

- [x] Complete REST API endpoints implemented with FastAPI
- [x] SQLite database with SQLAlchemy ORM and automatic startup migrations
- [x] Pydantic schemas with email format and date validations
- [x] Connected responsive frontend (HTML5/CSS3/Vanilla JS)
- [x] Centralized frontend API configuration (`frontend/js/config.js`)
- [x] Live search, course filtering, and pagination
- [x] Add, edit, view profile, and delete modals
- [x] Automated test suite passing with 100% success rate (13/13 tests)
- [x] Production configurations (`requirements.txt`, `Procfile`, `render.yaml`)
- [x] `.gitignore` and `.env.example` properly configured
- [x] Git repository initialized and prepared for remote push

---

## 📄 License & Credits

Developed by Intern for **EWB Edu Tech Pvt. Ltd.** Python Backend Development Internship Assignment.
All rights reserved © 2026.
