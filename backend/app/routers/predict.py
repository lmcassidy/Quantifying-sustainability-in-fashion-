"""API routes for price prediction."""

from fastapi import APIRouter, HTTPException, Request

from app.schemas.predict import PricePredictionInput, PricePredictionResponse
from app.services.model_service import predict_price

router = APIRouter()


@router.post("/predict-price", response_model=PricePredictionResponse)
async def predict_product_price(
    prediction_input: PricePredictionInput,
    request: Request,
) -> PricePredictionResponse:
    """
    Predict price for a product based on sustainability features.

    Uses a pre-trained machine learning model to estimate the product price
    based on its sustainability score, brand, category, and subcategory.
    """
    model = request.app.state.price_model

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Price prediction model not available. Run the training script first.",
        )

    try:
        result = predict_price(
            model=model,
            score=prediction_input.score,
            brand=prediction_input.brand,
            category=prediction_input.category,
            subcategory=prediction_input.subcategory,
        )

        return PricePredictionResponse(
            predicted_price=result["predicted_price"],
            confidence=result["confidence"],
            model_type=result["model_type"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
