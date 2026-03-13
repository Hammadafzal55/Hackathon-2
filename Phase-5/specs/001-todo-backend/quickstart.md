# Quickstart Guide: Todo Backend Service

## Prerequisites

- Python 3.11+
- pip package manager
- Neon Serverless PostgreSQL account and connection string

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Copy the example environment file and configure your Neon PostgreSQL connection:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Neon PostgreSQL connection string:
   ```
   DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname
   ```

5. **Initialize the database**
   Run the database initialization script to create tables:
   ```bash
   python -m backend.src.database.init
   ```

## Running the Application

1. **Start the development server**
   ```bash
   uvicorn backend.src.main:app --reload --port 8000
   ```

2. **Access the API**
   The API will be available at `http://localhost:8000`
   Interactive API documentation available at `http://localhost:8000/docs`

## API Endpoints

- `GET /api/{user_id}/tasks` - List all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

## Environment Variables

- `DATABASE_URL` - Neon PostgreSQL connection string (required)
- `SECRET_KEY` - Secret key for JWT signing (required for auth)
- `ALGORITHM` - Algorithm for JWT encoding (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time in minutes (default: 30)

## Testing

Run the test suite:
```bash
pytest tests/
```

Run specific test files:
```bash
pytest tests/unit/test_tasks.py
pytest tests/integration/test_api.py
```