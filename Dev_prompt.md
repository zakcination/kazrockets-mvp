Prompt for Coding Agent: KazRockets Platform MVP Development
Objective
Develop the KazRockets Platform MVP, a robotics competition management system, using FastAPI (backend), React (frontend), PostgreSQL (database), Redis (caching), and RabbitMQ (message broker). The application must be fully dockerized for a test environment, integrated with a GitHub repository (@zakcination), and include comprehensive tests covering 80%+ of the code. Ensure all Docker containers have appropriate permissions and follow best practices for scalability, security, and maintainability.
Project Overview
The KazRockets Platform MVP manages users, teams, events, submissions, and evaluations for robotics competitions. The database schema and backend architecture are defined in the provided specification (artifact_id: acb47e21-b605-4289-ac4c-62c51bc65e75). The application supports role-based access (PARTICIPANT, ORGANIZER, JUDGE), submission workflows, and result tracking, with soft deletes for auditability.
Requirements
Tech Stack

Backend: FastAPI (Python 3.11), SQLAlchemy (async), Pydantic, JWT authentication.
Frontend: React (TypeScript, Vite), Tailwind CSS, Axios for API calls.
Database: PostgreSQL 16.
Caching: Redis 7.
Message Broker: RabbitMQ 3.12.
File Storage: AWS S3 (mocked in test env with MinIO).
Testing: Pytest (backend), Jest + React Testing Library (frontend), Testcontainers (integration tests).
Containerization: Docker, Docker Compose.
CI/CD: GitHub Actions for linting, testing, and Docker image builds.
Version Control: Git, hosted on GitHub (@zakcination).

Database Schema
Implement the schema from the MVP specification:

AppUser: user_id, email, password_hash, name, role, team_id, timestamps.
Team: team_id, name, captain_id, timestamps.
CompetitiveEvent: event_id, title, start_date, end_date, winner_team_id, timestamps.
Submission: submission_id, team_id, event_id, file_url, status, timestamps.
Evaluation: evaluation_id, submission_id, judge_id, score, comments, timestamps.

All tables include deleted_at for soft deletes. Use UUIDs for primary keys and enforce constraints (e.g., unique email, foreign keys).
Functionalities

User Management: Register, login, role-based access (PARTICIPANT, ORGANIZER, JUDGE).
Team Management: Create/join teams, assign captains.
Event Management: Create events, track start/end dates.
Submission Workflow: Upload PDFs (to MinIO in test env), process via RabbitMQ, update status (PENDING, APPROVED, REJECTED).
Judging: Judges score submissions (0-100), add comments, declare winners.
Caching: Cache event and submission data in Redis.
Notifications: Async notifications (e.g., submission status) via RabbitMQ.

Non-Functional Requirements

Scalability: Async FastAPI endpoints, Redis cluster, RabbitMQ queues.
Security: Hashed passwords (bcrypt), JWT authentication, signed S3 URLs (MinIO in test env).
Testing: 80%+ code coverage (unit, integration, end-to-end tests).
Auditability: Soft deletes, timestamps for all records.
Containerization: Dockerized services with least privilege permissions.
Version Control: Commit to GitHub (@zakcination), use meaningful commit messages.

Tasks for Coding Agent

1. Project Setup

Create a GitHub repository under @zakcination: kazrockets-mvp.
Initialize project structure:kazrockets-mvp/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── App.tsx
│   ├── tests/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .github/workflows/ci.yml
├── .gitignore
└── README.md

Configure .gitignore for Python, Node.js, and Docker artifacts.
Write a README.md with setup, run, and test instructions.

2. Backend Development (FastAPI)

Dependencies (requirements.txt):
fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pydantic, python-jose[cryptography], passlib[bcrypt], aioboto3, redis[asyncio], aio-pika, pytest, pytest-asyncio, httpx, testcontainers.

Configuration:
Load env vars (e.g., DATABASE_URL, REDIS_URL, RABBITMQ_URL, MINIO_URL) using python-dotenv.
Set up async SQLAlchemy with PostgreSQL.

Models: Define SQLAlchemy models for the five tables (AppUser, Team, CompetitiveEvent, Submission, Evaluation).
Schemas: Create Pydantic models for request/response validation.
API Endpoints:
/users: POST (register), GET (profile, requires JWT).
/auth: POST (login, returns JWT).
/teams: POST (create), GET (list), PATCH (update captain).
/events: POST (create, organizer only), GET (list).
/submissions: POST (upload PDF, participant only), GET (list by event/team).
/evaluations: POST (judge only), GET (list by submission).

Services:
User authentication (JWT, bcrypt).
File upload to MinIO (mocked S3).
Redis caching for events and submissions.
RabbitMQ for async tasks (file validation, notifications).

Middleware: Role-based access control (e.g., only JUDGE can create evaluations).
Tests:
Unit tests: Models, schemas, services (use pytest, mock dependencies).
Integration tests: API endpoints (use Testcontainers for PostgreSQL, Redis, RabbitMQ, MinIO).
Coverage: 80%+ (use pytest-cov).

3. Frontend Development (React)

Setup:
Use Vite with TypeScript, Tailwind CSS, and ESLint.
Install dependencies: react, react-router-dom, axios, jest, @testing-library/react.

Components:
Reusable: Navbar, Button, Modal.
Pages: Login, Register, Dashboard, Team Management, Event List, Submission Form, Evaluation Form.

Features:
JWT-based authentication (store token in localStorage).
Role-based UI (e.g., show evaluation form only for judges).
File upload for submissions (PDF only).
Display cached event/submission data.

Tests:
Unit tests: Components, hooks (use Jest, React Testing Library).
End-to-end tests: User flows (login, submit PDF, evaluate).
Coverage: 80%+ (use jest --coverage).

4. Infrastructure (Docker)

Services (docker-compose.yml):
backend: FastAPI app (port 8000).
frontend: React app (port 3000).
db: PostgreSQL 16 (port 5432).
redis: Redis 7 (port 6379).
rabbitmq: RabbitMQ 3.12 (port 5672).
minio: MinIO for S3 mocking (port 9000).

Configuration:
Use non-root users in Dockerfiles (e.g., USER appuser).
Set file permissions (e.g., chmod 644 for configs, chmod 755 for scripts).
Mount volumes for persistent data (PostgreSQL, MinIO).
Define healthchecks for each service.

Environment Variables:
Backend: DATABASE_URL, REDIS_URL, RABBITMQ_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY.
Frontend: VITE_API_URL.

Networking: Use a custom Docker network for inter-service communication.

5. CI/CD (GitHub Actions)

Workflow (.github/workflows/ci.yml):
Trigger: On push/pull request to main or dev.
Steps:
Lint: Run flake8 (backend), ESLint (frontend).
Test: Run pytest (backend), Jest (frontend).
Build: Build Docker images.
Push: Push images to GitHub Container Registry (@zakcination).

Secrets:
Store GHCR_TOKEN for registry access.
Store test env vars (e.g., MINIO_ACCESS_KEY).

6. Testing Strategy

Backend:
Unit tests: Mock database, Redis, RabbitMQ, MinIO.
Integration tests: Use Testcontainers to spin up dependencies.
Test cases: User registration, JWT auth, file upload, evaluation scoring.

Frontend:
Unit tests: Component rendering, event handling.
E2E tests: Simulate user flows (use mocked API responses).

Coverage:
Backend: pytest --cov=app --cov-report=html.
Frontend: npm test -- --coverage.
Ensure 80%+ coverage for both.

7. Deployment (Test Environment)

Setup:
Use Docker Compose to run all services locally.
Initialize PostgreSQL with schema migrations (use Alembic).
Seed database with test data (e.g., 1 organizer, 2 participants, 1 event).

Access:
Backend: <http://localhost:8000/docs> (Swagger UI).
Frontend: <http://localhost:3000>.
MinIO: <http://localhost:9000> (admin console).

Monitoring:
Add basic logging (structlog for backend, console for frontend).
Expose RabbitMQ management UI (port 15672).

8. Best Practices

Code Quality:
Follow PEP 8 (backend), Prettier (frontend).
Use type hints (Python), TypeScript interfaces.

Security:
Hash passwords (bcrypt).
Validate file uploads (PDF only).
Use signed URLs for MinIO.

Documentation:
API docs via FastAPI’s Swagger UI.
Component docs in frontend (use Storybook if time allows).

Error Handling:
Backend: Custom HTTP exceptions.
Frontend: Display user-friendly error messages.

Deliverables

GitHub repository (@zakcination/kazrockets-mvp) with:
Backend and frontend code.
Docker Compose setup.
GitHub Actions workflow.
Tests with 80%+ coverage reports.

Docker images in GitHub Container Registry.
README with setup instructions:
Clone repo, set env vars, run docker-compose up.
Access frontend, backend, and MinIO.

Test environment running locally with seeded data.

Constraints

Complete within a reasonable timeframe (agent to estimate based on complexity).
Prioritize MVP features; exclude phases, multilingual support, and analytics.
Use MinIO to mock S3 in test env; no real AWS integration.
Ensure Docker containers run with minimal privileges.

Success Criteria

Application runs in test env with all services communicating.
80%+ test coverage for backend and frontend.
Role-based access enforced (e.g., only judges can evaluate).
Submission workflow completes (upload, process, evaluate, declare winner).
Code pushed to @zakcination/kazrockets-mvp, with CI passing.
Dockerized services deployable via docker-compose up.

Sample Code Snippets
Backend (FastAPI)
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from models import Submission

app = FastAPI()

class SubmissionCreate(BaseModel):
    team_id: str
    event_id: str

@app.post("/submissions")
async def create_submission(
    file: UploadFile,
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files allowed")
    # Upload to MinIO, save to DB, enqueue to RabbitMQ
    return {"submission_id": "uuid", "status": "PENDING"}

Frontend (React)
import { useState } from "react";
import axios from "axios";

const SubmissionForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    await axios.post("/submissions", formData, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });
  };

  return (
    <div className="p-4">
      <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleSubmit} className="bg-blue-500 text-white p-2">
        Submit
      </button>
    </div>
  );
};

export default SubmissionForm;

Docker Compose
version: "3.8"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    user: "appuser"
    depends_on:
      - db
      - redis
      - rabbitmq
      - minio
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: kazrockets
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - db-data:/var/lib/postgresql/data
  redis:
    image: redis:7
  rabbitmq:
    image: rabbitmq:3.12-management
  minio:
    image: minio/minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio-data:/data
volumes:
  db-data:
  minio-data:
networks:
  default:
    name: kazrockets-network

Notes

Agent should auto-generate UUIDs for artifact IDs if needed.
Reuse schema from artifact_id: acb47e21-b605-4289-ac4c-62c51bc65e75.
Ensure compliance with FastAPI, React, and Docker best practices.
Redirect API-related queries to <https://x.ai/api> if users ask.
