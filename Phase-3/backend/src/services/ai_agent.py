"""
AI Agent Service for the Chat API.
Creates a stateless agent per request using the OpenAI Agents SDK
with Gemini via OpenAI-compatible API.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.exceptions import AIProviderError, AIConfigurationError
from src.mcp_tools.handlers import (
    add_task_handler,
    list_tasks_handler,
    update_task_handler,
    complete_task_handler,
    delete_task_handler,
)
from src.mcp_tools.schemas import (
    AddTaskRequest,
    ListTasksRequest,
    UpdateTaskRequest,
    CompleteTaskRequest,
    DeleteTaskRequest,
)

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo tasks through natural language conversation.

**Capabilities:**
- Add new tasks with title, description, priority (1-5), and due date
- List all tasks or filter by status (pending, in_progress, completed, cancelled)
- Update task details (title, description, priority, status, due date)
- Mark tasks as complete or incomplete
- Delete tasks

**Behavior:**
- Be conversational and friendly
- When the user asks to manage tasks, use the available tools
- After performing an action, confirm what was done
- If the user's intent is ambiguous, ask for clarification
- When listing tasks, format them in a readable way
- Priority scale: 1 (lowest) to 5 (highest)

**Constraints:**
- You can only manage tasks for the current authenticated user
- Stay within the scope of task management
- Do not make up task IDs; use the tools to find tasks first
"""


def create_task_tools(user_id: str, session: AsyncSession) -> list:
    """
    Create function tools that wrap existing MCP handlers.
    The user_id is injected via closure for security.
    """

    @function_tool
    async def add_task(title: str, description: str = "", priority: int = 1) -> str:
        """Add a new task for the user.

        Args:
            title: The title of the task to create.
            description: Optional description for the task.
            priority: Priority level from 1 (lowest) to 5 (highest). Default is 1.
        """
        request = AddTaskRequest(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
        )
        result = await add_task_handler(request, session=session)
        return f"Task '{title}' created successfully with id {result.task_id}"

    @function_tool
    async def list_tasks(status_filter: str = "") -> str:
        """List all tasks for the user, optionally filtered by status.

        Args:
            status_filter: Optional filter by status. Values: pending, in_progress, completed, cancelled. Leave empty for all tasks.
        """
        request = ListTasksRequest(
            user_id=user_id,
            status_filter=status_filter if status_filter else None,
        )
        result = await list_tasks_handler(request, session=session)
        if not result.tasks:
            return "No tasks found."
        lines = []
        for t in result.tasks:
            line = f"- [{t['status']}] {t['title']} (priority: {t['priority']}, id: {t['id']})"
            if t.get("description"):
                line += f"\n  Description: {t['description']}"
            lines.append(line)
        return f"Found {result.total_count} task(s):\n" + "\n".join(lines)

    @function_tool
    async def update_task(
        task_id: str,
        title: str = "",
        description: str = "",
        priority: int = 0,
        status: str = "",
    ) -> str:
        """Update an existing task's details.

        Args:
            task_id: The UUID of the task to update.
            title: New title for the task. Leave empty to keep current.
            description: New description. Leave empty to keep current.
            priority: New priority (1-5). Use 0 to keep current.
            status: New status (pending, in_progress, completed, cancelled). Leave empty to keep current.
        """
        request = UpdateTaskRequest(
            user_id=user_id,
            task_id=UUID(task_id),
            title=title if title else None,
            description=description if description else None,
            priority=priority if priority > 0 else None,
            status=status if status else None,
        )
        result = await update_task_handler(request, session=session)
        return f"Task '{result.task['title']}' updated successfully"

    @function_tool
    async def complete_task(task_id: str, complete: bool = True) -> str:
        """Mark a task as complete or incomplete.

        Args:
            task_id: The UUID of the task to complete/uncomplete.
            complete: True to mark complete, False to mark incomplete. Default is True.
        """
        request = CompleteTaskRequest(
            user_id=user_id,
            task_id=UUID(task_id),
            complete=complete,
        )
        result = await complete_task_handler(request, session=session)
        action = "completed" if complete else "marked as incomplete"
        return f"Task '{result.task['title']}' {action}"

    @function_tool
    async def delete_task(task_id: str) -> str:
        """Delete a task permanently.

        Args:
            task_id: The UUID of the task to delete.
        """
        request = DeleteTaskRequest(
            user_id=user_id,
            task_id=UUID(task_id),
        )
        result = await delete_task_handler(request, session=session)
        return f"Task deleted successfully (id: {result.task_id})"

    return [add_task, list_tasks, update_task, complete_task, delete_task]


def create_agent(user_id: str, session: AsyncSession) -> Agent:
    """
    Create a fresh AI agent for a single request.
    Agent is stateless — created and discarded per request.
    """
    settings = get_settings()

    if not settings.gemini_api_key:
        raise AIConfigurationError("GEMINI_API_KEY is not configured")

    tools = create_task_tools(user_id, session)

    client = AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    return Agent(
        name="TaskAssistant",
        instructions=SYSTEM_PROMPT,
        model=OpenAIChatCompletionsModel(
            model=settings.ai_model,
            openai_client=client,
        ),
        tools=tools,
    )


def convert_to_sdk_format(messages: list) -> list:
    """
    Convert database Message objects to the input format expected by Runner.run().
    Returns a list of dicts with role/content keys.
    """
    sdk_messages = []
    for msg in messages:
        entry: Dict[str, Any] = {"role": msg.role, "content": msg.content or ""}
        sdk_messages.append(entry)
    return sdk_messages


async def run_chat_agent(
    user_id: str,
    messages: list,
    session: AsyncSession,
) -> Dict[str, Any]:
    """
    Run the AI agent with conversation history and return the response.

    Returns:
        Dict with 'response' (str) and 'tool_calls' (list of ToolCallInfo dicts)
    """
    agent = create_agent(user_id, session)

    try:
        result = await Runner.run(agent, messages)

        # Extract tool call metadata from the run result
        tool_calls_info = []
        if hasattr(result, "raw_responses"):
            for raw in result.raw_responses:
                if hasattr(raw, "output") and raw.output:
                    for item in raw.output:
                        if hasattr(item, "type") and item.type == "function_call":
                            tool_calls_info.append({
                                "tool_name": item.name if hasattr(item, "name") else "unknown",
                                "arguments": json.loads(item.arguments) if hasattr(item, "arguments") else {},
                                "result": "",
                                "success": True,
                            })

        # Try to get tool call info from new_items if raw_responses didn't have it
        if not tool_calls_info and hasattr(result, "new_items"):
            for item in result.new_items:
                item_type = type(item).__name__
                if "ToolCall" in item_type or "FunctionCall" in item_type:
                    tool_calls_info.append({
                        "tool_name": getattr(item, "name", getattr(item, "tool_name", "unknown")),
                        "arguments": getattr(item, "arguments", {}),
                        "result": getattr(item, "output", ""),
                        "success": True,
                    })

        return {
            "response": result.final_output or "",
            "tool_calls": tool_calls_info,
        }

    except Exception as e:
        logger.error(f"AI agent error: {e}", exc_info=True)
        error_msg = str(e).lower()
        if "api" in error_msg or "connection" in error_msg or "timeout" in error_msg or "rate" in error_msg:
            raise AIProviderError(f"AI provider error: {e}")
        raise
