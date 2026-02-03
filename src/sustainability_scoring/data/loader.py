"""Data loading utilities for fashion product datasets."""

from pathlib import Path
from typing import Union

import pandas as pd

from sustainability_scoring.reference import (
    MATERIALS_CSV,
    ORIGINS_CSV,
    CARE_CSV,
    CERTIFICATIONS_CSV,
)


def load_product_data(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Load raw fashion product dataset from CSV.

    Parameters
    ----------
    filepath : str or Path
        Path to the product CSV file.

    Returns
    -------
    pd.DataFrame
        Raw product dataframe with columns:
        Id, Product_Name, Price, Material, Percentage_Material,
        Certification1, Certification2, Shop_Name, Category,
        Subcategory, Origin, Care_Instruction
    """
    df = pd.read_csv(filepath)
    return df


def load_reference_tables() -> dict[str, pd.DataFrame]:
    """
    Load all reference tables for sustainability scoring.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary with keys: 'materials', 'origins', 'care', 'certifications'
        Each value is a pandas DataFrame with the reference data.
    """
    return {
        "materials": pd.read_csv(MATERIALS_CSV),
        "origins": pd.read_csv(ORIGINS_CSV),
        "care": pd.read_csv(CARE_CSV),
        "certifications": pd.read_csv(CERTIFICATIONS_CSV),
    }


def load_material_reference() -> pd.DataFrame:
    """Load material LCA reference table."""
    return pd.read_csv(MATERIALS_CSV)


def load_origin_reference() -> pd.DataFrame:
    """Load origin impact reference table."""
    return pd.read_csv(ORIGINS_CSV)


def load_care_reference() -> pd.DataFrame:
    """Load care instruction impact reference table."""
    return pd.read_csv(CARE_CSV)


def load_certification_reference() -> pd.DataFrame:
    """Load certification bonus reference table."""
    return pd.read_csv(CERTIFICATIONS_CSV)
