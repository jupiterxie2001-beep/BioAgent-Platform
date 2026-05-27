#!/usr/bin/env python3
"""Quick test to verify the backend setup is working."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

async def test_database_connection():
    """Test database connection and table creation."""
    try:
        from app.core.database import engine, init_db
        
        print("Testing database connection...")
        await init_db()
        print("✓ Database tables created successfully")
        
        # Test connection
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("✓ Database connection successful")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

async def test_imports():
    """Test that all required modules can be imported."""
    modules = [
        "app.main",
        "app.core.config",
        "app.core.database",
        "app.core.security",
        "app.database.models",
        "app.schemas.user",
        "app.api.auth",
        "app.api.health",
        "app.api",
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ Imported {module}")
        except ImportError as e:
            print(f"✗ Failed to import {module}: {e}")
            return False
    return True

async def main():
    print("Testing BioAgent Platform backend setup...")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing module imports:")
    if not await test_imports():
        print("\n✗ Module import test failed")
        return False
    
    # Test database
    print("\n2. Testing database:")
    if not await test_database_connection():
        print("\n✗ Database test failed")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Backend is ready to run.")
    
    # Show API endpoints
    print("\nAvailable API endpoints:")
    print("  POST   /api/v1/auth/register")
    print("  POST   /api/v1/auth/login")
    print("  GET    /api/v1/auth/me (requires JWT)")
    print("  GET    /api/v1/health")
    print("\nTo start the server:")
    print("  cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)