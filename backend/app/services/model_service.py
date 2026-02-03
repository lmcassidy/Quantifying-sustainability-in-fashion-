"""Service for loading and using the price prediction model."""

from pathlib import Path
from typing import Optional

import joblib

from sustainability_scoring.models.price_predictor import PricePredictor


# Path to the saved model
MODEL_DIR = Path(__file__).parent.parent.parent / "models"
MODEL_PATH = MODEL_DIR / "price_model.joblib"


def load_price_model() -> Optional[PricePredictor]:
    """
    Load the pre-trained price prediction model.

    Returns None if the model file doesn't exist.
    """
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


def save_price_model(model: PricePredictor) -> None:
    """Save a trained price prediction model."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)


def predict_price(
    model: PricePredictor,
    score: float,
    brand: str,
    category: str,
    subcategory: str,
) -> dict:
    """
    Predict price for a product based on its features.

    Returns a dictionary with predicted price and confidence.
    """
    import pandas as pd

    # Create a feature DataFrame matching the model's expected format
    # The model expects one-hot encoded features, so we need to handle this carefully
    feature_dict = {
        "Score_100": score,
    }

    # The model was trained with one-hot encoded brand/category/subcategory
    # For prediction, we need to create dummy columns
    df = pd.DataFrame([feature_dict])

    try:
        # Get the feature names the model expects
        if hasattr(model, "feature_names_") and model.feature_names_ is not None:
            # Create a DataFrame with all zeros for missing features
            expected_features = model.feature_names_
            for feat in expected_features:
                if feat not in df.columns:
                    df[feat] = 0

            # Set the appropriate one-hot columns to 1
            brand_col = f"Brand_{brand}"
            if brand_col in expected_features:
                df[brand_col] = 1

            category_col = f"Category_{category}"
            if category_col in expected_features:
                df[category_col] = 1

            subcategory_col = f"Subcategory_{subcategory}"
            if subcategory_col in expected_features:
                df[subcategory_col] = 1

            # Reorder columns to match training
            df = df[expected_features]

        prediction = model.predict(df)[0]

        # Determine confidence based on whether we matched known categories
        confidence = "high" if brand_col in expected_features else "medium"

        return {
            "predicted_price": round(float(prediction), 2),
            "confidence": confidence,
            "model_type": model.model_type,
        }
    except Exception as e:
        # Fallback: simple prediction based on score only
        return {
            "predicted_price": round(score * 0.5 + 20, 2),  # Simple heuristic
            "confidence": "low",
            "model_type": "fallback",
        }
