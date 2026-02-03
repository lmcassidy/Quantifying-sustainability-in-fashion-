"""Sustainability scoring calculator."""

import pandas as pd


def _minmax_normalize(series: pd.Series) -> pd.Series:
    """
    Apply min-max normalization to a series.

    Parameters
    ----------
    series : pd.Series
        Numeric series to normalize.

    Returns
    -------
    pd.Series
        Normalized series with values between 0 and 1.
    """
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())


def calculate_sustainability_score(df_merged: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate sustainability scores for fashion products.

    Implements a weighted statistical scoring model that combines:
    - Material LCA impacts (CO2, water, energy, chemical)
    - Care-phase impacts (washing energy, water, CO2)
    - Origin impacts (grid intensity, transport, manufacturing)
    - Certification bonuses

    The final score is on a 0-100 scale where higher = more sustainable.

    Parameters
    ----------
    df_merged : pd.DataFrame
        Merged product dataframe with all impact columns.
        Required columns: Id, Material_CO2, Material_Water, Material_Energy,
        Material_Chemical, Percentage_Material, Care_CO2, Care_Water,
        Care_Energy, Origin_Grid, Origin_Transport, Origin_Manufacturing,
        Cert1_Bonus, Cert2_Bonus

    Returns
    -------
    pd.DataFrame
        Product-level dataframe with sustainability scores.
        Key columns: Id, Brand, Product_Name, Price, Score_100, S_final,
        S_env, Score_env_burden, Certification_Total, plus normalized metrics.
    """
    df = df_merged.copy()

    # WEIGHTED MATERIAL IMPACTS (row-level)
    material_cols = ["Material_CO2", "Material_Water", "Material_Energy", "Material_Chemical"]

    for col in material_cols:
        df[f"Weighted_{col}"] = df[col] * (df["Percentage_Material"] / 100)

    weighted_cols = [f"Weighted_{c}" for c in material_cols]

    # AGGREGATE MATERIAL IMPACTS PER PRODUCT
    material_agg = df.groupby("Id")[weighted_cols].sum().reset_index()

    # BUILD PRODUCT-LEVEL TABLE
    prod = df.groupby("Id", as_index=False).agg({
        "Brand": "first",
        "Product_Name": "first",
        "Price": "first",
        "Category": "first",
        "Subcategory": "first",
        "Care_CO2": "first",
        "Care_Water": "first",
        "Care_Energy": "first",
        "Origin_Grid": "first",
        "Origin_Transport": "first",
        "Origin_Manufacturing": "first",
        "Cert1_Bonus": "first",
        "Cert2_Bonus": "first",
    })

    # MERGE MATERIAL AGGREGATES INTO PRODUCT TABLE
    prod = prod.merge(material_agg, on="Id", how="left")

    # NORMALIZATION (min-max, 0 = best, 1 = worst for impacts)

    # Material normalization
    prod["Material_CO2_norm"] = _minmax_normalize(prod["Weighted_Material_CO2"])
    prod["Material_Water_norm"] = _minmax_normalize(prod["Weighted_Material_Water"])
    prod["Material_Energy_norm"] = _minmax_normalize(prod["Weighted_Material_Energy"])
    prod["Material_Chemical_norm"] = _minmax_normalize(prod["Weighted_Material_Chemical"])

    # Care normalization
    prod["Care_CO2_norm"] = _minmax_normalize(prod["Care_CO2"])
    prod["Care_Water_norm"] = _minmax_normalize(prod["Care_Water"])
    prod["Care_Energy_norm"] = _minmax_normalize(prod["Care_Energy"])

    # Origin indices already 0-1 (impact indices)
    prod["Origin_Grid_norm"] = prod["Origin_Grid"]
    prod["Origin_Transport_norm"] = prod["Origin_Transport"]
    prod["Origin_Manufacturing_norm"] = prod["Origin_Manufacturing"]

    # ENVIRONMENTAL BURDEN SCORE (0 = best, 1 = worst)
    env_cols = [
        "Material_CO2_norm", "Material_Water_norm",
        "Material_Energy_norm", "Material_Chemical_norm",
        "Care_CO2_norm", "Care_Water_norm", "Care_Energy_norm",
        "Origin_Grid_norm", "Origin_Transport_norm", "Origin_Manufacturing_norm",
    ]

    prod["Score_env_burden"] = prod[env_cols].mean(axis=1)

    # POSITIVE SUSTAINABILITY SCORE (0-1)
    # Flip burden -> sustainability
    prod["S_env"] = 1 - prod["Score_env_burden"]

    # Certification bonus (positive)
    prod["Certification_Total"] = prod["Cert1_Bonus"].fillna(0) + prod["Cert2_Bonus"].fillna(0)

    # Final sustainability score in 0-1
    prod["S_final"] = (prod["S_env"] + prod["Certification_Total"]).clip(0, 1)

    # FINAL 0-100 SUSTAINABILITY SCORE
    prod["Score_100"] = (prod["S_final"] * 100).round(0)

    # RETURN CLEAN TABLE
    cols_out = [
        "Id", "Brand", "Product_Name", "Price",
        "Category", "Subcategory",
        "Score_100", "S_final", "S_env", "Score_env_burden",
        "Certification_Total",
    ] + env_cols

    return prod[cols_out]


def get_score_breakdown(df_scored: pd.DataFrame, product_id: int) -> dict:
    """
    Get detailed score breakdown for a single product.

    Parameters
    ----------
    df_scored : pd.DataFrame
        Scored dataframe from calculate_sustainability_score().
    product_id : int
        Product ID to get breakdown for.

    Returns
    -------
    dict
        Dictionary with score components and final score.
    """
    row = df_scored[df_scored["Id"] == product_id].iloc[0]

    return {
        "product_id": product_id,
        "product_name": row["Product_Name"],
        "brand": row["Brand"],
        "final_score": row["Score_100"],
        "environmental_score": round(row["S_env"] * 100, 1),
        "certification_bonus": round(row["Certification_Total"] * 100, 1),
        "breakdown": {
            "material_impact": {
                "co2": round(row["Material_CO2_norm"] * 100, 1),
                "water": round(row["Material_Water_norm"] * 100, 1),
                "energy": round(row["Material_Energy_norm"] * 100, 1),
                "chemical": round(row["Material_Chemical_norm"] * 100, 1),
            },
            "care_impact": {
                "co2": round(row["Care_CO2_norm"] * 100, 1),
                "water": round(row["Care_Water_norm"] * 100, 1),
                "energy": round(row["Care_Energy_norm"] * 100, 1),
            },
            "origin_impact": {
                "grid": round(row["Origin_Grid_norm"] * 100, 1),
                "transport": round(row["Origin_Transport_norm"] * 100, 1),
                "manufacturing": round(row["Origin_Manufacturing_norm"] * 100, 1),
            },
        },
    }
