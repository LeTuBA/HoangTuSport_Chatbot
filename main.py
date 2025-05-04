import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv
from app.core.config import settings

# Không cần load_dotenv() ở đây nữa vì đã được load trong config.py
# load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Vô hiệu hóa log của SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

# Application lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: initialize resources
    logger.info("Application starting up...")
    
    # Khởi tạo và chuẩn bị database SQLModel
    from app.db.database import create_db_and_tables
    create_db_and_tables()
    logger.info("Database initialized and tables created")
    
    # Initialize vector database
    # This is a placeholder - actual implementation would depend on your setup
    logger.info("Initialized vector database")
    
    yield
    
    # Shutdown event: cleanup resources
    logger.info("Application shutting down...")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-agent chatbot service with RAG for cosmetic shop",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
from app.api.endpoints import router
app.include_router(router, prefix="/api")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status code: {response.status_code}")
    return response

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Cosmetic Shop Chatbot API",
        "docs": "/docs"
    }

# Run application if executed directly
if __name__ == "__main__":
    port = settings.PORT
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    ) 