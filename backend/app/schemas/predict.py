"""Pydantic schemas for price prediction."""

from pydantic import BaseModel, Field


class PricePredictionInput(BaseModel):
    """Input for price prediction based on sustainability features."""

    score: float = Field(..., ge=0, le=100, description="Sustainability score")
    brand: str = Field(..., description="Brand name")
    category: str = Field(..., description="Product category")
    subcategory: str = Field(..., description="Product subcategory")


class PricePredictionResponse(BaseModel):
    """Response from price prediction."""

    predicted_price: float = Field(..., description="Predicted price in euros")
    confidence: str = Field(..., description="Confidence level (low/medium/high)")
    model_type: str = Field(..., description="Model used for prediction")
