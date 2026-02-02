# Todo Backend API

A FastAPI-based backend service for managing user tasks with secure authentication and data isolation.

## Overview

This backend provides RESTful API endpoints for managing user tasks. It uses:
- **FastAPI** for the web framework
- **SQLModel** for database modeling and ORM
- **PostgreSQL** with asyncpg for database operations
- **Alembic** for database migrations
- **Better Auth compatible JWT** for authentication

## Features

- Create, read, update, and delete tasks
- Secure user authentication with JWT tokens
- User data isolation (users can only access their own tasks)
- RESTful API design
- Comprehensive error handling
- Structured logging

## API Endpoints

- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

## Authentication

The API expects JWT tokens in the Authorization header:
```
Authorization: Bearer <jwt-token>
```

The user ID in the URL must match the user ID in the JWT token for authorization.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and JWT secret
   ```

3. Run database migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

## Running the Application

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Database Setup

The application uses Alembic for database migrations:

1. To run the initial migration (after setting up PostgreSQL):
   ```bash
   cd backend
   alembic upgrade head
   ```

2. To create a new migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

3. To rollback a migration:
   ```bash
   alembic downgrade -1
   ```

The initial migration (001_initial_migration_users_tasks.py) is already created and will set up the users and tasks tables with proper relationships and indexes.

## Environment Variables

- `DATABASE_URL`: PostgreSQL database connection string
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)