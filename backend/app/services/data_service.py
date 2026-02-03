"""Service for loading and managing reference data and sample products."""

from pathlib import Path

import pandas as pd

from sustainability_scoring.data.loader import load_reference_tables
from sustainability_scoring.data.cleaner import merge_reference_data, clean_product_data
from sustainability_scoring.scoring.calculator import calculate_sustainability_score


# Path to the data directory
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def load_reference_data() -> dict[str, pd.DataFrame]:
    """Load all reference tables for sustainability scoring."""
    return load_reference_tables()


def load_sample_products() -> pd.DataFrame:
    """
    Load and score sample products from the dataset.

    Returns a DataFrame with scored products for the demo.
    """
    # Try to load pre-scored data first
    scored_path = DATA_DIR / "sustainability_scores.csv"
    if scored_path.exists():
        df = pd.read_csv(scored_path)
        return df

    # If not available, try the merged dataset
    merged_path = DATA_DIR / "Merged_product_dataset.csv"
    if merged_path.exists():
        df = pd.read_csv(merged_path)
        df_scored = calculate_sustainability_score(df)
        return df_scored

    # Fallback: load and process raw data
    raw_path = DATA_DIR / "FashionProductsDataset_Original.csv"
    if raw_path.exists():
        df = pd.read_csv(raw_path)
        df = clean_product_data(df)
        references = load_reference_tables()
        df = merge_reference_data(df, references)
        df = df.dropna(subset=["Material_CO2"])
        df_scored = calculate_sustainability_score(df)
        return df_scored

    # Return empty DataFrame if no data found
    return pd.DataFrame()


def get_valid_materials(reference_data: dict[str, pd.DataFrame]) -> list[str]:
    """Get list of valid material names."""
    return reference_data["materials"]["Material"].tolist()


def get_valid_origins(reference_data: dict[str, pd.DataFrame]) -> list[str]:
    """Get list of valid origin countries."""
    return reference_data["origins"]["Origin"].tolist()


def get_valid_care_instructions(reference_data: dict[str, pd.DataFrame]) -> list[str]:
    """Get list of valid care instructions."""
    return reference_data["care"]["Care_Instruction"].tolist()


def get_valid_certifications(reference_data: dict[str, pd.DataFrame]) -> list[str]:
    """Get list of valid certifications."""
    return reference_data["certifications"]["Certification"].tolist()
