"""Service for calculating sustainability scores."""

import pandas as pd

from sustainability_scoring.data.cleaner import merge_reference_data
from sustainability_scoring.scoring.calculator import (
    calculate_sustainability_score,
    get_score_breakdown,
)

from app.schemas.product import (
    ProductInput,
    ScoreResponse,
    ScoreBreakdown,
    MaterialImpactBreakdown,
    ImpactBreakdown,
    OriginImpactBreakdown,
)


def score_product(
    product: ProductInput,
    reference_data: dict[str, pd.DataFrame],
) -> ScoreResponse:
    """
    Calculate sustainability score for a single product.

    Converts the ProductInput to a DataFrame, merges with reference data,
    calculates the score, and returns a structured response.
    """
    # Build rows for each material (the scoring system expects one row per material)
    rows = []
    for i, material in enumerate(product.materials):
        row = {
            "Id": 1,  # Single product
            "Product_Name": product.product_name,
            "Shop_Name": product.brand,
            "Category": product.category,
            "Subcategory": product.subcategory,
            "Material": material.name,
            "Percentage_Material": material.percentage,
            "Origin": product.origin,
            "Care_Instruction": product.care_instruction,
            "Certification1": product.certification1 or "None",
            "Certification2": product.certification2 or "None",
            "Price": product.price or "0.00",
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # Merge with reference data
    df_merged = merge_reference_data(df, reference_data)

    # Check for missing reference data
    missing_materials = df_merged[df_merged["Material_CO2"].isna()]["Material"].unique()
    if len(missing_materials) > 0:
        raise ValueError(f"Unknown materials: {', '.join(missing_materials)}")

    missing_care = df_merged[df_merged["Care_CO2"].isna()]["Care_Instruction"].unique()
    if len(missing_care) > 0:
        raise ValueError(f"Unknown care instruction: {', '.join(missing_care)}")

    missing_origin = df_merged[df_merged["Origin_Grid"].isna()]["Origin"].unique()
    if len(missing_origin) > 0:
        raise ValueError(f"Unknown origin: {', '.join(missing_origin)}")

    # Calculate sustainability score
    df_scored = calculate_sustainability_score(df_merged)

    # Get the score breakdown
    breakdown_dict = get_score_breakdown(df_scored, product_id=1)

    # Convert to response schema
    return ScoreResponse(
        product_name=breakdown_dict["product_name"],
        brand=breakdown_dict["brand"],
        final_score=breakdown_dict["final_score"],
        environmental_score=breakdown_dict["environmental_score"],
        certification_bonus=breakdown_dict["certification_bonus"],
        breakdown=ScoreBreakdown(
            material_impact=MaterialImpactBreakdown(
                co2=breakdown_dict["breakdown"]["material_impact"]["co2"],
                water=breakdown_dict["breakdown"]["material_impact"]["water"],
                energy=breakdown_dict["breakdown"]["material_impact"]["energy"],
                chemical=breakdown_dict["breakdown"]["material_impact"]["chemical"],
            ),
            care_impact=ImpactBreakdown(
                co2=breakdown_dict["breakdown"]["care_impact"]["co2"],
                water=breakdown_dict["breakdown"]["care_impact"]["water"],
                energy=breakdown_dict["breakdown"]["care_impact"]["energy"],
            ),
            origin_impact=OriginImpactBreakdown(
                grid=breakdown_dict["breakdown"]["origin_impact"]["grid"],
                transport=breakdown_dict["breakdown"]["origin_impact"]["transport"],
                manufacturing=breakdown_dict["breakdown"]["origin_impact"]["manufacturing"],
            ),
        ),
    )
