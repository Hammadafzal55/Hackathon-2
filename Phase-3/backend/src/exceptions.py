"""
Custom exception classes and handlers for the Todo backend application.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any


class TodoException(Exception):
    """
    Base exception class for Todo application.
    """

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class TodoNotFoundException(TodoException):
    """
    Exception raised when a todo item is not found.
    """

    def __init__(self, todo_id: int):
        super().__init__(
            message=f"Todo with id {todo_id} not found",
            status_code=404
        )


class UserNotFoundException(TodoException):
    """
    Exception raised when a user is not found.
    """

    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with id {user_id} not found",
            status_code=404
        )


class UnauthorizedException(TodoException):
    """
    Exception raised when a user is not authorized to perform an action.
    """

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=401
        )


class ValidationException(TodoException):
    """
    Exception raised when input validation fails.
    """

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=422
        )


class AIProviderError(TodoException):
    """
    Exception raised when the AI provider (Gemini) is unavailable or returns an error.
    """

    def __init__(self, message: str = "AI provider is temporarily unavailable"):
        super().__init__(
            message=message,
            status_code=503
        )


class AIConfigurationError(TodoException):
    """
    Exception raised when AI configuration is invalid (e.g., missing API key).
    """

    def __init__(self, message: str = "AI service is not properly configured"):
        super().__init__(
            message=message,
            status_code=500
        )


class ConversationNotFoundError(TodoException):
    """
    Exception raised when a conversation is not found or doesn't belong to the user.
    """

    def __init__(self, conversation_id: str = ""):
        msg = f"Conversation not found" if not conversation_id else f"Conversation {conversation_id} not found"
        super().__init__(
            message=msg,
            status_code=404
        )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance
    """

    @app.exception_handler(TodoNotFoundException)
    async def handle_todo_not_found_exception(request: Request, exc: TodoNotFoundException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": "TODO_NOT_FOUND"
            }
        )

    @app.exception_handler(UserNotFoundException)
    async def handle_user_not_found_exception(request: Request, exc: UserNotFoundException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": "USER_NOT_FOUND"
            }
        )

    @app.exception_handler(UnauthorizedException)
    async def handle_unauthorized_exception(request: Request, exc: UnauthorizedException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": "UNAUTHORIZED"
            }
        )

    @app.exception_handler(ValidationException)
    async def handle_validation_exception(request: Request, exc: ValidationException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": "VALIDATION_ERROR"
            }
        )

    @app.exception_handler(AIProviderError)
    async def handle_ai_provider_error(request: Request, exc: AIProviderError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": "AI_PROVIDER_ERROR"
            }
        )

    @app.exception_handler(AIConfigurationError)
    async def handle_ai_configuration_error(request: Request, exc: AIConfigurationError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": "AI_CONFIGURATION_ERROR"
            }
        )

    @app.exception_handler(ConversationNotFoundError)
    async def handle_conversation_not_found(request: Request, exc: ConversationNotFoundError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": "CONVERSATION_NOT_FOUND"
            }
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": "HTTP_ERROR"
            }
        )

    @app.exception_handler(Exception)
    async def handle_general_exception(request: Request, exc: Exception):
        # Log the exception details in production
        import logging
        logging.error(f"Unhandled exception: {str(exc)}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR"
            }
        )


def add_exception_handlers(app: FastAPI) -> None:
    """
    Convenience function to add all exception handlers to the app.

    Args:
        app (FastAPI): The FastAPI application instance
    """
    register_exception_handlers(app)