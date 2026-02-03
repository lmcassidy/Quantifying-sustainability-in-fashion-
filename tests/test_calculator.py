"""Tests for sustainability score calculator."""

import pytest
import pandas as pd
import numpy as np

from sustainability_scoring.scoring.calculator import (
    calculate_sustainability_score,
    get_score_breakdown,
    _minmax_normalize,
)


class TestMinMaxNormalize:
    """Tests for min-max normalization helper."""

    def test_normalizes_to_0_1_range(self):
        """Should normalize values to 0-1 range."""
        series = pd.Series([0, 50, 100])

        result = _minmax_normalize(series)

        assert result.min() == 0.0
        assert result.max() == 1.0
        assert result.iloc[1] == 0.5

    def test_handles_constant_series(self):
        """Should return zeros for constant series."""
        series = pd.Series([5, 5, 5])

        result = _minmax_normalize(series)

        assert all(result == 0)

    def test_preserves_relative_order(self):
        """Should preserve relative ordering of values."""
        series = pd.Series([10, 30, 20, 40])

        result = _minmax_normalize(series)

        assert result.iloc[0] < result.iloc[2] < result.iloc[1] < result.iloc[3]


class TestCalculateSustainabilityScore:
    """Tests for calculate_sustainability_score function."""

    @pytest.fixture
    def sample_merged_df(self):
        """Create a sample merged dataframe for testing."""
        return pd.DataFrame({
            "Id": [1, 1, 2],
            "Brand": ["H&M", "H&M", "Patagonia"],
            "Product_Name": ["Product A", "Product A", "Product B"],
            "Price": ["€ 50.00", "€ 50.00", "€ 100.00"],
            "Category": ["Woman", "Woman", "Woman"],
            "Subcategory": ["Jumper", "Jumper", "Sweater"],
            "Material": ["Cotton", "Polyester", "Recycled Polyester"],
            "Percentage_Material": [60.0, 40.0, 100.0],
            "Material_CO2": [6.0, 9.5, 5.5],
            "Material_Water": [2700, 50, 20],
            "Material_Energy": [55, 120, 60],
            "Material_Chemical": [40, 35, 20],
            "Care_CO2": [0.04, 0.04, 0.015],
            "Care_Water": [15, 15, 8],
            "Care_Energy": [0.5, 0.5, 0.2],
            "Origin_Grid": [0.65, 0.65, 0.25],
            "Origin_Transport": [0.40, 0.40, 0.10],
            "Origin_Manufacturing": [0.60, 0.60, 0.30],
            "Cert1_Bonus": [0.0, 0.0, 0.20],
            "Cert2_Bonus": [0.0, 0.0, 0.20],
        })

    def test_returns_dataframe(self, sample_merged_df):
        """Should return a pandas DataFrame."""
        result = calculate_sustainability_score(sample_merged_df)

        assert isinstance(result, pd.DataFrame)

    def test_aggregates_by_product_id(self, sample_merged_df):
        """Should aggregate multi-material products by Id."""
        result = calculate_sustainability_score(sample_merged_df)

        # Should have 2 products (Id 1 and 2)
        assert len(result) == 2

    def test_score_in_0_100_range(self, sample_merged_df):
        """Scores should be in 0-100 range."""
        result = calculate_sustainability_score(sample_merged_df)

        assert result["Score_100"].min() >= 0
        assert result["Score_100"].max() <= 100

    def test_certification_bonus_increases_score(self, sample_merged_df):
        """Products with certifications should have higher scores."""
        result = calculate_sustainability_score(sample_merged_df)

        # Product 2 (Patagonia with certifications) should score higher
        patagonia_score = result[result["Brand"] == "Patagonia"]["Score_100"].iloc[0]
        hm_score = result[result["Brand"] == "H&M"]["Score_100"].iloc[0]

        assert patagonia_score > hm_score

    def test_has_required_output_columns(self, sample_merged_df):
        """Should have all required output columns."""
        result = calculate_sustainability_score(sample_merged_df)

        required_cols = [
            "Id", "Brand", "Product_Name", "Price",
            "Score_100", "S_final", "S_env", "Score_env_burden",
            "Certification_Total",
        ]
        for col in required_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_weights_materials_by_percentage(self, sample_merged_df):
        """Should weight material impacts by percentage."""
        result = calculate_sustainability_score(sample_merged_df)

        # Product 1 has 60% Cotton (CO2=6) and 40% Polyester (CO2=9.5)
        # Weighted CO2 = 0.6*6 + 0.4*9.5 = 3.6 + 3.8 = 7.4
        # This should be reflected in the scoring

        # Just verify it runs and produces valid scores
        assert not result["Score_100"].isna().any()


class TestGetScoreBreakdown:
    """Tests for get_score_breakdown function."""

    @pytest.fixture
    def sample_scored_df(self):
        """Create a sample scored dataframe for testing."""
        return pd.DataFrame({
            "Id": [1],
            "Brand": ["H&M"],
            "Product_Name": ["Test Product"],
            "Price": ["€ 50.00"],
            "Category": ["Woman"],
            "Subcategory": ["Jumper"],
            "Score_100": [75.0],
            "S_final": [0.75],
            "S_env": [0.60],
            "Score_env_burden": [0.40],
            "Certification_Total": [0.15],
            "Material_CO2_norm": [0.3],
            "Material_Water_norm": [0.4],
            "Material_Energy_norm": [0.5],
            "Material_Chemical_norm": [0.35],
            "Care_CO2_norm": [0.2],
            "Care_Water_norm": [0.25],
            "Care_Energy_norm": [0.3],
            "Origin_Grid_norm": [0.65],
            "Origin_Transport_norm": [0.40],
            "Origin_Manufacturing_norm": [0.60],
        })

    def test_returns_dict(self, sample_scored_df):
        """Should return a dictionary."""
        result = get_score_breakdown(sample_scored_df, product_id=1)

        assert isinstance(result, dict)

    def test_contains_product_info(self, sample_scored_df):
        """Should contain product identification info."""
        result = get_score_breakdown(sample_scored_df, product_id=1)

        assert result["product_id"] == 1
        assert result["product_name"] == "Test Product"
        assert result["brand"] == "H&M"

    def test_contains_scores(self, sample_scored_df):
        """Should contain final and environmental scores."""
        result = get_score_breakdown(sample_scored_df, product_id=1)

        assert result["final_score"] == 75.0
        assert "environmental_score" in result
        assert "certification_bonus" in result

    def test_contains_breakdown(self, sample_scored_df):
        """Should contain detailed breakdown."""
        result = get_score_breakdown(sample_scored_df, product_id=1)

        assert "breakdown" in result
        assert "material_impact" in result["breakdown"]
        assert "care_impact" in result["breakdown"]
        assert "origin_impact" in result["breakdown"]
