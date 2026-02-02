# Research: Authentication Integration for Todo Application

## Overview
Research for Better Auth integration to provide secure user signup/signin and protected backend API access using JWT tokens and Better Auth–managed database tables.

## Better Auth Database Tables Research

### Default Database Schema
Better Auth automatically creates the following core tables:
- **User table**: Stores user information including email, name, email verification status, and timestamps
- **Session table**: Manages user sessions with tokens, expiration times, and user associations
- **Account table**: Links user accounts to different providers (for social login)
- **Verification table**: Handles email verification and password reset tokens

### Custom Schema Capabilities
Better Auth allows customization of table and column names:
- `modelName` option to change table names (e.g., "users" instead of default)
- `fields` mapping to customize column names (e.g., "full_name" instead of "name")
- Automatic creation of indexes for performance optimization

## JWT Plugin Configuration Research

### Basic JWT Setup
Better Auth provides a JWT plugin that can be configured as follows:
```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
    plugins: [
        jwt(),
    ]
})
```

### JWT Token Claims
- Standard claims include: sub (subject/user ID), iss (issuer), aud (audience), exp (expiration), iat (issued at)
- Custom claims can be added using plugin configuration
- User ID is available in the token for ownership verification

## Secret Key Management Research

### Environment Variables
Better Auth uses environment variables for secure secret management:
- `BETTER_AUTH_SECRET` environment variable for JWT signing
- Secrets should be the same in both frontend and backend for proper token verification
- Proper handling through environment configuration files

## Frontend Integration Research

### Better Auth Client
- Better Auth provides a client library for frontend integration
- Handles user state management and session persistence
- Automatically includes JWT tokens in API requests
- Provides authentication state hooks for UI integration

### Authentication Flows
- Sign-up flow: Creates user account and establishes session
- Sign-in flow: Validates credentials and establishes session
- Sign-out flow: Destroys session and clears local storage

## Backend Integration Research

### JWT Verification Middleware
- FastAPI middleware to extract JWT from Authorization header
- Verification of token signature using shared secret
- Extraction of user ID from token claims for ownership validation
- Proper error handling for invalid/missing tokens

### API Protection Strategies
- All endpoints require valid JWT tokens
- 401 Unauthorized responses for unauthenticated requests
- Ownership validation by matching token user ID with requested resource
- Filtering of data based on authenticated user ID

## Integration Patterns Research

### Frontend-Backend Communication
- JWT tokens automatically attached to API requests by Better Auth client
- Authorization header format: `Bearer {jwt_token}`
- Backend verifies token and extracts user identity for each request
- Proper error handling for expired or invalid tokens

### User Isolation Implementation
- Database queries filtered by authenticated user ID
- Ownership validation on all CRUD operations
- Prevention of cross-account access through token validation
- Consistent application of user context across all operations

## Implementation Considerations

### Security Best Practices
- Use HTTPS for all authentication flows
- Proper secret rotation and management
- Token expiration and refresh mechanisms
- Protection against common web vulnerabilities (XSS, CSRF)

### Performance Optimization
- Efficient database queries with proper indexing
- JWT validation performance under 100ms
- Session management without impacting user experience
- Caching strategies for repeated operations

### Error Handling
- Graceful handling of authentication failures
- Clear error messages for users
- Proper logging for debugging
- Recovery flows for common error scenarios

## Technology Stack Alignment

### Frontend Technologies
- Next.js 16+ with App Router for navigation
- Better Auth client for authentication management
- React hooks for state management
- Tailwind CSS for responsive design

### Backend Technologies
- FastAPI for REST endpoints
- SQLModel for database operations
- Neon Serverless PostgreSQL for data storage
- JWT for token-based authentication

## Deployment Considerations

### Environment Configuration
- Proper setup of BETTER_AUTH_SECRET in production
- Database connection configuration for Neon PostgreSQL
- CORS configuration for frontend-backend communication
- SSL/TLS setup for secure communication

### Scaling Factors
- Session management in serverless environments
- Database connection pooling considerations
- JWT validation performance at scale
- User isolation maintenance with increasing users