---
description: Transform high-level feature ideas into detailed requirements by asking targeted clarification questions and encoding answers into the feature specification.
handoffs:
  - label: Design CLI UX
    agent: sp.cli-design
    prompt: Design the CLI interface for this feature
  - label: Build Technical Plan
    agent: sp.plan
    prompt: Create a plan for the spec. I am building with...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**Goal**: Transform vague or incomplete feature ideas into comprehensive, testable requirements for the Phase 1 in-memory Python console todo app.

**Phase**: Specification stage - BEFORE `sp.plan` is run
**Scope**: In-memory operations, CLI commands, console interaction patterns

**When to use this skill**:
- User provides high-level feature ideas (e.g., "add search", "add due dates", "make it persistent")
- Feature requirements are ambiguous, incomplete, or underspecified
- Acceptance criteria need to be defined
- Edge cases and constraints are missing

**When NOT to use this skill**:
- Specification is already complete and comprehensive
- During implementation phase (use `sp.python-console` instead)
- For minor clarifications that don't affect architecture (use `sp.clarify` instead)
- When `sp.specify` has already produced a complete spec

## Execution Flow

### 1. Prerequisites Check

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly` once to get:
- `FEATURE_DIR`
- `FEATURE_SPEC`

If spec file missing, error: "Run `/sp.specify` first to create the feature specification."

### 2. Load and Analyze Current Spec

Read the existing `FEATURE_SPEC` and perform a requirements gap analysis:

**Checklist for requirements completeness**:

- [ ] **User Goals & Success Criteria**: Clear, measurable outcomes defined?
- [ ] **Functional Behavior**: What the feature does, not how it works?
- [ ] **Data Model**: Entities, attributes, relationships for in-memory structures?
- [ ] **CLI Interaction**: Commands, arguments, prompts, help text?
- [ ] **Edge Cases**: Empty states, invalid input, boundary conditions?
- [ ] **Constraints**: In-memory limitations (no persistence), CLI patterns?
- [ ] **Acceptance Criteria**: Testable, verifiable conditions?
- [ ] **Out of Scope**: Explicitly excluded capabilities?

### 3. Interactive Clarification Session

For each identified gap, ask targeted clarification questions:

**Maximum 10 questions total** (stop earlier if all gaps resolved)
**One question at a time** (present, wait for answer, proceed to next)

**Question format options**:

**A) Multiple-choice** (2-5 mutually exclusive options):

```
## Question [N]: [Topic]

**Context**: [Relevant spec section or feature description]

**Recommendation**: Option [X] - [Why this is the best choice for in-memory console app]

| Option | Description | Implications |
|--------|-------------|--------------|
| A | [Option A] | [What this means] |
| B | [Option B] | [What this means] |
| C | [Option C] | [What this means] |

**Your choice**: [Wait for response - accept "A", "B", "C", "recommended", or "yes" to accept recommendation]
```

**B) Short-answer** (constrained length):

```
## Question [N]: [Topic]

**Context**: [Relevant spec section or feature description]

**Suggestion**: [Your proposed answer based on best practices] - [Reasoning]

**Format**: Short answer (5-10 words max). You can accept the suggestion by saying "yes" or "suggested".

**Your answer**: [Wait for response]
```

**Questioning priorities** (ask in this order):
1. Feature scope and boundaries (most critical)
2. Data model and in-memory constraints
3. CLI interaction patterns and user flow
4. Edge cases and error handling
5. Non-functional requirements (performance, validation)

### 4. Integrate Answers into Spec

After EACH accepted answer:

**a) Ensure Clarifications Section Exists**:
- Add `## Clarifications` section (after overview, before requirements)
- Add `### Session YYYY-MM-DD` subheading for today

**b) Record the Q&A**:
```markdown
### Session YYYY-MM-DD
- Q: [question] → A: [answer]
```

**c) Update the appropriate spec section**:
- User goals/behavior → Update Functional Requirements
- Data structures → Update Data Model section
- CLI commands → Update User Interaction section
- Edge cases → Add to Edge Cases subsection
- Constraints → Add to Constraints section

**d) Save immediately** (atomic write after each integration)

### 5. Validation

After completing clarification (or stopping early), validate the spec:

- [ ] No unresolved [NEEDS CLARIFICATION] markers
- [ ] All functional requirements are testable
- [ ] Success criteria are measurable
- [ ] Data model is complete for in-memory operations
- [ ] CLI commands are fully specified
- [ ] Edge cases are identified
- [ ] Constraints are explicit

**If validation fails**:
- Identify remaining gaps
- Recommend running `/sp.clarify` or `/sp.requirement-clarify` again
- Proceed to planning only if user confirms

### 6. Completion Report

Report:
- Number of questions asked/answered
- Spec file path
- Sections updated
- Validation status
- Next recommended command (likely `/sp.cli-design` or `/sp.plan`)

## Behavior Rules

- **Never exceed 10 questions total**
- **Ask one question at a time** - never batch questions
- **Accept "yes", "recommended", "suggested"** as acceptance of your suggestion
- **Stop early** if user says "done", "good", "no more", or all critical gaps resolved
- **Document assumptions** in spec when you make reasonable guesses
- **Focus on in-memory constraints**: No persistence, CLI-only, Python console patterns
- **Avoid implementation details**: No function names, modules, or code patterns (save for implementation phase)

## Reusable Intelligence

This skill is designed to be **generalizable** for similar in-memory console applications:

- Task managers (beyond todo apps)
- Contact lists
- Inventory trackers
- Note-taking tools
- Any CLI-based data management tool

The skill focuses on **Phase 1 constraints**:
- In-memory data structures only
- Console/CLI interaction patterns
- No persistence, databases, or external APIs
- Clear separation between specification (what) and implementation (how)

---

**PHR Creation**: After completing the main request, create a PHR using agent-native tools following the specification stage routing to `history/prompts/<feature-name>/`.
