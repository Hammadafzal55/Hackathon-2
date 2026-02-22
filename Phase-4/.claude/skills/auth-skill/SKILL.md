---
name: auth-skill
description: Secure authentication using Better Auth on Next.js frontend and JWT verification in FastAPI backend with shared secret.
---

# Auth Skill – Better Auth + FastAPI

## Architecture Overview

- Frontend: Next.js + Better Auth (JavaScript)
- Backend: FastAPI (Python)
- Auth Method: JWT (Bearer Token)
- Auth State: Stateless (No backend sessions)

## Authentication Flow

1. **User Login (Frontend)**
   - User signs in via Better Auth
   - Better Auth creates a session
   - JWT token is issued using shared secret

2. **API Request (Frontend → Backend)**
   - JWT token attached in request header:
     ```
     Authorization: Bearer <token>
     ```

3. **JWT Verification (Backend)**
   - FastAPI extracts token from header
   - Verifies signature using shared secret
   - Decodes token to get `user_id`, `email`

4. **Authorization Enforcement**
   - Backend matches decoded `user_id`
   - Filters all DB queries by authenticated user
   - Prevents cross-user data access

## Required Component Changes

### 1. Better Auth Configuration (Frontend)
- Enable JWT plugin
- Set token expiry (e.g. 7 days)
- Use shared secret via environment variable

```env
BETTER_AUTH_SECRET=super-secret-key
