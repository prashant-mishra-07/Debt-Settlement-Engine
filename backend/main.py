"""
FastAPI Main Application - Debt Settlement Engine
Backend API Layer for Cash Flow Minimization System
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.routes.groups import router as groups_router
from app.api.v1.routes.optimize import router as optimize_router
from database.db_connection import connect_to_mongo, close_mongo_connection

# Initialize FastAPI app
app = FastAPI(
    title="Debt Settlement Engine API",
    description="Optimized Cash Flow Minimization using Graph-Based Algorithms with C++ IPC and MongoDB persistence.",
    version="1.0.0",
    contact={
        "name": "Debt Settlement Engineering Team",
        "email": "support@debt-settlement-engine.local",
        "url": "https://example.com/support"
    }
)

# Global exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(groups_router, prefix="/api/v1", tags=["groups"])
app.include_router(optimize_router, prefix="/api/v1", tags=["optimization"])


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Debt Settlement Engine API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "debt-settlement-engine-api"}

# ==================== Main Entry Point ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
