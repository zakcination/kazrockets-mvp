# KazRockets MVP - Quick Launch Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker and Docker Compose installed
- Git installed
- Ports 3000, 8000, 5432, 6379, 5672, 9000, 9001, 15672 available

### 1. Clone and Setup
```bash
git clone https://github.com/zakcination/kazrockets-mvp.git
cd kazrockets-mvp
cp .env.example .env
```

### 2. Launch All Services
```bash
# Start all services in background
docker-compose up -d

# Check service status
docker-compose ps

# View logs (optional)
docker-compose logs -f
```

### 3. Wait for Services to Be Ready
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Register your first user**: http://localhost:3000/register

---

## 📋 Service Details

### Frontend (React + TypeScript)
- **URL**: http://localhost:3000
- **Technology**: React 18, TypeScript, Vite, Tailwind CSS
- **Features**: Authentication, Dashboard, Teams, Events, Submissions, Evaluations

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health
- **Technology**: FastAPI, SQLAlchemy, PostgreSQL, JWT Authentication

### Database (PostgreSQL)
- **Host**: localhost:5432
- **Database**: kazrockets
- **Username**: kazrockets
- **Password**: password
- **Connection**: `postgresql://kazrockets:password@localhost:5432/kazrockets`

### Cache (Redis)
- **Host**: localhost:6379
- **Usage**: Session storage, API caching
- **Test**: `redis-cli ping`

### Message Queue (RabbitMQ)
- **Host**: localhost:5672
- **Management UI**: http://localhost:15672
- **Username**: guest
- **Password**: guest
- **Usage**: Async file processing, notifications

### File Storage (MinIO)
- **API**: http://localhost:9000
- **Console**: http://localhost:9001
- **Username**: minioadmin
- **Password**: minioadmin
- **Bucket**: kazrockets-submissions

---

## 🔧 Development Workflow

### Running Individual Services

#### Backend Only
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Only
```bash
cd frontend
npm install
npm run dev
```

#### Database Only
```bash
docker-compose up -d db
```

### Environment Variables
Key environment variables in `.env`:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://kazrockets:password@localhost:5432/kazrockets

# JWT Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# API URL for Frontend
VITE_API_URL=http://localhost:8000

# MinIO (File Storage)
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

---

## 🧪 Testing the Application

### 1. User Registration Flow
```bash
# Register an Organizer
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "organizer@test.com",
    "password": "password123",
    "name": "Test Organizer",
    "role": "ORGANIZER"
  }'

# Register a Participant
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "participant@test.com",
    "password": "password123", 
    "name": "Test Participant",
    "role": "PARTICIPANT"
  }'

# Register a Judge
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "judge@test.com",
    "password": "password123",
    "name": "Test Judge", 
    "role": "JUDGE"
  }'
```

### 2. API Testing with Authentication
```bash
# Login and get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "organizer@test.com", "password": "password123"}' \
  | jq -r '.tokens.access_token')

# Create an event (Organizer only)
curl -X POST "http://localhost:8000/api/v1/events/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Robotics Championship 2024",
    "start_date": "2024-07-01T10:00:00Z",
    "end_date": "2024-07-03T18:00:00Z"
  }'

# Get all events
curl -X GET "http://localhost:8000/api/v1/events/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🗄️ Database Schema

### Core Tables
1. **app_users** - User accounts (participants, organizers, judges)
2. **teams** - Competition teams
3. **competitive_events** - Robotics competitions
4. **submissions** - Team project submissions (PDF files)
5. **evaluations** - Judge scores and comments

### Relationships
- Users can belong to teams (many-to-one)
- Teams have captains (one-to-one with users)
- Teams submit to events (many-to-many via submissions)
- Judges evaluate submissions (many-to-many via evaluations)

---

## 🔒 User Roles & Permissions

### PARTICIPANT
- Create and join teams
- Submit project files
- View own team's submissions and scores

### ORGANIZER  
- Create and manage events
- View all teams and users
- Approve/reject submissions
- Declare event winners

### JUDGE
- Evaluate submissions (score 0-100)
- Add comments to evaluations
- View submission details

---

## 📊 Monitoring & Logs

### Service Health Checks
```bash
# Check all services
docker-compose ps

# Backend health
curl http://localhost:8000/health

# Database connection
docker-compose exec db pg_isready -U kazrockets

# Redis connection  
docker-compose exec redis redis-cli ping

# RabbitMQ status
curl -u guest:guest http://localhost:15672/api/overview
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U kazrockets -d kazrockets

# Useful queries
SELECT COUNT(*) FROM app_users;
SELECT name, role FROM app_users;
SELECT title, start_date FROM competitive_events;
```

---

## 🛠️ Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 <PID>
```

#### Database Connection Failed
```bash
# Reset database
docker-compose down -v
docker-compose up -d db
# Wait 30 seconds
docker-compose up -d backend
```

#### Services Not Starting
```bash
# Check Docker resources
docker system df
docker system prune

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Permission Denied (MinIO)
```bash
# Reset MinIO data
docker-compose down
docker volume rm kazrockets_minio_data
docker-compose up -d minio
```

### Reset Everything
```bash
# Complete reset (WARNING: Deletes all data)
docker-compose down -v
docker system prune -f
docker-compose up -d
```

---

## 🚢 Deployment Considerations

### Environment Configuration
- Change `JWT_SECRET_KEY` in production
- Update CORS origins for production domains
- Configure proper database credentials
- Set up SSL certificates
- Configure file storage (AWS S3 instead of MinIO)

### Scaling
- Backend: Add load balancer, multiple instances
- Database: Read replicas, connection pooling
- Redis: Cluster mode for high availability
- Frontend: CDN for static assets

### Security
- Enable HTTPS
- Configure firewall rules
- Regular security updates
- Monitor for vulnerabilities
- Implement rate limiting

---

## 📞 Support

### Logs Location
- Backend: `docker-compose logs backend`
- Frontend: `docker-compose logs frontend`
- Database: `docker-compose logs db`

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=debug
docker-compose up -d backend
```

### Performance Monitoring
- Backend metrics: http://localhost:8000/api/v1/docs
- RabbitMQ metrics: http://localhost:15672
- Database queries: Check logs with `LOG_LEVEL=debug`

---

## 🎯 Next Steps

1. **Try the Web Interface**: Go to http://localhost:3000
2. **Register Users**: Create accounts with different roles
3. **Create Teams**: Form robotics teams
4. **Set Up Events**: Create competitions
5. **Submit Projects**: Upload PDF submissions
6. **Judge Submissions**: Score and evaluate projects
7. **API Integration**: Use the REST API for custom integrations

---

**🎉 Your KazRockets MVP is now running!**