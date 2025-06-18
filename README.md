# KazRockets Platform MVP Database Specification

## Overview

The KazRockets Platform MVP Database supports a robotics competition platform for managing users, teams, events, submissions, and evaluations. The design focuses on simplicity for rapid deployment while ensuring scalability, auditability, and efficiency. The backend uses FastAPI for RESTful APIs, Redis for caching, and RabbitMQ as a message broker for asynchronous tasks like submission processing and notifications. Soft deletes ensure archival integrity, and the schema is optimized for a distributed environment.

## Objectives

- Enable core competition management: user roles, team formation, event tracking, submissions, and judging.
- Ensure scalability with a distributed backend (FastAPI, Redis, RabbitMQ).
- Minimize complexity for MVP while supporting future enhancements.
- Maintain auditability and role-based access control.

## Database Schema (PostgreSQL)

The schema is simplified to five core tables, reducing redundancy while covering essential functionalities.

### 1. AppUser

Stores participants, organizers, and judges.

- **Fields**:
  - `user_id`: UUID (Primary Key)
  - `email`: String (Unique, Not Null)
  - `password_hash`: String (Not Null)
  - `name`: String (Not Null)
  - `role`: Enum (`PARTICIPANT`, `ORGANIZER`, `JUDGE`) (Not Null)
  - `team_id`: UUID (Foreign Key, Nullable, references `Team`)
  - `created_at`: Timestamp (Not Null)
  - `updated_at`: Timestamp (Not Null)
  - `deleted_at`: Timestamp (Nullable, for soft deletes)
- **Constraints**:
  - Unique email.
  - Role-based permissions enforced in FastAPI.

### 2. Team

Represents teams formed by participants.

- **Fields**:
  - `team_id`: UUID (Primary Key)
  - `name`: String (Not Null)
  - `captain_id`: UUID (Foreign Key, Not Null, references `AppUser`)
  - `created_at`: Timestamp (Not Null)
  - `updated_at`: Timestamp (Not Null)
  - `deleted_at`: Timestamp (Nullable, for soft deletes)
- **Constraints**:
  - `captain_id` must reference a `PARTICIPANT`.

### 3. CompetitiveEvent

Manages competition events.

- **Fields**:
  - `event_id`: UUID (Primary Key)
  - `title`: String (Not Null)
  - `start_date`: Timestamp (Not Null)
  - `end_date`: Timestamp (Not Null)
  - `winner_team_id`: UUID (Foreign Key, Nullable, references `Team`)
  - `created_at`: Timestamp (Not Null)
  - `updated_at`: Timestamp (Not Null)
  - `deleted_at`: Timestamp (Nullable, for soft deletes)
- **Constraints**:
  - `end_date` &gt; `start_date`.

### 4. Submission

Stores team submissions (PDFs) for events.

- **Fields**:
  - `submission_id`: UUID (Primary Key)
  - `team_id`: UUID (Foreign Key, Not Null, references `Team`)
  - `event_id`: UUID (Foreign Key, Not Null, references `CompetitiveEvent`)
  - `file_url`: String (Not Null, URL to cloud-stored PDF)
  - `status`: Enum (`PENDING`, `APPROVED`, `REJECTED`) (Not Null, Default: `PENDING`)
  - `submitted_at`: Timestamp (Not Null)
  - `updated_at`: Timestamp (Not Null)
  - `deleted_at`: Timestamp (Nullable, for soft deletes)

### 5. Evaluation

Captures judge scores and comments.

- **Fields**:
  - `evaluation_id`: UUID (Primary Key)
  - `submission_id`: UUID (Foreign Key, Not Null, references `Submission`)
  - `judge_id`: UUID (Foreign Key, Not Null, references `AppUser`)
  - `score`: Integer (Not Null, Range: 0-100)
  - `comments`: Text (Nullable)
  - `created_at`: Timestamp (Not Null)
  - `updated_at`: Timestamp (Not Null)
  - `deleted_at`: Timestamp (Nullable, for soft deletes)
- **Constraints**:
  - `judge_id` must reference a `JUDGE`.

## Architecture

### Backend: FastAPI

- **Purpose**: RESTful API for CRUD operations on users, teams, events, submissions, and evaluations.
- **Features**:
  - Role-based middleware for access control (e.g., only `JUDGE` can create evaluations).
  - Asynchronous endpoints for high concurrency.
  - Pydantic models for request/response validation.
  - JWT-based authentication for secure user sessions.
- **Example Endpoint**:
  - `POST /submissions`: Uploads PDF, stores URL in cloud (e.g., AWS S3), and enqueues processing via RabbitMQ.

### Caching: Redis

- **Purpose**: Cache frequently accessed data to reduce database load.
- **Use Cases**:
  - Cache event details (e.g., `GET /events/{event_id}`) with TTL of 1 hour.
  - Cache user profiles for quick access during authentication.
  - Store submission status for real-time updates.
- **Configuration**:
  - Redis cluster for scalability.
  - Key format: `kazrockets:{entity}:{id}` (e.g., `kazrockets:event:uuid`).

### Message Broker: RabbitMQ

- **Purpose**: Handle asynchronous tasks to improve performance and reliability.
- **Tasks**:
  - Process uploaded submission files (e.g., validate PDF format).
  - Send notifications (e.g., submission status, deadlines) via email or in-app messages.
  - Queue evaluation assignments to judges.
- **Setup**:
  - Queues: `submission_processing`, `notifications`, `evaluation_assignment`.
  - Workers: FastAPI background tasks consume messages.

### File Storage

- **Provider**: AWS S3 (or equivalent) for storing PDFs and event files.
- **Access**: Signed URLs for secure, time-limited access.
- **Naming**: `submissions/{event_id}/{team_id}/{submission_id}.pdf`.

## Key Functionalities

### 1. Role-Based Access

- `PARTICIPANT`: Join/create teams, submit PDFs.
- `ORGANIZER`: Create events, approve/reject submissions.
- `JUDGE`: Score submissions, add comments.
- FastAPI middleware enforces role permissions.

### 2. Team and Event Management

- Participants form teams with a captain.
- Organizers create events with start/end dates.
- Redis caches event and team data for fast retrieval.

### 3. Submission Workflow

- Teams upload PDFs via FastAPI endpoint.
- RabbitMQ processes uploads asynchronously (e.g., validates file type).
- Status updates (`PENDING`, `APPROVED`, `REJECTED`) stored in database and cached in Redis.

### 4. Judging and Results

- Judges submit scores/comments via FastAPI.
- Evaluations determine winners, stored in `CompetitiveEvent.winner_team_id`.
- Results cached in Redis for quick access.

### 5. Soft Deletes

- `deleted_at` ensures archival integrity across all tables.
- Deleted records excluded from queries but retained for audits.

## Design Considerations

### Scalability

- **Database**: PostgreSQL with UUID primary keys for distributed systems.
- **Indexes**: On `email`, `team_id`, `event_id`, `submission_id` for fast queries.
- **FastAPI**: Asynchronous endpoints handle high traffic.
- **Redis**: Cluster mode supports horizontal scaling.
- **RabbitMQ**: Multiple queues and workers ensure task distribution.

### Error Handling

- FastAPI validates inputs with Pydantic, reducing invalid data.
- RabbitMQ retries failed tasks (e.g., file processing) with exponential backoff.
- Database constraints (e.g., foreign keys, unique emails) prevent inconsistencies.
- Logging: Centralized logging (e.g., ELK stack) for monitoring errors.

### Efficiency

- Redis reduces database queries for read-heavy operations (e.g., event details).
- RabbitMQ offloads time-consuming tasks (e.g., file validation) from FastAPI.
- S3 minimizes local storage overhead.

### Security

- Passwords hashed (bcrypt) in `AppUser`.
- JWT tokens for authentication.
- S3 signed URLs for secure file access.
- Role-based middleware in FastAPI.

## Future Enhancements

- Add phases to events for multi-stage competitions.
- Support multilingual interfaces (e.g., Kazakh, Russian).
- Implement real-time notifications via WebSockets.
- Add analytics dashboard for organizers.

## Sample FastAPI Code

Below is a sample FastAPI endpoint for submission uploads, demonstrating integration with Redis and RabbitMQ.

```python

from fastapi import FastAPI, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from uuid import UUID import aioboto3
from redis.asyncio import Redis
from aio_pika import connect_robust, Message
from sqlalchemy.ext.asyncio import AsyncSession 
from db import get_db
from models import Submission import os

app = FastAPI()

class SubmissionCreate(BaseModel): team_id: UUID event_id: UUID

async def get_redis(): return Redis(host="redis", port=6379)

async def get_rabbit(): return await connect_robust("amqp://guest:guest@rabbitmq/")

@app.post("/submissions") async def create_submission( file: UploadFile, data: SubmissionCreate, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis), rabbit: aio_pika.Connection = Depends(get_rabbit) ): if file.content_type != "application/pdf": raise HTTPException(400, "Only PDF files allowed")


# Upload to S3
session = aioboto3.Session()
async with session.client("s3") as s3:
    file_url = f"submissions/{data.event_id}/{data.team_id}/{file.filename}"
    await s3.upload_fileobj(file.file, "kazrockets-bucket", file_url)

# Save submission to database
submission = Submission(
    team_id=data.team_id,
    event_id=data.event_id,
    file_url=f"s3://kazrockets-bucket/{file_url}",
    status="PENDING"
)
db.add(submission)
await db.commit()

# Cache submission status
await redis.set(f"kazrockets:submission:{submission.submission_id}", "PENDING", ex=3600)

# Enqueue processing
async with rabbit:
    channel = await rabbit.channel()
    await channel.default_exchange.publish(
        Message(f"Process submission {submission.submission_id}".encode()),
        routing_key="submission_processing"
    )

return {"submission_id": submission.submission_id, "status": "PENDING"}
```
