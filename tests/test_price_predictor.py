"""Tests for price prediction models."""

import pytest
import pandas as pd
import numpy as np

from sustainability_scoring.models.price_predictor import PricePredictor


class TestPricePredictorInit:
    """Tests for PricePredictor initialization."""

    def test_default_model_type(self):
        """Should default to random_forest model."""
        predictor = PricePredictor()

        assert predictor.model_type == "random_forest"

    def test_accepts_valid_model_types(self):
        """Should accept all supported model types."""
        for model_type in ["decision_tree", "random_forest", "gradient_boosting"]:
            predictor = PricePredictor(model_type=model_type)
            assert predictor.model_type == model_type

    def test_rejects_invalid_model_type(self):
        """Should raise ValueError for invalid model type."""
        with pytest.raises(ValueError, match="Unknown model type"):
            PricePredictor(model_type="invalid_model")

    def test_model_not_trained_initially(self):
        """Model should be None before training."""
        predictor = PricePredictor()

        assert predictor.model is None


class TestPrepareFeatures:
    """Tests for feature preparation."""

    @pytest.fixture
    def sample_scored_df(self):
        """Create a sample scored dataframe for testing."""
        return pd.DataFrame({
            "Id": [1, 2, 3],
            "Brand": ["H&M", "Zara", "Patagonia"],
            "Product_Name": ["Product A", "Product B", "Product C"],
            "Price": ["€ 50.00", "€ 30.00", "€ 100.00"],
            "Category": ["Woman", "Man", "Woman"],
            "Subcategory": ["Jumper", "Tshirt", "Sweater"],
            "Score_100": [50.0, 60.0, 80.0],
            "S_final": [0.5, 0.6, 0.8],
            "S_env": [0.4, 0.5, 0.6],
            "Score_env_burden": [0.6, 0.5, 0.4],
            "Certification_Total": [0.1, 0.1, 0.2],
            "Material_CO2_norm": [0.3, 0.4, 0.2],
            "Material_Water_norm": [0.4, 0.3, 0.1],
            "Material_Energy_norm": [0.5, 0.4, 0.3],
            "Material_Chemical_norm": [0.35, 0.3, 0.2],
            "Care_CO2_norm": [0.2, 0.3, 0.1],
            "Care_Water_norm": [0.25, 0.35, 0.15],
            "Care_Energy_norm": [0.3, 0.4, 0.2],
            "Origin_Grid_norm": [0.65, 0.55, 0.25],
            "Origin_Transport_norm": [0.40, 0.35, 0.10],
            "Origin_Manufacturing_norm": [0.60, 0.55, 0.30],
        })

    def test_converts_price_to_numeric(self, sample_scored_df):
        """Should convert price from string to numeric."""
        predictor = PricePredictor()

        result = predictor.prepare_features(sample_scored_df)

        assert result["Price"].dtype == np.float64

    def test_drops_leakage_columns(self, sample_scored_df):
        """Should drop columns that would cause leakage."""
        predictor = PricePredictor()

        result = predictor.prepare_features(sample_scored_df)

        leakage_cols = ["Id", "Product_Name", "Score_100", "S_final", "S_env", "Score_env_burden"]
        for col in leakage_cols:
            assert col not in result.columns

    def test_one_hot_encodes_categoricals(self, sample_scored_df):
        """Should one-hot encode categorical columns."""
        predictor = PricePredictor()

        result = predictor.prepare_features(sample_scored_df)

        # Should have encoded Brand columns (drop_first=True, so 2 of 3)
        assert "Brand_Patagonia" in result.columns or "Brand_Zara" in result.columns

        # Original categorical columns should be gone
        assert "Brand" not in result.columns
        assert "Category" not in result.columns


class TestTrainAndPredict:
    """Tests for model training and prediction."""

    @pytest.fixture
    def sample_ml_df(self):
        """Create a sample ML-ready dataframe."""
        np.random.seed(42)
        n = 100

        return pd.DataFrame({
            "Price": np.random.uniform(20, 200, n),
            "Certification_Total": np.random.uniform(0, 0.4, n),
            "Material_CO2_norm": np.random.uniform(0, 1, n),
            "Material_Water_norm": np.random.uniform(0, 1, n),
            "Material_Energy_norm": np.random.uniform(0, 1, n),
            "Material_Chemical_norm": np.random.uniform(0, 1, n),
            "Care_CO2_norm": np.random.uniform(0, 1, n),
            "Care_Water_norm": np.random.uniform(0, 1, n),
            "Care_Energy_norm": np.random.uniform(0, 1, n),
            "Origin_Grid_norm": np.random.uniform(0, 1, n),
            "Origin_Transport_norm": np.random.uniform(0, 1, n),
            "Origin_Manufacturing_norm": np.random.uniform(0, 1, n),
            "Brand_Patagonia": np.random.randint(0, 2, n),
            "Brand_Zara": np.random.randint(0, 2, n),
        })

    def test_train_returns_metrics(self, sample_ml_df):
        """Training should return metrics dictionary."""
        predictor = PricePredictor(model_type="decision_tree")

        metrics = predictor.train(sample_ml_df)

        assert isinstance(metrics, dict)
        assert "R2" in metrics
        assert "MAE" in metrics
        assert "RMSE" in metrics

    def test_model_is_fitted_after_train(self, sample_ml_df):
        """Model should be fitted after training."""
        predictor = PricePredictor(model_type="decision_tree")

        predictor.train(sample_ml_df)

        assert predictor.model is not None

    def test_predict_returns_array(self, sample_ml_df):
        """Predict should return numpy array."""
        predictor = PricePredictor(model_type="decision_tree")
        predictor.train(sample_ml_df)

        X = sample_ml_df.drop(columns=["Price"])
        predictions = predictor.predict(X)

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == len(X)

    def test_predict_raises_if_not_trained(self, sample_ml_df):
        """Predict should raise error if model not trained."""
        predictor = PricePredictor()

        X = sample_ml_df.drop(columns=["Price"])

        with pytest.raises(ValueError, match="Model not trained"):
            predictor.predict(X)


class TestFeatureImportance:
    """Tests for feature importance."""

    @pytest.fixture
    def trained_predictor(self):
        """Create a trained predictor."""
        np.random.seed(42)
        n = 100

        df = pd.DataFrame({
            "Price": np.random.uniform(20, 200, n),
            "Feature_A": np.random.uniform(0, 1, n),
            "Feature_B": np.random.uniform(0, 1, n),
            "Feature_C": np.random.uniform(0, 1, n),
        })

        predictor = PricePredictor(model_type="random_forest")
        predictor.train(df)

        return predictor

    def test_returns_series(self, trained_predictor):
        """Should return pandas Series."""
        importance = trained_predictor.get_feature_importance()

        assert isinstance(importance, pd.Series)

    def test_respects_top_n(self, trained_predictor):
        """Should return only top N features."""
        importance = trained_predictor.get_feature_importance(top_n=2)

        assert len(importance) == 2

    def test_sorted_descending(self, trained_predictor):
        """Should be sorted in descending order."""
        importance = trained_predictor.get_feature_importance()

        assert list(importance.values) == sorted(importance.values, reverse=True)

    def test_raises_if_not_trained(self):
        """Should raise error if model not trained."""
        predictor = PricePredictor()

        with pytest.raises(ValueError, match="Model not trained"):
            predictor.get_feature_importance()
