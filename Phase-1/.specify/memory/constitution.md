<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 1.1.0
Modified Principles:
  - III. Zero External Dependencies: Updated to allow pytest for testing
  - IV. Console/CLI Interface: Updated to reflect interactive menu-driven interface as default
Modified Sections:
  - Constraints/Technology Stack: Updated Python version to 3.13+, testing to pytest
  - Definition of Done: Marked all items complete
Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section references updated principles
  ✅ spec-template.md - Scope constraints aligned with Phase 1 principles
  ✅ tasks-template.md - Task organization aligned with modular testing principle
Follow-up TODOs: None

CONSTITUTION VERSIONING DECISION:
  - 1.0.0: Initial ratification with complete principle set for Phase 1 project
  - 1.1.0: Updated to reflect actual implementation (interactive CLI, pytest)
  - Rationale: Minor version bump for material guidance expansion (interactive mode)
-->

# Phase 1 Todo In-Memory Python Console App Constitution

## Core Principles

### I. In-Memory Only (NON-NEGOTIABLE)

All data storage MUST occur in memory at runtime. No persistence mechanisms (databases, files, external APIs) are permitted in Phase 1.

- Tasks exist only for the duration of the Python process execution
- No file I/O for data storage, loading, or saving
- No external database connections or queries
- Restarting the application clears all data - this is expected behavior
- Rationale: Phase 1 focuses on core CRUD operations and CLI patterns without persistence complexity

### II. Phase 1 Scope Boundary (NON-NEGOTIABLE)

All development MUST be restricted to 5 defined core operations only.

- **Add**: Create new tasks in the in-memory list
- **View**: List all tasks, optionally filtered by status
- **Update**: Modify task descriptions
- **Delete**: Remove tasks from the list
- **Mark Complete/Incomplete**: Toggle task status between "todo" and "done"

No additional features (search, categories, priorities, due dates, sorting, etc.) are permitted in Phase 1.
- Rationale: Establishes clear MVP boundaries and prevents scope creep

### III. Minimal External Dependencies (NON-NEGOTIABLE)

The application MUST use Python standard library for core functionality.

- Core application logic uses only standard library modules
- pytest is permitted as the sole external dependency (for testing only)
- No external APIs or services
- No frameworks (no Flask, FastAPI, Click, etc.)
- Use built-in modules (sys, typing, dataclasses, etc.) for application code
- Rationale: Ensures portability and simplicity while allowing modern testing practices

### IV. Interactive Console Interface (NON-NEGOTIABLE)

All user interaction MUST occur through a menu-driven interactive command-line interface.

- Default mode: Interactive menu with numbered options (run via `uv run todo`)
- Alternative mode: Direct commands via `uv run todo <command> [args]` pattern
- Standard input/output for user communication (stdin/stdout)
- Error messages displayed inline with user-friendly formatting
- Continuous loop until user explicitly exits
- Clear screen between operations for clean UI
- Rationale: Phase 1 is explicitly a console application with interactive user experience

### V. Modular and Testable (NON-NEGOTIABLE)

Code MUST be structured in modular, independently testable components.

- Separation of concerns: Model logic separate from CLI command handlers
- Small, focused functions (single responsibility principle)
- Type hints for all function signatures
- Comprehensive docstrings for all public functions
- Unit tests for all model operations and business logic
- Tests written before implementation (Red-Green-Refactor cycle)
- Rationale: Ensures maintainability, testability, and clean architecture

### VI. Demo-Ready Quality (NON-NEGOTIABLE)

The application MUST be clean, readable, and suitable for demonstration.

- Clear, descriptive variable and function names
- Consistent code formatting and style
- Helpful error messages that guide users
- Documentation (README.md) with clear setup and usage instructions
- Working examples in documentation
- Rationale: Phase 1 is for demonstration and learning - code quality matters

## Code Standards

### Naming Conventions

- **Functions**: lowercase_with_underscores (e.g., `add_task`, `list_tasks`)
- **Classes**: PascalCase (e.g., `Task`, `TaskManager`)
- **Constants**: UPPER_CASE_WITH_UNDERSCORES (e.g., `MAX_TASKS`, `DEFAULT_STATUS`)
- **Files**: lowercase_with_underscores (e.g., `task.py`, `cli_handlers.py`)

### Code Organization

- `src/models/`: Data models and business logic
- `src/cli/`: Command-line interface handlers
- `src/main.py`: Application entry point
- `tests/`: Unit tests (mirror src structure)

### Type Hints

All function signatures MUST include type hints:
```python
def add_task(tasks: List[Task], description: str) -> Task:
    ...
```

### Docstrings

All public functions MUST include docstrings with:
- Brief description
- Args section with type and purpose
- Returns section with type and description
- Raises section for exceptions (if applicable)

### Error Handling

- Validate all user input before processing
- Raise specific exceptions (ValueError, KeyError, etc.) with clear messages
- Catch exceptions at CLI layer and display user-friendly errors
- Never expose internal stack traces to users

## Development Workflow

### Specification Phase

1. **Feature Definition**: Use `/sp.specify` to create feature specifications
2. **Requirement Clarification**: Use `/sp.requirement-clarify` to resolve ambiguities
3. **CLI Design**: Use `/sp.cli-design` to define command interfaces
4. **Planning**: Use `/sp.plan` to create implementation architecture

### Implementation Phase

1. **Task Breakdown**: Use `/sp.tasks` to create testable implementation tasks
2. **Implementation**: Use `/sp.python-console` to write modular Python code
3. **Testing**: Write unit tests for all components (Red-Green-Refactor)
4. **Validation**: Verify all acceptance criteria pass

### Quality Gates

- All unit tests pass before committing
- Code follows constitution principles (manual review)
- Documentation updated (README.md)
- Demo-ready quality (clean, readable, working examples)

## Constraints

### Technology Stack

- **Language**: Python 3.13+ (managed via uv)
- **Storage**: In-memory data structures (lists, dataclasses)
- **Interface**: Interactive console menu (default) + CLI commands
- **Testing**: pytest (external dependency for testing only)
- **Package Manager**: uv
- **Dependencies**: pytest (testing only)

### Performance (Phase 1 Targets)

- Support for 1000+ tasks in memory (no degradation)
- Command execution under 100ms for typical operations
- Memory usage under 50MB for 1000 tasks

### Scope Boundaries (Explicitly Out of Scope)

- No persistence or data saving
- No search functionality
- No task categories or tags
- No priorities or due dates
- No sorting or filtering beyond status
- No multiple lists or workspaces
- No user authentication or multi-user support
- No web or GUI interface

## Definition of Done

A feature is complete when:

- [x] All 5 core operations work correctly (Add, View, Update, Delete, Mark Complete/Incomplete)
- [x] All unit tests pass (53 tests via pytest)
- [x] Code follows all constitution principles
- [x] Interactive menu interface works as designed
- [x] Error messages are clear and helpful
- [x] README.md includes setup and usage instructions
- [x] Application is demo-ready (can be run and demonstrated via `uv run todo`)

## Governance

### Constitution Authority

This constitution supersedes all other project practices and guidelines.

- All code changes must verify compliance with constitution principles
- Any violation must be explicitly justified in the implementation plan
- Constitution updates require documentation of changes, rationale, and impact

### Amendment Process

1. **Proposal**: Document proposed change with rationale
2. **Review**: Assess impact on existing code and principles
3. **Version**: Increment version according to semantic versioning:
   - MAJOR: Backward-incompatible principle removal or redefinition
   - MINOR: New principle or material guidance expansion
   - PATCH: Clarification, wording, or non-semantic refinement
4. **Approval**: Requires explicit consensus (or user approval in AI context)
5. **Propagation**: Update dependent templates and documentation

### Compliance Review

- All pull requests must include constitution compliance check
- Plan templates must reference constitution gates
- Spec templates must enforce phase scope boundaries
- Task templates must align with modular testing principle

### Runtime Guidance

Use `CLAUDE.md` for runtime development guidance and specific workflow instructions.

---

**Version**: 1.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2025-12-29
