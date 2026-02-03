"""Tests for data cleaning utilities."""

import pytest
import pandas as pd

from sustainability_scoring.data.cleaner import clean_product_data, merge_reference_data


class TestCleanProductData:
    """Tests for clean_product_data function."""

    def test_standardizes_certification1_whitespace(self):
        """Should remove leading/trailing whitespace from Certification1."""
        df = pd.DataFrame({
            "Certification1": [" RWS", "RWS ", "Fair Trade "],
            "Certification2": [None, None, None],
            "Material": ["Cotton", "Cotton", "Cotton"],
            "Category": ["Woman", "Woman", "Woman"],
            "Subcategory": ["Jumper", "Jumper", "Jumper"],
        })

        result = clean_product_data(df)

        assert list(result["Certification1"]) == ["RWS", "RWS", "Fair Trade"]

    def test_standardizes_material_case(self):
        """Should standardize material names to title case."""
        df = pd.DataFrame({
            "Certification1": [None],
            "Certification2": [None],
            "Material": ["wool"],
            "Category": ["Woman"],
            "Subcategory": ["Jumper"],
        })

        result = clean_product_data(df)

        assert result.iloc[0]["Material"] == "Wool"

    def test_standardizes_category(self):
        """Should standardize category names."""
        df = pd.DataFrame({
            "Certification1": [None],
            "Certification2": [None],
            "Material": ["Cotton"],
            "Category": ["Woman's Knitwear"],
            "Subcategory": ["Jumper"],
        })

        result = clean_product_data(df)

        assert result.iloc[0]["Category"] == "Woman"

    def test_standardizes_subcategory_case(self):
        """Should apply title case to subcategory."""
        df = pd.DataFrame({
            "Certification1": [None],
            "Certification2": [None],
            "Material": ["Cotton"],
            "Category": ["Woman"],
            "Subcategory": ["sweater"],
        })

        result = clean_product_data(df)

        assert result.iloc[0]["Subcategory"] == "Sweater"

    def test_returns_copy_not_modifying_original(self):
        """Should return a copy, not modify the original."""
        df = pd.DataFrame({
            "Certification1": [" RWS"],
            "Certification2": [None],
            "Material": ["wool"],
            "Category": ["Woman"],
            "Subcategory": ["Jumper"],
        })

        result = clean_product_data(df)

        # Original should be unchanged
        assert df.iloc[0]["Material"] == "wool"
        # Result should be cleaned
        assert result.iloc[0]["Material"] == "Wool"


class TestMergeReferenceData:
    """Tests for merge_reference_data function."""

    def test_adds_material_columns(self):
        """Should add material impact columns after merge."""
        df = pd.DataFrame({
            "Id": [1],
            "Shop_Name": ["TestBrand"],
            "Product_Name": ["Test Product"],
            "Price": ["€ 10.00"],
            "Category": ["Woman"],
            "Subcategory": ["Jumper"],
            "Material": ["Cotton"],
            "Percentage_Material": [100.0],
            "Certification1": [None],
            "Certification2": [None],
            "Care_Instruction": ["Hand wash"],
            "Origin": ["China"],
        })

        result = merge_reference_data(df)

        assert "Material_CO2" in result.columns
        assert "Material_Water" in result.columns
        assert "Material_Energy" in result.columns
        assert "Material_Chemical" in result.columns

    def test_adds_origin_columns(self):
        """Should add origin impact columns after merge."""
        df = pd.DataFrame({
            "Id": [1],
            "Shop_Name": ["TestBrand"],
            "Product_Name": ["Test Product"],
            "Price": ["€ 10.00"],
            "Category": ["Woman"],
            "Subcategory": ["Jumper"],
            "Material": ["Cotton"],
            "Percentage_Material": [100.0],
            "Certification1": [None],
            "Certification2": [None],
            "Care_Instruction": ["Hand wash"],
            "Origin": ["China"],
        })

        result = merge_reference_data(df)

        assert "Origin_Grid" in result.columns
        assert "Origin_Transport" in result.columns
        assert "Origin_Manufacturing" in result.columns

    def test_adds_certification_bonus_columns(self):
        """Should add certification bonus columns after merge."""
        df = pd.DataFrame({
            "Id": [1],
            "Shop_Name": ["TestBrand"],
            "Product_Name": ["Test Product"],
            "Price": ["€ 10.00"],
            "Category": ["Woman"],
            "Subcategory": ["Jumper"],
            "Material": ["Cotton"],
            "Percentage_Material": [100.0],
            "Certification1": ["Fair Trade"],
            "Certification2": ["Bluesign"],
            "Care_Instruction": ["Hand wash"],
            "Origin": ["China"],
        })

        result = merge_reference_data(df)

        assert "Cert1_Bonus" in result.columns
        assert "Cert2_Bonus" in result.columns

    def test_renames_shop_name_to_brand(self):
        """Should rename Shop_Name to Brand."""
        df = pd.DataFrame({
            "Id": [1],
            "Shop_Name": ["TestBrand"],
            "Product_Name": ["Test Product"],
            "Price": ["€ 10.00"],
            "Category": ["Woman"],
            "Subcategory": ["Jumper"],
            "Material": ["Cotton"],
            "Percentage_Material": [100.0],
            "Certification1": [None],
            "Certification2": [None],
            "Care_Instruction": ["Hand wash"],
            "Origin": ["China"],
        })

        result = merge_reference_data(df)

        assert "Brand" in result.columns
        assert "Shop_Name" not in result.columns
