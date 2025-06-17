# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="LifeSync AI Backend",
    description="AI-powered backend for LifeSync daily routine organizer",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to LifeSync AI Backend",
        "version": "1.0.0",
        "endpoints": {
            "parse_task": "/api/v1/parse-task",
            "suggest_schedule": "/api/v1/suggest-schedule",
            "process_document": "/api/v1/process-document",
            "wellness_suggestions": "/api/v1/wellness-suggestions",
            "analyze_behavior": "/api/v1/analyze-behavior",
            "health": "/api/v1/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )