"""
Main FastAPI application for the Todo backend.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .database.init import initialize_database
from .api.routes import tasks, chat
from .config import get_settings
from .exceptions import add_exception_handlers
from .services.mcp_server import initialize_mcp_server


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    Runs startup and shutdown events.
    """
    logger.info("Starting up the application...")

    # Initialize database on startup
    try:
        await initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Initialize MCP server (conditionally, based on configuration)
    try:
        mcp_enabled = getattr(settings, 'mcp_server_enabled', True)  # Default to enabled
        if mcp_enabled:
            await initialize_mcp_server()
            logger.info("MCP server initialized successfully")
        else:
            logger.info("MCP server is disabled")
    except Exception as e:
        logger.warning(f"Failed to initialize MCP server (non-critical): {e}")
        # Don't raise - MCP server is optional and shouldn't prevent app startup

    yield  # Application runs here

    logger.info("Shutting down the application...")


# Create FastAPI app instance
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.debug
)


# Add exception handlers
add_exception_handlers(app)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """
    Root endpoint for the API.
    """
    return {"message": "Todo Backend API", "version": settings.app_version}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for the API.
    """
    return {"status": "healthy", "app": settings.app_name}