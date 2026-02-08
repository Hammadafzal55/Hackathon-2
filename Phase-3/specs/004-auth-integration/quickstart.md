# Quickstart Guide: Authentication Integration for Todo Application

## Overview
Quickstart guide for implementing authentication integration using Better Auth with JWT-based verification and Better Auth–managed database tables. This guide covers setting up the authentication system and integrating it with the existing todo application.

## Prerequisites

### Development Environment
- Node.js 18+ installed
- Python 3.11+ installed
- npm or yarn package manager
- Git for version control
- Modern web browser (Chrome, Firefox, Safari, Edge)
- PostgreSQL client (for database inspection)

### Project Dependencies
- Next.js 16+ with App Router
- React 18+
- TypeScript 5.0+
- Tailwind CSS configured
- FastAPI backend
- SQLModel ORM
- Existing frontend and backend codebases from previous features

### Better Auth Requirements
- Better Auth library (latest version)
- JWT plugin for Better Auth
- Environment variable for BETTER_AUTH_SECRET

## Setup Process

### 1. Install Better Auth Dependencies
```bash
# Navigate to frontend directory
cd frontend

# Install Better Auth and related dependencies
npm install better-auth @better-auth/cli
# or
yarn add better-auth @better-auth/cli
```

### 2. Install Backend Dependencies
```bash
# Navigate to backend directory
cd backend

# Install any required backend dependencies (if needed)
pip install python-jose[cryptography]  # For JWT handling in FastAPI
```

### 3. Configure Environment Variables
Create/update environment files with authentication secrets:

**Frontend (.env.local)**:
```
BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

**Backend (.env)**:
```
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
DATABASE_URL=postgresql://...
```

## Implementation Steps

### Step 1: Set Up Better Auth on Frontend
1. Create the authentication client configuration
2. Set up the authentication provider wrapper
3. Implement sign-up/sign-in/sign-out functionality
4. Configure JWT token handling

### Step 2: Configure Better Auth Database Integration
1. Configure Better Auth to use Neon PostgreSQL
2. Allow Better Auth to create and manage its required tables
3. Verify that Better Auth tables are created successfully
4. Set up proper database indexing for performance

### Step 3: Implement Frontend Authentication Integration
1. Store authentication state using React Context
2. Attach JWT token to all API requests automatically
3. Update header UI to reflect authenticated state
4. Implement UI toggling between unauthenticated (Signup/Signin) and authenticated (Signout/Todo) states

### Step 4: Set Up Shared Secret Configuration
1. Define BETTER_AUTH_SECRET environment variable consistently
2. Ensure same secret is used in both frontend and backend
3. Verify secret loading in both environments
4. Test secret configuration with a simple JWT validation

### Step 5: Implement Backend JWT Verification
1. Create FastAPI middleware or dependency for JWT verification
2. Extract JWT from Authorization header
3. Verify token signature using shared secret
4. Decode token to retrieve user identity from Better Auth claims

### Step 6: Protect API Endpoints
1. Require valid JWT for all task endpoints
2. Reject requests without valid token
3. Reject requests with invalid/expired token
4. Match token user ID with request user_id for ownership validation

### Step 7: Enforce Task Ownership
1. Filter all database queries by authenticated user
2. Ensure tasks align with Better Auth user identity
3. Enforce ownership on all CRUD operations
4. Prevent cross-user data access

## Running the Auth-Protected Application

### Development Mode
```bash
# Terminal 1: Start the backend server
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start the frontend development server
cd frontend
npm run dev
# or
yarn dev

# Visit http://localhost:3000 to see the authenticated application
```

### Building for Production
```bash
# Build the frontend
cd frontend
npm run build

# The backend is typically deployed separately
# Follow your cloud provider's instructions for FastAPI deployment
```

## Key Components to Implement

### Better Auth Client Configuration
- Main authentication client with JWT plugin
- Environment-based configuration
- Error handling and retry mechanisms
- Session management utilities

### Authentication Provider Component
- React Context provider for authentication state
- Hooks for accessing authentication status
- Methods for sign-up, sign-in, and sign-out
- Loading and error states

### JWT Verification Middleware
- FastAPI dependency for token validation
- User ID extraction from token claims
- Ownership validation for requested resources
- Proper error responses for invalid tokens

### Protected API Endpoints
- Authentication-required task endpoints
- User ID validation against token claims
- Data filtering by authenticated user
- Proper error handling for unauthorized access

### Authentication-Aware UI Components
- Dynamic header that shows different options based on auth state
- Protected routes that redirect unauthenticated users
- Loading states during authentication checks
- Error displays for authentication failures

## Configuration Files

### Frontend Auth Configuration
- Create auth.ts file with Better Auth client configuration
- Enable JWT plugin with proper settings
- Configure base URLs and authentication callbacks
- Set up proper error handling

### Backend JWT Middleware
- Create auth_middleware.py with JWT verification logic
- Define proper exception handlers
- Configure secret key loading from environment
- Set up user context for request handlers

## Testing the Authentication System

### Authentication Flow Testing
- Register a new user and verify account creation
- Sign in and verify JWT token reception
- Sign out and verify session invalidation
- Attempt to access protected endpoints without token

### Task Ownership Testing
- Create tasks as one user and verify access
- Attempt to access another user's tasks (should fail)
- Verify that unauthenticated users get 401 responses
- Test token expiration and refresh mechanisms

### Security Testing
- Attempt to forge JWT tokens (should be rejected)
- Test concurrent sessions for the same user
- Verify that user data remains isolated
- Test error handling for invalid authentication states

### Performance Testing
- Measure JWT validation time (should be <100ms)
- Test concurrent user authentication
- Verify that session management doesn't impact performance
- Monitor database query performance with user filtering

## Troubleshooting Common Issues

### Authentication Not Working
- Verify that BETTER_AUTH_SECRET is identical in frontend and backend
- Check that environment variables are properly loaded
- Ensure CORS settings allow communication between frontend and backend
- Verify that Better Auth database tables were created properly

### JWT Token Validation Failing
- Confirm that the same secret key is used in both environments
- Check that tokens are properly formatted in Authorization header
- Verify that token expiration is handled correctly
- Ensure token signing algorithm matches verification

### Database Connection Issues
- Verify database URL is properly configured
- Check that Better Auth has proper permissions to create tables
- Ensure Neon PostgreSQL connection pool settings are appropriate
- Verify that authentication-related indexes exist

## Next Steps

After completing the authentication integration:
1. Conduct thorough testing across different user scenarios
2. Perform security audit and address any vulnerabilities
3. Optimize JWT validation performance
4. Update documentation with authentication patterns
5. Prepare for user acceptance testing
6. Plan for production deployment with proper security measures