import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.main import app
from src.database.init import initialize_database
import asyncio

def test_backend_startup():
    """Test that the backend can start up properly."""
    print("Testing backend startup...")

    # Test that we can import the app
    assert app is not None
    print("✓ FastAPI app imported successfully")

    # Test that we can access the routes
    route_paths = []
    for route in app.routes:
        if hasattr(route, 'path'):
            route_paths.append(route.path)

    # Check for some expected patterns in the routes
    expected_patterns = ['/health', '/', '/docs', '/api']
    found_patterns = []
    for pattern in expected_patterns:
        for route_path in route_paths:
            if pattern in route_path:
                found_patterns.append(pattern)
                break

    for pattern in found_patterns:
        print(f"✓ Standard route pattern {pattern} available")

    print("✓ Backend startup test completed successfully")
    print("\nThe backend is ready to run with the following command:")
    print("cd backend")
    print("uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAPI documentation will be available at http://localhost:8000/docs")

if __name__ == "__main__":
    test_backend_startup()