---
name: backend-core
description: Generate backend routes, handle HTTP requests/responses, and connect to databases. Use for API and server-side development.
---

# Backend Core Skill

## Instructions

1. **Project setup**
   - Initialize backend project
   - Configure environment variables
   - Set up server entry point

2. **Routing**
   - Define RESTful routes (GET, POST, PUT, DELETE)
   - Organize routes by feature/module
   - Use route prefixes (e.g. `/api/v1`)

3. **Request & Response Handling**
   - Parse request body and params
   - Validate incoming data
   - Return proper HTTP status codes
   - Send JSON responses

4. **Database Connection**
   - Connect to database (MongoDB / PostgreSQL / MySQL)
   - Handle connection errors
   - Use models/schemas for data structure

5. **Error Handling**
   - Centralized error middleware
   - Meaningful error messages
   - Avoid exposing sensitive details

## Best Practices
- Follow REST API standards
- Keep controllers thin and reusable
- Use async/await for database operations
- Separate concerns (routes, controllers, models)
- Secure secrets using `.env`
- Always validate user input

## Example Structure
```js
// server.js
import express from "express";
import mongoose from "mongoose";

const app = express();
app.use(express.json());

// Route
app.get("/api/health", (req, res) => {
  res.status(200).json({ status: "OK" });
});

// Database connection
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("DB Connected"))
  .catch(err => console.error(err));

app.listen(3000, () => {
  console.log("Server running on port 3000");
});
