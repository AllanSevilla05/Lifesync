#!/usr/bin/env python3
"""
Simple startup script for LifeSync backend server
"""
import sys
import os
import subprocess

def main():
    """Start the LifeSync backend server with proper configuration"""
    
    # Change to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    print("🚀 Starting LifeSync Backend Server...")
    print(f"📁 Working directory: {backend_dir}")
    
    # Create database tables if they don't exist
    try:
        print("📊 Creating database tables...")
        
        # Use uv to run the database setup
        result = subprocess.run([
            "uv", "run", "python", "-c", 
            "from app.core.database import engine; from app.models import models, goal_models, habit_models, collaboration_models; models.Base.metadata.create_all(bind=engine); print('Database tables created!')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database tables created successfully!")
        else:
            print(f"⚠️  Database setup warning: {result.stderr}")
            print("🔄 Server will continue, but database might not work properly")
        
    except Exception as e:
        print(f"⚠️  Database setup warning: {e}")
        print("🔄 Server will continue, but database might not work properly")
    
    # Start the server
    try:
        print("🌐 Starting Uvicorn server...")
        print("📍 Server will be available at: http://127.0.0.1:8000")
        print("📋 API docs will be available at: http://127.0.0.1:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the server using uv
        subprocess.run([
            "uv", "run", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())