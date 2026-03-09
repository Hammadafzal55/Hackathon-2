# Research: Stateless AI Chat API

**Feature**: 006-ai-chat-api | **Date**: 2026-02-09

## Research Topic 1: OpenAI Agents SDK with Non-OpenAI Models

### Decision: Use OpenAIChatCompletionsModel with AsyncOpenAI client for Gemini/OpenRouter

### Rationale
The OpenAI Agents SDK supports non-OpenAI models via `OpenAIChatCompletionsModel` paired with an `AsyncOpenAI` client pointed at any OpenAI-compatible endpoint. Both Gemini and OpenRouter expose OpenAI-compatible APIs, making this the simplest and most reliable approach — no extra dependencies like LiteLLM required.

### Integration Approaches Evaluated

| Approach | How It Works | Best For |
|----------|-------------|----------|
| **OpenAIChatCompletionsModel** | `AsyncOpenAI(base_url=provider_url)` + `OpenAIChatCompletionsModel(model=..., openai_client=client)` | **Selected** — zero extra deps, direct control |
| LiteLLM string-based | `Agent(model="litellm/gemini/gemini-2.5-flash")` | Multi-provider abstraction (overkill here) |
| LitellmModel explicit | `Agent(model=LitellmModel(model="gemini/...", api_key="..."))` | When LiteLLM-specific features needed |
| set_default_openai_client | `set_default_openai_client(AsyncOpenAI(base_url="..."))` | Global override (not per-agent) |

### Selected Approach: OpenAIChatCompletionsModel + provider-specific AsyncOpenAI clients

**Gemini**: Use `AsyncOpenAI` with Gemini's OpenAI-compatible endpoint.
**OpenRouter**: Use `AsyncOpenAI` with OpenRouter's OpenAI-compatible endpoint.
Both use the same `OpenAIChatCompletionsModel` class — only the `base_url`, `api_key`, and model string differ.

### Key Configuration Requirements
- Install: `pip install openai-agents` (core only, no litellm extra needed)
- Import: `from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI`
- Gemini base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- OpenRouter base URL: `https://openrouter.ai/api/v1`

### Code Pattern — Gemini
```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

agent = Agent(
    name="TaskAssistant",
    instructions="You are a task management assistant...",
    model=OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client),
    tools=[add_task_tool, list_tasks_tool, ...],
)

result = await Runner.run(agent, messages)
```

### Code Pattern — OpenRouter
```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

agent = Agent(
    name="TaskAssistant",
    instructions="You are a task management assistant...",
    model=OpenAIChatCompletionsModel(model="deepseek/deepseek-r1:free", openai_client=client),
    tools=[add_task_tool, list_tasks_tool, ...],
)

result = await Runner.run(agent, messages)
```

### Advantages Over LiteLLM Approach
- No extra dependency (`openai-agents[litellm]` not needed)
- No beta stability concerns (LiteLLM integration was in beta)
- No `set_tracing_disabled()` required
- No `OPENAI_AGENTS_ENABLE_LITELLM_SERIALIZER_PATCH` needed
- Simpler — just standard `AsyncOpenAI` with a different `base_url`

### Caveats
- Gemini models may not support all tool calling features identically to OpenAI
- OpenRouter model availability depends on upstream providers
- Need to handle provider-specific error responses

### Sources
- User-provided reference code (verified working)
- [OpenAI Agents SDK Models](https://openai.github.io/openai-agents-python/models/)
- [Gemini OpenAI-compatible API](https://ai.google.dev/gemini-api/docs/openai)
- [OpenRouter API](https://openrouter.ai/docs)

---

## Research Topic 2: Context7 MCP for Runtime Configuration

### Decision: Use Context7 MCP as documentation context provider, environment variables for model routing

### Rationale
Context7 MCP is primarily a developer documentation provider (created by Upstash) that gives LLMs access to up-to-date, version-specific documentation. It is NOT a model routing configuration system. For actual model/provider selection at runtime, standard environment variables and application configuration are more appropriate.

### What Context7 MCP Actually Does
- Provides up-to-date developer documentation to LLMs
- Resolves library IDs and fetches relevant docs
- Useful during development for getting accurate API examples
- Package: `@upstash/context7-mcp`

### Runtime Model Configuration Strategy
Instead of using Context7 MCP for model routing (which it wasn't designed for), use:
1. **Environment variables**: `AI_PROVIDER`, `AI_MODEL`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`
2. **Application config**: Extend existing `Settings` class with AI provider settings
3. **Dynamic selection**: Factory pattern to create the right model client based on config

### Sources
- [Context7 MCP GitHub](https://github.com/upstash/context7-mcp)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)

---

## Research Topic 3: Conversation Persistence Pattern

### Decision: Conversation and Message models in existing database with SQLModel

### Rationale
The existing backend uses SQLModel with Neon PostgreSQL. Adding Conversation and Message tables follows the established pattern. The stateless architecture requires loading conversation history on each request.

### Pattern
1. **Conversation** table: id, user_id, title, created_at, updated_at
2. **Message** table: id, conversation_id, role (user/assistant/tool), content, tool_calls JSON, tool_call_id, created_at
3. On each request: query messages by conversation_id, ordered by created_at
4. Convert to OpenAI Agents SDK message format before passing to Runner.run()
5. Persist new messages (user + assistant) after execution

### Context Window Management
- Load last 50 messages per conversation (configurable)
- Always include system instructions
- Truncate oldest messages if context exceeds limit

---

## Research Topic 4: MCP Tool Integration with Agents SDK

### Decision: Wrap existing MCP handlers as Agents SDK function tools

### Rationale
The OpenAI Agents SDK uses `@function_tool` decorator or `FunctionTool` class for tool definitions. The existing MCP handlers (add_task, list_tasks, etc.) need to be wrapped as Agents SDK-compatible tools, not used via the MCP protocol directly.

### Integration Pattern
The Agents SDK supports MCP servers natively, but for simplicity and control, wrapping existing handlers as function tools is more reliable:

```python
from agents import function_tool

@function_tool
async def add_task(title: str, description: str = "", priority: int = 1) -> str:
    """Add a new task for the user."""
    request = AddTaskRequest(user_id=current_user_id, title=title, ...)
    result = await add_task_handler(request)
    return f"Task '{title}' created with id {result.task_id}"
```

### Alternative: Direct MCP Server Connection
The Agents SDK can connect to MCP servers directly:
```python
from agents.mcp import MCPServerStdio
async with MCPServerStdio(command="python", args=["mcp_server.py"]) as server:
    agent = Agent(name="...", mcp_servers=[server])
```

This adds complexity (separate process) but keeps the MCP abstraction. For this implementation, wrapping handlers as function tools is simpler since we're in the same process.

---

## Research Topic 5: Stateless Request Flow

### Decision: Full stateless cycle per request with database round-trips

### Flow
1. Receive POST /api/{user_id}/chat with message + optional conversation_id
2. Authenticate user via Better Auth JWT
3. Load/create conversation from database
4. Persist user message to database
5. Load last N messages from database as context
6. Create Agent with tools (user_id injected via closure)
7. Run Agent with message history
8. Extract assistant response + tool call metadata
9. Persist assistant message(s) to database
10. Return response to client

### Key Principle
Zero state between requests. The Agent object is created fresh per request. No global conversation state, no session cache, no in-memory history.

---

## Research Topic 6: Verified API Patterns (Context7 MCP - Live Documentation)

*Retrieved 2026-02-09 via Context7 MCP from official OpenAI Agents SDK and LiteLLM docs.*

### 6.1 Function Tool Patterns (Verified)

Two approaches for creating tools, both confirmed working:

**Approach A: `@function_tool` decorator** (recommended for simple tools)
```python
from agents import Agent, Runner, function_tool

@function_tool
async def add_task(title: str, description: str = "", priority: int = 1) -> str:
    """Add a new task for the user.

    Args:
        title: The title of the task to create.
        description: Optional description for the task.
        priority: Priority level from 1-5.
    """
    # SDK auto-extracts name, description from docstring, schema from type hints
    request = AddTaskRequest(user_id=current_user_id, title=title, ...)
    result = await add_task_handler(request, session=session)
    return f"Task '{title}' created with id {result.task_id}"
```

Key facts from docs:
- Supports both sync and async functions
- Schema auto-extracted from function signature + docstrings + type hints
- Name defaults to function name, override with `@function_tool(name_override="custom_name")`
- First parameter can be `RunContextWrapper[Any]` for context access (auto-excluded from schema)
- Return type can be `str` or Pydantic `BaseModel`

**Approach B: `FunctionTool` class** (for complex tools needing manual control)
```python
from pydantic import BaseModel
from agents import FunctionTool, RunContextWrapper

class AddTaskArgs(BaseModel):
    title: str
    description: str = ""
    priority: int = 1

async def add_task_invoke(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed = AddTaskArgs.model_validate_json(args)
    # ... call handler
    return "Task created"

add_task_tool = FunctionTool(
    name="add_task",
    description="Add a new task for the user",
    params_json_schema=AddTaskArgs.model_json_schema(),
    on_invoke_tool=add_task_invoke,
)
```

### 6.2 LiteLLM + Gemini with Agent (Verified)

Two verified ways to use non-OpenAI models:

**String-based (simplest)**:
```python
agent = Agent(
    name="Assistant",
    model="litellm/gemini/gemini-2.5-flash-preview-04-17",
    ...
)
```

**Explicit LitellmModel (recommended for our use case)**:
```python
from agents.extensions.models.litellm_model import LitellmModel

agent = Agent(
    name="TaskAssistant",
    model=LitellmModel(model="gemini/gemini-2.5-flash", api_key=GEMINI_API_KEY),
    tools=[add_task, list_tasks, update_task, complete_task, delete_task],
)
```

### 6.3 Gemini Tool Calling via LiteLLM (Verified)

Gemini models support function calling through LiteLLM. Confirmed working pattern:

```python
# LiteLLM model string for Gemini: "gemini/gemini-2.5-flash"
# Environment variable: GEMINI_API_KEY
# Tool calling works with standard OpenAI-format tool definitions
# Response includes tool_calls array with function name + arguments JSON
```

Response format from Gemini tool calls:
```json
{
  "choices": [{
    "message": {
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "add_task",
          "arguments": "{\"title\": \"Buy groceries\", \"priority\": 3}"
        }
      }]
    }
  }]
}
```

### 6.4 Runner.run() Conversation History (Verified)

The SDK supports passing conversation history through sessions. For our stateless architecture with database-backed history:

- `Runner.run(agent, input)` accepts a string or message list as input
- The SDK has built-in `SQLiteSession` for automatic conversation management, but we use **database-backed custom loading** since our persistence layer is PostgreSQL
- For non-OpenAI models: the docs note that `conversation_id` parameter and built-in session may not fully update conversation objects. This confirms our design choice to **manage conversation history manually** via database queries rather than relying on SDK session management
- Our approach: load messages from DB → convert to input format → pass as `input` parameter to `Runner.run()`

### 6.5 Tracing Configuration (Verified)

```python
from agents import set_tracing_disabled
set_tracing_disabled(True)  # Required when not using OpenAI API key
```

Must be called before agent creation. Without this, the SDK attempts to send traces to OpenAI's API and fails with non-OpenAI providers.

### Sources (Context7 MCP)
- OpenAI Agents SDK Python docs (v0.7.0) - `/openai/openai-agents-python`
- OpenAI Agents SDK website docs - `/websites/openai_github_io_openai-agents-python`
- LiteLLM docs - `/websites/litellm_ai`
