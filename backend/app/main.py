"""
FastAPI application for Sustainability Scoring API.
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the src directory to the path so we can import sustainability_scoring
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.routers import scoring, products, predict, reference
from app.services.model_service import load_price_model
from app.services.data_service import load_reference_data, load_sample_products


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load resources on startup, cleanup on shutdown."""
    # Startup: Load reference data and ML model
    app.state.reference_data = load_reference_data()
    app.state.sample_products = load_sample_products()
    app.state.price_model = load_price_model()
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="Sustainability Scoring API",
    description="API for calculating sustainability scores for fashion products",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
# Allow configurable origins via environment variable (comma-separated)
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scoring.router, prefix="/api", tags=["Scoring"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(predict.router, prefix="/api", tags=["Price Prediction"])
app.include_router(reference.router, prefix="/api/reference", tags=["Reference Data"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": hasattr(app.state, "price_model") and app.state.price_model is not None,
        "reference_data_loaded": hasattr(app.state, "reference_data") and app.state.reference_data is not None,
    }
