---
name: database-schema-design
description: Design robust database schemas using tables, relationships, and migrations. Use for backend and data-driven applications.
---

# Database Schema Design

## Instructions

1. **Schema Planning**
   - Identify entities and relationships
   - Define primary and foreign keys
   - Normalize data (avoid duplication)

2. **Table Creation**
   - Use appropriate data types
   - Apply constraints (NOT NULL, UNIQUE)
   - Add indexes for performance

3. **Migrations**
   - Version-control schema changes
   - Write reversible migrations (up & down)
   - Keep migrations small and atomic

## Best Practices
- Follow naming conventions (snake_case)
- Avoid storing derived data
- Use foreign keys for data integrity
- Plan for scalability early
- Document schema decisions

## Example Structure
```sql
-- users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- posts table
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
