"""Data cleaning and merging utilities for fashion product datasets."""

import pandas as pd

from sustainability_scoring.data.loader import load_reference_tables


def clean_product_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize raw product data.

    Performs the following cleaning operations:
    - Standardizes certification names (removes whitespace, fixes typos)
    - Standardizes material names (e.g., 'wool' -> 'Wool')
    - Standardizes category names
    - Strips whitespace from subcategory and applies title case

    Parameters
    ----------
    df : pd.DataFrame
        Raw product dataframe from load_product_data().

    Returns
    -------
    pd.DataFrame
        Cleaned product dataframe.
    """
    df_clean = df.copy()

    # Clean Certification1
    df_clean["Certification1"] = df_clean["Certification1"].replace({
        " RWS": "RWS",
        "RWS ": "RWS",
        "Fair Trade ": "Fair Trade",
        " Fair Trade ": "Fair Trade",
    })

    # Clean Certification2
    df_clean["Certification2"] = df_clean["Certification2"].replace({
        " RCS": "RCS",
        "RCS ": "RCS",
        "Fair Trade ": "Fair Trade",
        " Fair Trade ": "Fair Trade",
    })

    # Clean Material
    df_clean["Material"] = df_clean["Material"].replace({
        "wool": "Wool",
    })

    # Clean Category
    df_clean["Category"] = df_clean["Category"].replace({
        "Woman's Knitwear": "Woman",
    })
    df_clean["Category"] = df_clean["Category"].str.strip()

    # Clean Subcategory
    df_clean["Subcategory"] = df_clean["Subcategory"].str.strip().str.title()

    return df_clean


def merge_reference_data(df: pd.DataFrame, references: dict[str, pd.DataFrame] = None) -> pd.DataFrame:
    """
    Merge product data with all reference tables.

    Adds LCA impact data from materials, care instructions, origin,
    and certification bonus scores.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned product dataframe.
    references : dict[str, pd.DataFrame], optional
        Dictionary of reference tables. If None, loads from package data.

    Returns
    -------
    pd.DataFrame
        Merged dataframe with all impact columns.
    """
    if references is None:
        references = load_reference_tables()

    df_merged = df.copy()

    # Merge Material Table
    material_cols = ["Material", "Carbon_kgCO2e", "Water_L", "FossilEnergy_MJ", "ChemicalImpact_Score"]
    df_merged = df_merged.merge(
        references["materials"][material_cols],
        how="left",
        on="Material",
    )

    # Merge Care Table
    care_cols = ["Care_Instruction", "Energy_Use_MJ", "Water_Use_L", "CO2_kg"]
    df_merged = df_merged.merge(
        references["care"][care_cols],
        how="left",
        on="Care_Instruction",
    )

    # Merge Origin Table
    origin_cols = ["Origin", "Energy_Grid_Intensity", "Transport_Impact_Score", "Manufacturing_Impact_Score"]
    df_merged = df_merged.merge(
        references["origins"][origin_cols],
        how="left",
        on="Origin",
    )

    # Merge Certification Bonuses
    cert_bonus = references["certifications"][["Certification", "Score_Bonus"]]

    # Merge Certification 1 Bonus
    df_merged = df_merged.merge(
        cert_bonus.rename(columns={"Score_Bonus": "Cert1_Bonus"}),
        how="left",
        left_on="Certification1",
        right_on="Certification",
    ).drop(columns=["Certification"])

    # Merge Certification 2 Bonus
    df_merged = df_merged.merge(
        cert_bonus.rename(columns={"Score_Bonus": "Cert2_Bonus"}),
        how="left",
        left_on="Certification2",
        right_on="Certification",
    ).drop(columns=["Certification"])

    # Rename columns for clarity
    df_merged = df_merged.rename(columns={
        "Carbon_kgCO2e": "Material_CO2",
        "Water_L": "Material_Water",
        "FossilEnergy_MJ": "Material_Energy",
        "ChemicalImpact_Score": "Material_Chemical",
        "Energy_Use_MJ": "Care_Energy",
        "Water_Use_L": "Care_Water",
        "CO2_kg": "Care_CO2",
        "Energy_Grid_Intensity": "Origin_Grid",
        "Transport_Impact_Score": "Origin_Transport",
        "Manufacturing_Impact_Score": "Origin_Manufacturing",
        "Certification1": "Certificate1",
        "Certification2": "Certificate2",
        "Shop_Name": "Brand",
    })

    # Reorder columns
    ordered_cols = [
        "Id", "Brand", "Product_Name", "Price",
        "Category", "Subcategory",
        "Material", "Percentage_Material",
        "Material_CO2", "Material_Water", "Material_Energy", "Material_Chemical",
        "Care_Instruction",
        "Care_CO2", "Care_Energy", "Care_Water",
        "Origin",
        "Origin_Grid", "Origin_Transport", "Origin_Manufacturing",
        "Certificate1", "Cert1_Bonus",
        "Certificate2", "Cert2_Bonus",
    ]

    # Keep ordered columns plus any extras
    df_merged = df_merged[ordered_cols + [c for c in df_merged.columns if c not in ordered_cols]]

    return df_merged


def prepare_dataset(filepath: str) -> pd.DataFrame:
    """
    Full pipeline: load, clean, and merge product data.

    Parameters
    ----------
    filepath : str
        Path to raw product CSV.

    Returns
    -------
    pd.DataFrame
        Fully prepared dataset ready for scoring.
    """
    from sustainability_scoring.data.loader import load_product_data

    df = load_product_data(filepath)
    df = clean_product_data(df)
    df = merge_reference_data(df)

    # Drop rows with missing material data
    df = df.dropna(subset=[
        "Material_CO2",
        "Material_Water",
        "Material_Energy",
        "Material_Chemical",
    ])

    return df
