"""Pydantic schemas for reference data responses."""

from pydantic import BaseModel, Field


class MaterialReference(BaseModel):
    """Material with LCA impact data."""

    name: str
    category: str
    carbon_kg_co2e: float = Field(..., description="Carbon footprint (kg CO2e)")
    water_l: float = Field(..., description="Water consumption (liters)")
    fossil_energy_mj: float = Field(..., description="Fossil energy use (MJ)")
    chemical_impact: float = Field(..., description="Chemical impact score")
    notes: str = ""


class OriginReference(BaseModel):
    """Manufacturing origin with impact indices."""

    name: str
    energy_grid_intensity: float = Field(..., ge=0, le=1)
    transport_impact: float = Field(..., ge=0, le=1)
    manufacturing_impact: float = Field(..., ge=0, le=1)
    notes: str = ""


class CareReference(BaseModel):
    """Care instruction with lifecycle impacts."""

    name: str
    energy_use_mj: float
    water_use_l: float
    co2_kg: float
    notes: str = ""


class CertificationReference(BaseModel):
    """Certification with score bonus."""

    name: str
    category: str
    score_bonus: float = Field(..., ge=0, le=1)
    description: str = ""


class ReferenceDataResponse(BaseModel):
    """Complete reference data response."""

    materials: list[MaterialReference]
    origins: list[OriginReference]
    care_instructions: list[CareReference]
    certifications: list[CertificationReference]
