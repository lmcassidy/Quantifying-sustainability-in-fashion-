"""Tests for data loading utilities."""

import pytest
import pandas as pd

from sustainability_scoring.data.loader import (
    load_product_data,
    load_reference_tables,
    load_material_reference,
    load_origin_reference,
    load_care_reference,
    load_certification_reference,
)


class TestLoadReferenceData:
    """Tests for loading reference tables."""

    def test_load_reference_tables_returns_dict(self):
        """load_reference_tables should return a dict with 4 keys."""
        refs = load_reference_tables()

        assert isinstance(refs, dict)
        assert set(refs.keys()) == {"materials", "origins", "care", "certifications"}

    def test_load_reference_tables_all_dataframes(self):
        """All values in reference dict should be DataFrames."""
        refs = load_reference_tables()

        for key, df in refs.items():
            assert isinstance(df, pd.DataFrame), f"{key} is not a DataFrame"

    def test_materials_has_required_columns(self):
        """Materials reference should have required LCA columns."""
        df = load_material_reference()

        required_cols = [
            "Material",
            "Carbon_kgCO2e",
            "Water_L",
            "FossilEnergy_MJ",
            "ChemicalImpact_Score",
        ]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_origins_has_required_columns(self):
        """Origins reference should have required impact columns."""
        df = load_origin_reference()

        required_cols = [
            "Origin",
            "Energy_Grid_Intensity",
            "Transport_Impact_Score",
            "Manufacturing_Impact_Score",
        ]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_care_has_required_columns(self):
        """Care reference should have required impact columns."""
        df = load_care_reference()

        required_cols = ["Care_Instruction", "Energy_Use_MJ", "Water_Use_L", "CO2_kg"]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_certifications_has_required_columns(self):
        """Certifications reference should have required bonus columns."""
        df = load_certification_reference()

        required_cols = ["Certification", "Score_Bonus"]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_materials_not_empty(self):
        """Materials reference should not be empty."""
        df = load_material_reference()
        assert len(df) > 0

    def test_origins_not_empty(self):
        """Origins reference should not be empty."""
        df = load_origin_reference()
        assert len(df) > 0


class TestLoadProductData:
    """Tests for loading product data."""

    def test_load_product_data_returns_dataframe(self, tmp_path):
        """load_product_data should return a DataFrame."""
        # Create a minimal test CSV
        test_csv = tmp_path / "test_products.csv"
        test_csv.write_text(
            "Id,Product_Name,Price,Material,Percentage_Material\n"
            "1,Test Product,€ 10.00,Cotton,100\n"
        )

        df = load_product_data(test_csv)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["Product_Name"] == "Test Product"
