"""
MCP Server Module
This module implements the MCP (Model Context Protocol) server for task management operations.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from contextlib import asynccontextmanager

# Import tool handlers
from src.mcp_tools.handlers import (
    add_task_handler,
    list_tasks_handler,
    update_task_handler,
    complete_task_handler,
    delete_task_handler
)

logger = logging.getLogger(__name__)


class MCPTaskServer:
    """
    MCP Server for task management operations.
    Provides AI agents with safe access to task operations through standardized tools.
    """

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.is_initialized: bool = False

    async def initialize(self):
        """Initialize the MCP server and register all task tools."""
        if self.is_initialized:
            logger.warning("MCP server already initialized")
            return

        try:
            logger.info("Initializing MCP Task Server...")

            # Register all task tools
            self.register_tool("add_task", add_task_handler)
            self.register_tool("list_tasks", list_tasks_handler)
            self.register_tool("update_task", update_task_handler)
            self.register_tool("complete_task", complete_task_handler)
            self.register_tool("delete_task", delete_task_handler)

            self.is_initialized = True
            logger.info(f"MCP server initialized successfully with {len(self.tools)} tools")

        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}", exc_info=True)
            raise

    async def start(self):
        """Start the MCP server."""
        if not self.is_initialized:
            await self.initialize()

        logger.info("MCP server is running and ready to accept tool calls")

    async def stop(self):
        """Stop the MCP server and cleanup resources."""
        logger.info("Stopping MCP server...")
        self.tools.clear()
        self.is_initialized = False
        logger.info("MCP server stopped successfully")

    def register_tool(self, name: str, tool_func: Callable):
        """
        Register a tool with the MCP server.

        Args:
            name: The name of the tool
            tool_func: The handler function for the tool
        """
        if name in self.tools:
            logger.warning(f"Tool '{name}' is already registered, overwriting...")

        self.tools[name] = tool_func
        logger.debug(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Get a registered tool by name.

        Args:
            name: The name of the tool

        Returns:
            The tool handler function if found, None otherwise
        """
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        """
        Get a list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    async def call_tool(self, tool_name: str, request: Any) -> Any:
        """
        Call a registered tool with the provided request.

        Args:
            tool_name: The name of the tool to call
            request: The request object for the tool

        Returns:
            The response from the tool

        Raises:
            ValueError: If the tool is not found
        """
        tool_func = self.get_tool(tool_name)
        if not tool_func:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {', '.join(self.list_tools())}")

        logger.info(f"Calling tool: {tool_name}")
        try:
            result = await tool_func(request)
            logger.info(f"Tool '{tool_name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}", exc_info=True)
            raise


# Global instance
mcp_server = MCPTaskServer()


async def initialize_mcp_server():
    """Initialize the MCP server during application startup."""
    await mcp_server.initialize()
    await mcp_server.start()


def get_mcp_server():
    """Get the global MCP server instance."""
    return mcp_server


def register_all_tools():
    """
    Register all task tools with the MCP server.
    This function can be called to re-register tools if needed.
    """
    mcp_server.register_tool("add_task", add_task_handler)
    mcp_server.register_tool("list_tasks", list_tasks_handler)
    mcp_server.register_tool("update_task", update_task_handler)
    mcp_server.register_tool("complete_task", complete_task_handler)
    mcp_server.register_tool("delete_task", delete_task_handler)
    logger.info("All tools registered successfully")