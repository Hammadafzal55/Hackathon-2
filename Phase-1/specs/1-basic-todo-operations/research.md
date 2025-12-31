# Research: Phase 1 Todo In-Memory Python Console App

**Feature**: 1-Basic-Todo-Operations
**Date**: 2025-12-29
**Purpose**: Resolve all technical decisions for implementation

## Overview

This document consolidates all technology and architecture decisions required to implement the Phase 1 Todo In-Memory Python Console App. All decisions are guided by the constitution principles and feature specification.

## Decisions

### 1. Data Structure for Task Storage

**Decision**: Python `List[Task]` with Task dataclass

**Rationale**:
- Lists maintain insertion order naturally (tasks display in creation order)
- O(1) access by index enables efficient task retrieval by ID
- Simple and straightforward - meets Phase 1 simplicity requirement
- Python dataclass provides clean, type-safe model definition

**Alternatives Considered**:
- `Dict[int, Task]` with ID as key: Rejected because ID reassignment after deletion would require complex key updates
- Custom `TaskManager` class: Rejected as unnecessary complexity for Phase 1
- `List[Dict]` for tasks: Rejected as less type-safe than dataclass

### 2. Task ID Management

**Decision**: Sequential 1-indexed integers with reassignment after deletion

**Rationale**:
- User-friendly display (IDs start at 1, not 0)
- Matches specification requirement for 1-to-N indexing
- Reassignment after deletion prevents gaps in index sequence

**Alternatives Considered**:
- Never reassign IDs (preserve gaps): Rejected because spec requires sequential 1-to-N indexing
- 0-indexed IDs: Rejected because spec assumes 1-indexing in all examples
- UUIDs: Rejected as unnecessary complexity and not user-friendly for CLI

### 3. Status Representation

**Decision**: String enumeration: `"incomplete"` or `"complete"`

**Rationale**:
- Simple and readable in CLI output
- No need for external enum libraries (standard library only)
- Easy to toggle between two states

**Alternatives Considered**:
- `enum.Enum`: Rejected to keep it simple and avoid import overhead
- Boolean `True/False`: Rejected as less readable in CLI output
- Integer codes (0/1): Rejected as less intuitive for users

### 4. Command Line Parsing

**Decision**: `argparse` module from Python standard library

**Rationale**:
- Built-in Python module (no dependencies - meets constitution)
- Automatic help generation (`-h`, `--help`)
- Type conversion and validation built-in
- Subcommand support for add/view/update/delete/complete

**Alternatives Considered**:
- `sys.argv` manual parsing: Rejected as more error-prone and no auto-help
- Click library: Rejected as external dependency (violates Principle III)
- `shlex` + custom parsing: Rejected as unnecessary complexity

### 5. CLI Output Formatting

**Decision**: Formatted strings with manual spacing, no external formatting libraries

**Rationale**:
- Standard library only (constitution requirement)
- Simple and predictable output
- Easy to test and maintain

**Alternatives Considered**:
- `rich` library: Rejected as external dependency
- `tabulate` library: Rejected as external dependency
- `f-string` with manual alignment: Chosen for simplicity and standard library

### 6. Error Handling Strategy

**Decision**: Raise specific exceptions in model layer, catch and format in CLI layer

**Rationale**:
- Separation of concerns (model raises exceptions, CLI displays user-friendly messages)
- Testable error conditions in unit tests
- Consistent error message format across all commands

**Alternatives Considered**:
- Print errors directly in model: Rejected as violates separation of concerns
- Return error codes/tuples: Rejected as less Pythonic and harder to test
- Exit immediately on errors: Rejected as prevents graceful error recovery

### 7. Testing Framework

**Decision**: `unittest` module from Python standard library

**Rationale**:
- Built-in Python module (no dependencies - meets constitution)
- Well-documented and widely understood
- Sufficient for Phase 1 testing needs

**Alternatives Considered**:
- `pytest` library: Rejected as external dependency (violates Principle III)
- `doctest`: Rejected as less suitable for complex multi-function testing
- Manual testing: Rejected as insufficient for TDD requirement

## Resolved Unknowns

All technical decisions from the implementation plan template have been resolved. No further research is required.

## Dependencies (None)

All dependencies are from Python standard library:
- `argparse` - Command line parsing
- `dataclasses` - Task model definition
- `typing` - Type hints
- `unittest` - Testing framework
- `sys` - I/O operations

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.8+ | Constitution requirement, standard library available |
| Storage | In-memory list | Spec requirement, O(1) index access |
| CLI | argparse | Standard library, auto-help, type validation |
| Testing | unittest | Standard library, TDD support |
| Dependencies | None | Constitution Principle III |

## Compliance

✅ All decisions comply with constitution principles:
- I. In-Memory Only: Using Python lists only
- II. Phase 1 Scope: Restricted to 5 core operations
- III. Zero External Dependencies: Only standard library modules
- IV. Console/CLI Interface: argparse for command parsing
- V. Modular and Testable: Separation of model and CLI layers
- VI. Demo-Ready Quality: Simple, readable, well-documented

## Notes

- No research agents needed - all decisions were clear from specification and constitution
- All Phase 0 unknowns resolved
- Ready to proceed to Phase 1: Data Model, CLI Contracts, and Quickstart
