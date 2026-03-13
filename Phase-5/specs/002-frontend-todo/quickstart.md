# Quickstart Guide: Todo Frontend Application

## Prerequisites

- Node.js 18.x or higher
- npm or yarn package manager
- Access to the Todo Backend API (running on http://localhost:8000 by default)

## Setup Instructions

### 1. Clone and Initialize
```bash
# Clone the repository
git clone <repository-url>
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### 2. Environment Configuration
Create a `.env.local` file in the project root:

```env
# Backend API configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_FIXED_USER_ID=123e4567-e89b-12d3-a456-426614174000
```

### 3. Run the Development Server
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

## Key Features Setup

### API Integration
The frontend communicates with the backend API using the configured base URL. All API calls include the fixed user ID in the path.

### Component Structure
- `src/app/page.tsx` - Main todo page
- `src/components/TaskList.tsx` - Task listing component
- `src/components/TaskItem.tsx` - Individual task display
- `src/components/TaskForm.tsx` - Task creation/editing form
- `src/lib/api.ts` - API client functions

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run linter

## First Steps

1. Verify the backend API is running at the configured URL
2. Start the frontend development server
3. Navigate to the application in your browser
4. Verify you can see the task list (should be empty initially)
5. Test creating a new task using the form
6. Verify the task appears in the list and is persisted in the backend

## Troubleshooting

### Common Issues
- **API Connection Errors**: Verify the backend is running and the API URL is correct
- **CORS Issues**: Ensure the backend allows requests from the frontend origin
- **Empty Task List**: This is expected if no tasks exist yet

### Verification Commands
```bash
# Check if backend is accessible
curl http://localhost:8000/health

# Check if frontend is running
curl http://localhost:3000
```