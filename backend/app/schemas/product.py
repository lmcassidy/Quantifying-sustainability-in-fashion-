"""Pydantic schemas for product-related requests and responses."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class MaterialInput(BaseModel):
    """A single material component of a product."""

    name: str = Field(..., description="Material name (e.g., 'Cotton', 'Polyester')")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of this material (0-100)")

    @field_validator("name")
    @classmethod
    def validate_material_name(cls, v: str) -> str:
        """Normalize material name to title case."""
        return v.strip().title()


class ProductInput(BaseModel):
    """Input schema for scoring a single product."""

    product_name: str = Field(..., min_length=1, description="Name of the product")
    brand: Optional[str] = Field(default="Unknown", description="Brand name")
    category: Optional[str] = Field(default="Other", description="Product category")
    subcategory: Optional[str] = Field(default="Other", description="Product subcategory")
    materials: list[MaterialInput] = Field(..., min_length=1, description="List of materials with percentages")
    origin: str = Field(..., description="Manufacturing origin country")
    care_instruction: str = Field(..., description="Care instruction")
    certification1: Optional[str] = Field(default="No Certification", description="First certification")
    certification2: Optional[str] = Field(default="No Certification", description="Second certification")
    price: Optional[str] = Field(default=None, description="Product price (e.g., '50.00')")

    @field_validator("materials")
    @classmethod
    def validate_materials_sum(cls, v: list[MaterialInput]) -> list[MaterialInput]:
        """Validate that material percentages sum to 100."""
        total = sum(m.percentage for m in v)
        if abs(total - 100) > 0.01:
            raise ValueError(f"Material percentages must sum to 100, got {total}")
        return v


class ImpactBreakdown(BaseModel):
    """Breakdown of impact scores for a category."""

    co2: float = Field(..., description="CO2 impact score (0-100, lower is better)")
    water: float = Field(..., description="Water impact score (0-100, lower is better)")
    energy: float = Field(..., description="Energy impact score (0-100, lower is better)")


class MaterialImpactBreakdown(ImpactBreakdown):
    """Material-specific impact breakdown with chemical score."""

    chemical: float = Field(..., description="Chemical impact score (0-100, lower is better)")


class OriginImpactBreakdown(BaseModel):
    """Origin-specific impact breakdown."""

    grid: float = Field(..., description="Grid energy impact (0-100, lower is better)")
    transport: float = Field(..., description="Transport impact (0-100, lower is better)")
    manufacturing: float = Field(..., description="Manufacturing impact (0-100, lower is better)")


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of sustainability score components."""

    material_impact: MaterialImpactBreakdown
    care_impact: ImpactBreakdown
    origin_impact: OriginImpactBreakdown


class ScoreResponse(BaseModel):
    """Response schema for sustainability score."""

    product_name: str
    brand: str
    final_score: float = Field(..., ge=0, le=100, description="Final sustainability score (0-100)")
    environmental_score: float = Field(..., description="Environmental component score")
    certification_bonus: float = Field(..., description="Bonus from certifications")
    breakdown: ScoreBreakdown


class ProductSummary(BaseModel):
    """Summary view of a scored product."""

    id: int
    product_name: str
    brand: str
    category: str
    subcategory: str
    price: Optional[str] = None
    score: float = Field(..., ge=0, le=100)


class ProductDetail(ProductSummary):
    """Detailed view of a scored product including breakdown."""

    materials: list[dict]
    origin: str
    care_instruction: str
    certifications: list[str]
    environmental_score: float
    certification_bonus: float
    breakdown: ScoreBreakdown
