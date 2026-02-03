#!/usr/bin/env python
"""
Script to train and save the price prediction model.

Run this once before starting the API to enable price predictions.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import joblib
import pandas as pd

from sustainability_scoring.models.price_predictor import PricePredictor
from sustainability_scoring.data.loader import load_reference_tables
from sustainability_scoring.data.cleaner import merge_reference_data, clean_product_data
from sustainability_scoring.scoring.calculator import calculate_sustainability_score


def train_and_save_model():
    """Train the price prediction model and save it."""
    print("Loading data...")

    # Try to load scored data
    data_dir = Path(__file__).parent.parent / "data"
    scored_path = data_dir / "sustainability_scores.csv"

    if scored_path.exists():
        df_scored = pd.read_csv(scored_path)
        print(f"Loaded {len(df_scored)} scored products from {scored_path}")
    else:
        # Load and score from scratch
        raw_path = data_dir / "FashionProductsDataset_Original.csv"
        if not raw_path.exists():
            print(f"Error: No data found at {raw_path}")
            return

        df = pd.read_csv(raw_path)
        df = clean_product_data(df)
        references = load_reference_tables()
        df = merge_reference_data(df, references)
        df = df.dropna(subset=["Material_CO2"])
        df_scored = calculate_sustainability_score(df)
        print(f"Scored {len(df_scored)} products from raw data")

    # Initialize predictor
    predictor = PricePredictor(model_type="random_forest")

    # Prepare features
    print("Preparing features...")
    df_ml = predictor.prepare_features(df_scored)

    # Drop rows with missing prices
    df_ml = df_ml.dropna(subset=["Price"])
    print(f"Training on {len(df_ml)} products with valid prices")

    # Train model
    print("Training model...")
    metrics = predictor.train(df_ml, target_col="Price", test_size=0.2)

    print(f"\nModel Performance:")
    print(f"  R2:   {metrics['R2']:.3f}")
    print(f"  MAE:  {metrics['MAE']:.2f}")
    print(f"  RMSE: {metrics['RMSE']:.2f}")

    # Store feature names for prediction
    predictor.feature_names_ = predictor.feature_names

    # Save model
    model_dir = Path(__file__).parent / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "price_model.joblib"

    joblib.dump(predictor, model_path)
    print(f"\nModel saved to {model_path}")

    # Print top features
    print("\nTop 10 Feature Importances:")
    importance = predictor.get_feature_importance(top_n=10)
    for feat, imp in importance.items():
        print(f"  {feat}: {imp:.4f}")


if __name__ == "__main__":
    train_and_save_model()
