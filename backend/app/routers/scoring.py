"""API routes for sustainability scoring."""

from fastapi import APIRouter, HTTPException, Request

from app.schemas.product import ProductInput, ScoreResponse
from app.services.scoring_service import score_product

router = APIRouter()


@router.post("/score", response_model=ScoreResponse)
async def calculate_score(product: ProductInput, request: Request) -> ScoreResponse:
    """
    Calculate sustainability score for a product.

    Accepts product details including materials, origin, care instructions,
    and certifications. Returns a score from 0-100 with detailed breakdown.
    """
    try:
        reference_data = request.app.state.reference_data
        if reference_data is None:
            raise HTTPException(status_code=503, detail="Reference data not loaded")

        result = score_product(product, reference_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")
