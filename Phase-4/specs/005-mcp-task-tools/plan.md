# Implementation Plan: MCP Server + Task Tools Foundation

**Branch**: `005-mcp-task-tools` | **Date**: 2026-02-07 | **Spec**: [../spec.md](../spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integration of an MCP (Model Context Protocol) server within the existing FastAPI backend to expose task operations as MCP tools. The implementation leverages the Official MCP SDK to provide AI agents with safe access to task management functions (add, list, update, complete, delete) while enforcing user isolation through the existing Better Auth authentication system and SQLModel database layer.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Official MCP SDK, SQLModel, Better Auth
**Storage**: Neon Serverless PostgreSQL with SQLModel ORM
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Web backend with integrated MCP server
**Performance Goals**: Tool operations complete under 2 seconds
**Constraints**: Tools must be stateless, no in-memory session state, user isolation enforced via user_id
**Scale/Scope**: Support multiple concurrent AI agents accessing task operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Stateless Architecture**: MCP tools must be stateless and not hold in-memory state (FR-003)
- ✅ **Tool-driven AI Behavior**: All task operations exposed as MCP tools for AI access (FR-002)
- ✅ **Security and Authentication**: User isolation enforced via existing Better Auth user_id (FR-004, FR-007)
- ✅ **MCP Server Standards**: Implementation uses Official MCP SDK as required (FR-001)
- ✅ **Database Access**: All operations through SQLModel ORM (FR-005)
- ✅ **Backwards Compatibility**: No disruption to existing API endpoints (FR-006)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py      # Current task model
│   │   └── user.py      # Current user model
│   ├── services/
│   │   └── mcp_server.py # New MCP server module
│   ├── mcp_tools/       # New directory for task MCP tools
│   │   ├── __init__.py
│   │   ├── schemas.py   # Tool schemas
│   │   └── handlers.py  # Tool handler implementations
│   ├── api/
│   │   └── routes/
│   │       └── tasks.py # Current task API routes (unchanged)
│   └── main.py          # FastAPI app entry point (modified to include MCP server)
└── requirements.txt     # Updated with MCP SDK dependency
```

**Structure Decision**: The MCP server will be integrated directly into the existing FastAPI application using the services/ directory for the server implementation and a new mcp_tools/ directory for the specific tools. This maintains the existing project structure while cleanly separating MCP-specific functionality.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|