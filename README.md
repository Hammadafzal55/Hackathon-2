# 🚀 Hackathon-02: Full-Stack Todo Application

A comprehensive full-stack todo application built during the hackathon, featuring an in-memory CLI backend (Phase 1), RESTful API with FastAPI (Phase 2), and modern frontend architecture.

## 📋 Project Overview

This is a progressive development project showcasing the evolution from a simple CLI tool to a complete full-stack web application with authentication and data persistence.

### Phases

- **Phase 1**: Todo CLI Application (Python + In-Memory Storage)
- **Phase 2**: RESTful API Backend (FastAPI + PostgreSQL)
- **Phase 3+**: Frontend Integration & Advanced Features

---

## 🎯 Phase 1: Todo CLI Application

A command-line todo manager with an interactive interface and comprehensive menu-driven operations.

### Features

- ✅ **Add Tasks** with title and optional description
- 📝 **View All Tasks** with formatted display
- 🔄 **Update Tasks** - modify title or description
- ❌ **Delete Tasks** - remove from list
- ✔️ **Toggle Status** - mark complete/incomplete
- 💾 **In-Memory Storage** - all data persists during session

### Tech Stack

- Python 3.13+
- UV Package Manager
- pytest for testing (53 tests included)

### Getting Started

```bash
# Install dependencies
cd Phase-1/
uv pip install -e .

# Run interactive mode
uv run todo

# Run tests
uv run pytest -v
```

### Usage Examples

**Interactive Menu:**
```bash
uv run todo
```

**Command Mode:**
```bash
# Add task
uv run todo add "Buy groceries" --description "Milk, eggs, bread"

# View tasks
uv run todo view

# Mark complete
uv run todo complete 1

# Delete task
uv run todo delete 2
```

### Project Structure (Phase 1)

```
Phase-1/
├── src/
│   ├── main.py              # Application entry point
│   ├── models/
│   │   └── task.py          # Task model & business logic
│   └── cli/
│       ├── handlers.py      # Command handlers
│       └── interactive.py   # Interactive menu
├── tests/                   # 53 comprehensive tests
├── specs/                   # Feature specifications
└── README.md
```

---

## 🔌 Phase 2: RESTful API Backend

Production-ready FastAPI backend with secure authentication and user data isolation.

### Features

- 🔐 **JWT Authentication** - secure user access
- 👤 **User Data Isolation** - users can only access their own tasks
- 🗄️ **PostgreSQL** - persistent data storage with asyncpg
- 📊 **Database Migrations** - Alembic for schema management
- ⚡ **Async/Await** - high-performance request handling
- 🧪 **Comprehensive Error Handling** - structured logging

### Tech Stack

- FastAPI Web Framework
- SQLModel for ORM
- PostgreSQL Database
- Alembic Migrations
- Better Auth compatible JWT
- asyncpg for async database operations

### API Endpoints

```
GET    /api/{user_id}/tasks              # Get all user tasks
POST   /api/{user_id}/tasks              # Create new task
GET    /api/{user_id}/tasks/{id}         # Get specific task
PUT    /api/{user_id}/tasks/{id}         # Update task
DELETE /api/{user_id}/tasks/{id}         # Delete task
PATCH  /api/{user_id}/tasks/{id}/complete # Toggle completion
```

### Authentication

Include JWT token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Setup Instructions

```bash
# Install backend dependencies
cd Phase-2/backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and JWT secret

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/todo_db
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Migrations

```bash
# Run all pending migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Rollback last migration
alembic downgrade -1
```

### Interactive API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎨 Frontend (Phase 3+)

The frontend integration with modern UI/UX is being developed in the Phase 3 branches.

### Current Development Branches

- `004-auth-integration` - Authentication UI
- `005-mcp-task-tools` - Task management tools
- `006-ai-chat-api` - AI Chat integration
- `007-chatkit-frontend` - Chat interface
- `008-advanced-features` - Advanced features
- `009-dapr-minikube-deploy` - Deployment setup

---

## 📊 Project Statistics

- **Total Tests**: 53+ (Phase 1)
- **API Endpoints**: 6+ RESTful endpoints
- **Database Tables**: Users, Tasks with relationships
- **Authentication**: JWT-based with user isolation

---

## 🔄 Development Workflow

1. **Clone Repository**
   ```bash
   git clone https://github.com/Hammadafzal55/Hackathon-2.git
   cd Hackathon-2
   ```

2. **Check Out Phase**
   ```bash
   # Phase 1 (CLI)
   git checkout main  # or your feature branch
   
   # Phase 2 (API)
   git checkout main
   ```

3. **Install Dependencies**
   ```bash
   # Phase 1
   cd Phase-1 && uv pip install -e .
   
   # Phase 2
   cd Phase-2/backend && pip install -r requirements.txt
   ```

4. **Run Project**
   ```bash
   # Phase 1
   uv run todo
   
   # Phase 2
   uvicorn src.main:app --reload
   ```

---

## 🧪 Testing

### Phase 1 Tests

```bash
cd Phase-1
uv run pytest -v              # Run all tests
uv run pytest -v --cov        # With coverage report
uv run pytest tests/test_task.py  # Specific test file
```

### Phase 2 API Tests

```bash
cd Phase-2/backend
pytest tests/                 # Run all tests
pytest -v --cov src/         # With coverage
```

---

## 🚀 Deployment

### Phase 1 (CLI)
Runs locally without deployment requirements.

### Phase 2 (Backend)

**Docker Deployment:**
```bash
cd Phase-2
docker build -t hackathon-2-api .
docker run -p 8000:8000 --env-file .env hackathon-2-api
```

**Vercel/Railway:**
- Configure PostgreSQL database
- Set environment variables
- Push to GitHub and connect to platform

---

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Guide](https://sqlmodel.tiangolo.com/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)
- [Python CLI Design](https://click.palletsprojects.com/)

---

## 🤝 Contributing

This is a hackathon project. For development:

1. Create feature branch from appropriate phase
2. Follow project structure conventions
3. Add tests for new features
4. Update documentation
5. Submit for review

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Hammad Afzal** - Full-Stack Developer

---

## 📞 Support

For questions or issues:
- 📧 Email: [Your Email]
- 🐛 GitHub Issues: [Report Bug](https://github.com/Hammadafzal55/Hackathon-2/issues)
- 💬 Discussions: [Ask Question](https://github.com/Hammadafzal55/Hackathon-2/discussions)

---

**Last Updated**: 2026
**Status**: 🟢 Active Development
