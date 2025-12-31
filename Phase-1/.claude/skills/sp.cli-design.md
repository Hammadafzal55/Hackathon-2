---
description: Design the command-line interface workflow for the todo app, including command structure, arguments, prompts, help text, and input validation rules.
handoffs:
  - label: Implement Python Code
    agent: sp.python-console
    prompt: Implement the feature based on the CLI design
  - label: Build Technical Plan
    agent: sp.plan
    prompt: Create a plan that includes this CLI UX design
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**Goal**: Design comprehensive, consistent CLI interaction patterns for the Phase 1 in-memory Python console todo app.

**Phase**: After specification, BEFORE implementation (`sp.implement` or `sp.python-console`)
**Scope**: CLI commands, arguments, prompts, help text, validation rules

**When to use this skill**:
- Feature requires CLI commands or user interaction
- Specification is complete but CLI UX patterns need definition
- Designing new command structures
- Defining input validation and user prompts
- Creating help text and usage patterns

**When NOT to use this skill**:
- Feature has no CLI component (e.g., pure internal functions)
- CLI UX is already fully designed
- For GUI or web applications (this is console-only)
- During implementation phase (design first, then implement)

## Execution Flow

### 1. Prerequisites Check

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly` once to get:
- `FEATURE_DIR`
- `FEATURE_SPEC`

If spec file missing or incomplete, error: "Ensure spec is complete via `/sp.requirement-clarify` before CLI design."

### 2. Load and Analyze Specification

Read `FEATURE_SPEC` and extract:
- Functional requirements
- User interaction scenarios
- Data model (entities, attributes)
- User stories and workflows
- Edge cases and constraints

### 3. Review Existing CLI Patterns (if any)

Check for existing CLI design artifacts:
- `specs/<feature>/cli-ux-design.md`
- Previous CLI commands in the codebase
- Constitution for UX consistency principles

### 4. Design CLI Structure

Based on the spec requirements, design the CLI interface:

**A) Command Taxonomy**:

Define the command structure for the feature:

```
<command> [--flag] [--option <value>] [argument]
```

For the todo app context:
- `todo add <task-description>` - Add a task
- `todo list [--filter <status>]` - List tasks
- `todo complete <task-id>` - Mark task complete
- `todo delete <task-id>` - Delete a task
- `todo help` - Show help

**B) Command Specifications**:

For each command required by the feature, document:

```markdown
### Command: `command-name`

**Purpose**: [What this command accomplishes]

**Syntax**:
```
command-name [--flag] [--option <value>] [argument]
```

**Arguments**:
- `arg-name` (required/optional): [Description and valid values]

**Options/Flags**:
- `-f, --flag` (required/optional): [Description]
- `-o, --option <value>` (required/optional): [Description, valid values]

**Input Validation**:
- [Type checking, range validation, format validation]

**Success Output**:
- [What the user sees on success]

**Error Output**:
- [Specific error messages for validation failures]
- [How to recover from errors]

**Examples**:
```
$ command-name example-arg
[Success output]

$ command-name --option value
[Success output]

$ command-name invalid-input
Error: [Specific error message]
```
```

**C) Interactive Mode Design**:

If the spec suggests interactive workflows:

```markdown
### Interactive Mode: `<workflow-name>`

**Purpose**: [What this workflow accomplishes]

**Flow**:
1. [Prompt 1 with input validation]
2. [Prompt 2 with input validation]
3. [Confirmation step]
4. [Execute action]

**Prompts**:
- Prompt 1: "Enter [input]: [help text]"
  - Validation: [rules]
  - Error message: "Invalid input. [reason]. Try again."

**Example Session**:
```
$ command-name --interactive
Enter task description: [user types]
[Validation feedback or success]
Enter due date (YYYY-MM-DD) or press Enter to skip: [user types]
[Confirmation or proceed]
Task added successfully!
```
```

**D) Help Text Design**:

```markdown
### Help System

**General Help** (`--help` or `help`):
```
Usage: todo <command> [options]

Commands:
  add <task>       Add a new task
  list [--filter]  List all tasks
  complete <id>    Mark a task as complete
  delete <id>      Delete a task
  help             Show this help message

Options:
  --filter <status> Filter by status: todo, done, all (default: all)
  -h, --help       Show help message

Examples:
  todo add "Buy groceries"
  todo list --filter done
  todo complete 1
```

**Command-specific Help** (`<command> --help`):
```
Usage: todo add <task> [options]

Description: Add a new task to the in-memory list

Arguments:
  task              Task description (required)

Options:
  -p, --priority <level>  Priority: low, medium, high (default: medium)
  -h, --help              Show this help message

Examples:
  todo add "Buy groceries"
  todo add "Pay bills" --priority high
```
```

**E) Consistency Guidelines**:

```markdown
### CLI Consistency Rules

**Command Naming**:
- Use lowercase, hyphen-separated commands
- Use present tense verbs: add, list, delete, complete
- Be concise but descriptive

**Flag Naming**:
- Short flags: single dash, single letter (e.g., `-h`, `-v`)
- Long flags: double dash, hyphen-separated words (e.g., `--help`, `--verbose`)
- Common patterns:
  - `-h, --help` - Show help
  - `-v, --verbose` - Verbose output
  - `-q, --quiet` - Quiet mode

**Error Messages**:
- Format: `Error: <specific message>`
- Be specific: what went wrong, why, how to fix
- Avoid technical jargon
- Suggest valid inputs or examples

**Success Messages**:
- Format: `<action> <noun> <outcome>`
- Examples: "Task added successfully", "Task 1 completed"
- Be concise and affirmative

**Validation Feedback**:
- Immediate feedback on invalid input
- Show what was entered and why it's invalid
- Provide example of valid input
```

### 5. Input Validation Rules

Define comprehensive validation for each input type:

```markdown
### Input Validation

**Text Input**:
- Non-empty strings
- Trim whitespace
- Max length: [characters]
- Strip special characters: [if applicable]

**Numeric Input**:
- Integer validation
- Range validation: [min] to [max]
- Must be positive: [yes/no]

**Date Input**:
- Format: YYYY-MM-DD
- Future dates only: [yes/no]
- Past dates only: [yes/no]

**Enum Input**:
- Valid values: [list]
- Case-insensitive matching: [yes/no]
- Allow abbreviations: [if applicable]

**ID References**:
- Must be valid task ID: [1-N]
- Task must exist: [yes/no]
- Task must be in correct state: [if applicable]
```

### 6. Output Design

```markdown
### Output Formats

**Success Output**:
- Single-line confirmation for simple actions
- Multi-line summary for complex actions
- Include relevant details: ID, status, summary

**Error Output**:
- Always start with "Error: "
- Specific error message (not generic "Invalid input")
- Recovery suggestion: how to fix the issue
- Example of valid input if applicable

**List Output**:
- Tabular or column-based format
- Headers for each column
- Sort order (by default)
- Empty state message: "No tasks found."

**Verbose Output** (optional):
- Detailed execution information
- Timestamps
- Resource usage
- Enable with `-v` or `--verbose` flag
```

### 7. Create CLI UX Design Document

Write the complete CLI design to `specs/<feature>/cli-ux-design.md`:

**Document structure**:
```markdown
# CLI UX Design: [Feature Name]

**Feature**: [Link to spec.md]
**Created**: [DATE]
**Phase**: Phase 1 - In-Memory Python Console App

## Overview
[Brief summary of CLI interaction patterns for this feature]

## Commands
[Command specifications for each required command]

## Interactive Workflows
[Interactive mode designs, if applicable]

## Help System
[General help and command-specific help text]

## Input Validation
[Validation rules for all input types]

## Output Design
[Success, error, and list output formats]

## Consistency Guidelines
[How this CLI design follows project CLI standards]

## Examples
[Example usage sessions for the feature]
```

### 8. Validation

Validate the CLI design:

- [ ] All commands from spec are covered
- [ ] Command syntax is consistent
- [ ] Input validation is comprehensive
- [ ] Error messages are specific and helpful
- [ ] Help text is clear and complete
- [ ] Examples demonstrate all key workflows
- [ ] Follows project CLI consistency guidelines

### 9. Completion Report

Report:
- Number of commands designed
- CLI design file path
- Validation status
- Next recommended command (likely `/sp.plan` or `/sp.python-console`)

## Behavior Rules

- **Design BEFORE implementation** - never write code first
- **Follow existing patterns** - check for prior CLI designs in the codebase
- **Be specific** - concrete examples for every command and validation rule
- **User-focused** - think like a user, not a developer
- **Console constraints** - in-memory only, no persistence, CLI patterns only
- **Avoid implementation details** - no function names, modules, or code structure

## Reusable Intelligence

This skill is designed to be **generalizable** for CLI applications:

- Consistency in command naming, flags, and help text
- Standard validation patterns for common input types
- Reusable error message formats
- Standardized output formats (success, error, list)
- Interactive workflow patterns

The CLI design can be reused as a **template** for similar console applications:
- Task managers
- Contact lists
- Inventory trackers
- Any CLI-based data management tool

---

**PHR Creation**: After completing the main request, create a PHR using agent-native tools following the specification stage routing to `history/prompts/<feature-name>/`.
