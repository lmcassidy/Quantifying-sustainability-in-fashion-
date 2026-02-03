"""API routes for reference data."""

from fastapi import APIRouter, Request

from app.schemas.reference import (
    MaterialReference,
    OriginReference,
    CareReference,
    CertificationReference,
)

router = APIRouter()


@router.get("/materials", response_model=list[MaterialReference])
async def list_materials(request: Request) -> list[MaterialReference]:
    """
    List all valid materials with their LCA impact data.
    """
    reference_data = request.app.state.reference_data
    if reference_data is None:
        return []

    materials = []
    for _, row in reference_data["materials"].iterrows():
        materials.append(
            MaterialReference(
                name=row["Material"],
                category=row["Category"],
                carbon_kg_co2e=row["Carbon_kgCO2e"],
                water_l=row["Water_L"],
                fossil_energy_mj=row["FossilEnergy_MJ"],
                chemical_impact=row["ChemicalImpact_Score"],
                notes=row.get("Notes", ""),
            )
        )
    return materials


@router.get("/origins", response_model=list[OriginReference])
async def list_origins(request: Request) -> list[OriginReference]:
    """
    List all valid manufacturing origins with their impact indices.
    """
    reference_data = request.app.state.reference_data
    if reference_data is None:
        return []

    origins = []
    for _, row in reference_data["origins"].iterrows():
        origins.append(
            OriginReference(
                name=row["Origin"],
                energy_grid_intensity=row["Energy_Grid_Intensity"],
                transport_impact=row["Transport_Impact_Score"],
                manufacturing_impact=row["Manufacturing_Impact_Score"],
                notes=row.get("Notes", ""),
            )
        )
    return origins


@router.get("/care", response_model=list[CareReference])
async def list_care_instructions(request: Request) -> list[CareReference]:
    """
    List all valid care instructions with their lifecycle impacts.
    """
    reference_data = request.app.state.reference_data
    if reference_data is None:
        return []

    care = []
    for _, row in reference_data["care"].iterrows():
        care.append(
            CareReference(
                name=row["Care_Instruction"],
                energy_use_mj=row["Energy_Use_MJ"],
                water_use_l=row["Water_Use_L"],
                co2_kg=row["CO2_kg"],
                notes=row.get("Notes", ""),
            )
        )
    return care


@router.get("/certifications", response_model=list[CertificationReference])
async def list_certifications(request: Request) -> list[CertificationReference]:
    """
    List all valid certifications with their score bonuses.
    """
    reference_data = request.app.state.reference_data
    if reference_data is None:
        return []

    certs = []
    for _, row in reference_data["certifications"].iterrows():
        certs.append(
            CertificationReference(
                name=row["Certification"],
                category=row["Category"],
                score_bonus=row["Score_Bonus"],
                description=row.get("Description", ""),
            )
        )
    return certs
