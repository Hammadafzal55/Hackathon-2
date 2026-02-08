<!-- SYNC IMPACT REPORT
Version change: 1.0 → 2.0
Modified principles: All principles were replaced to reflect the AI Chatbot nature
Added sections: None removed, but all content updated for AI/MCP focus
Removed sections: Previous web application-specific principles
Templates requiring updates:
- ✅ .specify/templates/plan-template.md - needs AI/MCP focus update
- ✅ .specify/templates/spec-template.md - needs AI/MCP focus update
- ✅ .specify/templates/tasks-template.md - needs AI/MCP focus update
- ⚠ .specify/templates/commands/*.md - may need updates for AI focus
- ⚠ README.md - may need updates for AI focus

Follow-up TODOs: Verify plan/spec/tasks templates are updated
-->

# Todo AI Chatbot Constitution (Phase III)

## Core Principles

### 1. Agent-first Development
Implementation must follow spec → plan → tasks → implementation workflow. All development activities must be executed via Claude Code tools. No manual coding is permitted. MCP (Model Context Protocol) tools must be used for all functionality.

### 2. Stateless Architecture
FastAPI server must remain stateless at all times with database-backed state persistence. Conversation history must be reconstructed from database on each request. Server must hold zero in-memory session or conversation state. All user and assistant messages must be persisted.

### 3. Tool-driven AI Behavior
AI agents must operate through MCP tools only, with no direct database access. All task operations must be executed via MCP tools only. MCP tools must be single-responsibility and stateless. AI logic must use OpenAI Agents SDK with Official MCP SDK.

### 4. Natural Language Interface
Users must be able to manage todos via natural language interactions. AI must correctly infer intent and invoke appropriate MCP tools. Frontend must use OpenAI ChatKit for seamless natural language communication. User experience must feel conversational and intuitive.

### 5. Reliability and Persistence
System must handle reliability across restarts and deployments. Conversation history must persist across server restarts. All user data must be stored persistently in Neon Serverless PostgreSQL. Error handling must be graceful and informative to users.

### 6. Security and Authentication
Authentication must be enforced via Better Auth for all interactions. All API endpoints must require valid authentication tokens. User data must be isolated so users can only access their own data. Secure handling of secrets and credentials using environment variables.

## Technical Standards

### Backend
FastAPI + SQLModel with stateless architecture, RESTful endpoints with consistent JSON responses. Proper request validation using Pydantic models. Conversation reconstruction from database on each request. No in-memory session state.

### Frontend
OpenAI ChatKit for natural language interface, responsive layouts, conversation-focused components. Client-side state management using React Context or Zustand. Proper conversation handling with validation. Accessibility-compliant markup and semantics.

### AI Framework
OpenAI Agents SDK for AI logic implementation, with proper tool integration and function calling. Intent recognition and mapping to appropriate MCP tools. Error handling for AI operations and tool invocations.

### MCP Server
Official MCP SDK implementation with single-responsibility tools. Statelessness enforced for all MCP tools. Proper error handling and validation for tool operations. Secure tool invocation and response formatting.

### Database
Neon Serverless PostgreSQL with proper foreign key relationships for conversation history. Conversation storage and retrieval mechanisms. Proper indexing for frequently queried conversation fields. Transaction management for data consistency.

### Authentication
Better Auth + JWT integration with secure secret handling. Session management with proper token expiration. Secure transmission of tokens using HTTPS. User isolation enforcement for conversation data.

### Development Workflow
Agentic Dev Stack — spec → plan → tasks → Claude Code implementation. All functionality implemented via MCP tools only. Comprehensive testing at all levels (unit, integration, end-to-end). No manual coding outside Claude Code tools.

### Code Quality
TypeScript for frontend, Pydantic validation for backend, modular design. Type safety and strict null checking enabled. Consistent linting and formatting rules. Comprehensive test coverage for critical functionality.

### Documentation
Full API docs, MCP tool documentation, and component usage notes. Inline code documentation for complex logic. Setup guides for new developers. Architecture decision records (ADRs) for significant choices.

## Constraints

### Functional Constraints
Must implement natural language todo management via AI chatbot. All user data stored persistently in PostgreSQL. MCP-based architecture required for all operations. Conversations must be linked to users via foreign keys.

### Process Constraints
No manual coding — all implementation via Claude Code and Spec-Kit Plus. Frontend must use OpenAI ChatKit exclusively. AI must use OpenAI Agents SDK, MCP server must use Official MCP SDK. Styling: Tailwind CSS or CSS Modules, mobile-first responsive design.

### Technical Constraints
Technology stack is fixed: OpenAI ChatKit frontend, Python FastAPI backend, OpenAI Agents SDK, Official MCP SDK, SQLModel ORM, Neon Serverless PostgreSQL, Better Auth.
MCP tools must be single-responsibility and stateless.
Server must hold zero in-memory session or conversation state.

### Architectural Constraints
Not building stateful chat servers or in-memory agents. No direct database access by AI agents. No UI-heavy or non-chat-based task management. No advanced AI features beyond defined task operations. No manual task CRUD outside MCP tools.

## Success Criteria

### Backend Functionality
All backend endpoints functional and stateless with database-backed persistence. Proper error handling and validation for all operations. Efficient database operations for conversation storage/retrieval. Secure authentication and authorization.

### Frontend Functionality
Frontend fully responsive with working conversation interface and components. Natural language interaction feels smooth and intuitive. Proper conversation navigation and routing. Cross-browser compatibility.

### AI Behavior
AI correctly infers intent and invokes MCP tools appropriately. Natural language processing works reliably for common todo operations. Conversations flow naturally and responses are contextually appropriate. Error handling for AI operations is graceful.

### Security Requirements
Authentication secure: JWTs valid, expired tokens rejected, user isolation enforced. No unauthorized access to other users' conversations or data. Secure handling of sensitive information. Protection against common security vulnerabilities.

### Database Requirements
Database migrations applied correctly; conversations linked to users. Proper data integrity and consistency for conversation history. Efficient queries and indexing for conversation data. Proper backup and recovery procedures.

### Code Quality
Modular, maintainable, and production-ready code. Consistent coding standards across the project. Proper separation of concerns with MCP tools. Comprehensive error handling throughout.

### Documentation
Full project documentation completed, ready for handover or review. Clear API and MCP tool documentation with examples. Setup and deployment guides. Architecture and design decisions documented.

## Governance

This constitution governs all development activities for the Todo AI Chatbot (Phase III) project. All implementation must comply with these principles and standards. Any deviations require explicit approval and documentation of the rationale. The constitution version is 2.0 as this represents a significant architectural shift from the Phase II web application to the Phase III AI chatbot.

**Version**: 2.0 | **Ratified**: 2026-01-14 | **Last Amended**: 2026-02-07