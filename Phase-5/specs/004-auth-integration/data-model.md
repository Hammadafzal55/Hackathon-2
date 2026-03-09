# Data Model: Authentication Integration for Todo Application

## Overview
Data model for authentication integration using Better Auth with JWT-based verification and Better Auth–managed database tables. This model defines the authentication-related entities and their relationships with the existing task management system.

## Authentication Entities

### User (Managed by Better Auth)
Represents an authenticated user with email, password hash (managed by Better Auth), and account status; serves as the owner of tasks.

**Fields**:
- `id`: string (Primary Key) - Unique identifier for the user
- `name`: string - User's full name
- `email`: string (Unique) - User's email address
- `emailVerified`: boolean - Whether the email has been verified
- `image`: string (Optional) - Profile image URL
- `createdAt`: timestamp - Account creation time
- `updatedAt`: timestamp - Last account update time
- `twoFactorEnabled`: boolean - Whether two-factor authentication is enabled
- `username`: string (Optional, Unique) - User's chosen username

**Relationships**:
- One-to-Many: User → Tasks (via user_id foreign key)

**Validation**:
- `email` must be a valid email format
- `email` must be unique across all users
- `name` must be non-empty
- `id` must be unique

### Session (Managed by Better Auth)
Represents an active user session with token, expiration time, and IP/user agent information.

**Fields**:
- `id`: string (Primary Key) - Unique session identifier
- `expiresAt`: timestamp - Session expiration time
- `token`: string (Unique) - Session token
- `createdAt`: timestamp - Session creation time
- `ipAddress`: string (Optional) - IP address of the session
- `userAgent`: string (Optional) - User agent string
- `userId`: string (Foreign Key) - Reference to the user who owns this session

**Relationships**:
- Many-to-One: Session → User (via userId foreign key)

**Validation**:
- `token` must be unique
- `expiresAt` must be in the future
- `userId` must reference an existing user

### Account (Managed by Better Auth)
Links user accounts to different authentication providers (for social login).

**Fields**:
- `id`: string (Primary Key) - Unique account identifier
- `providerId`: string - ID of the authentication provider
- `providerAccountId`: string - Account ID at the provider
- `refreshToken`: string (Optional) - OAuth refresh token
- `accessToken`: string (Optional) - OAuth access token
- `expiresAt`: timestamp (Optional) - Token expiration time
- `tokenType`: string - Type of token
- `scope`: string - OAuth scope
- `userId`: string (Foreign Key) - Reference to the user who owns this account

**Relationships**:
- Many-to-One: Account → User (via userId foreign key)

**Validation**:
- `userId` must reference an existing user
- `providerId` and `providerAccountId` combination must be unique

### Verification (Managed by Better Auth)
Handles email verification and password reset tokens.

**Fields**:
- `id`: string (Primary Key) - Unique verification identifier
- `identifier`: string - The identifier (e.g., email) being verified
- `value`: string - The verification token
- `expiresAt`: timestamp - Token expiration time
- `type`: string - Type of verification (email_verification, password_reset, etc.)

**Validation**:
- `expiresAt` must be in the future
- `type` must be one of the allowed verification types

## Application Entities

### Task (Application managed, with user relationship)
Belongs to a specific user, with access restricted to the owning user; includes user_id for ownership validation.

**Fields**:
- `id`: string (Primary Key) - Unique task identifier
- `title`: string - Task title
- `description`: string (Optional) - Task description
- `status`: string - Task status (pending, in_progress, completed, cancelled)
- `priority`: number - Priority level (1-5, where 1 is lowest)
- `due_date`: string (Optional) - Due date for the task
- `user_id`: string (Foreign Key) - Reference to the user who owns this task
- `created_at`: timestamp - Task creation time
- `updated_at`: timestamp - Last task update time
- `completed_at`: string (Optional) - Time when task was completed

**Relationships**:
- Many-to-One: Task → User (via user_id foreign key)

**Validation**:
- `user_id` must reference an existing user
- `title` must be non-empty
- `priority` must be between 1 and 5
- `status` must be one of the allowed values

## Authentication Token Model

### JWT Token
Contains user identity claims (user ID, email), expiration time, and is signed by Better Auth for authentication verification.

**Claims**:
- `sub` (Subject): User ID (matches the user.id from Better Auth)
- `iat` (Issued At): Timestamp when token was issued
- `exp` (Expiration): Timestamp when token expires
- `iss` (Issuer): Token issuer identifier
- `email`: User's email address (optional custom claim)

**Validation Rules**:
- Token signature must be valid (signed by Better Auth)
- Current time must be before `exp` (expiration)
- `sub` (user ID) must correspond to an existing user in the database
- Token must not be revoked (if using token revocation mechanism)

## State Transitions

### User Authentication States
- Unauthenticated → Authenticating (when user submits credentials)
- Authenticating → Authenticated (on successful authentication)
- Authenticating → Unauthenticated (on failed authentication)
- Authenticated → Unauthenticated (on sign-out or token expiration)

### Session States
- Active → Expired (when session reaches expiration time)
- Active → Revoked (on user-initiated logout)
- Expired/Revoked → Active (on new authentication)

## Validation Rules

### Authentication Compliance
- All API requests must include a valid JWT token in the Authorization header
- User ID in JWT token must match the requested resource ownership
- Sessions must be validated against the database for active status
- User accounts must be verified (emailVerified=true) before full access

### Data Integrity
- Foreign key relationships must be maintained between users and their tasks
- User IDs in JWT tokens must correspond to existing user records
- Task ownership cannot be transferred between users without proper authorization
- Session tokens must be unique and securely random

### Security Requirements
- Password hashes must never be exposed to the application layer (handled by Better Auth)
- Session tokens must be transmitted over HTTPS only
- JWT tokens must be validated with proper signature verification
- User data isolation must be enforced at the application level

### Performance Requirements
- JWT token validation must complete in under 100ms
- User lookup by ID must be efficient (proper indexing)
- Session validation must not significantly impact API response times
- Database queries must be optimized for concurrent user access