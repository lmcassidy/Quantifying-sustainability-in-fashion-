"""API routes for sample products."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Query

from app.schemas.product import ProductSummary

router = APIRouter()


@router.get("/products", response_model=list[ProductSummary])
async def list_products(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: Optional[str] = Query(default=None),
) -> list[ProductSummary]:
    """
    List sample products from the dataset.

    Returns scored products for browsing in the demo UI.
    """
    sample_products = request.app.state.sample_products

    if sample_products is None or sample_products.empty:
        return []

    df = sample_products.copy()

    # Filter by category if specified
    if category:
        df = df[df["Category"].str.lower() == category.lower()]

    # Apply pagination
    df = df.iloc[offset : offset + limit]

    # Convert to response format
    products = []
    for _, row in df.iterrows():
        products.append(
            ProductSummary(
                id=int(row["Id"]),
                product_name=row["Product_Name"],
                brand=row.get("Brand", "Unknown"),
                category=row.get("Category", "Other"),
                subcategory=row.get("Subcategory", "Other"),
                price=str(row["Price"]) if "Price" in row else None,
                score=float(row["Score_100"]),
            )
        )

    return products


@router.get("/products/{product_id}", response_model=ProductSummary)
async def get_product(product_id: int, request: Request) -> ProductSummary:
    """
    Get a single product by ID.
    """
    sample_products = request.app.state.sample_products

    if sample_products is None or sample_products.empty:
        raise HTTPException(status_code=404, detail="No products available")

    product = sample_products[sample_products["Id"] == product_id]

    if product.empty:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    row = product.iloc[0]
    return ProductSummary(
        id=int(row["Id"]),
        product_name=row["Product_Name"],
        brand=row.get("Brand", "Unknown"),
        category=row.get("Category", "Other"),
        subcategory=row.get("Subcategory", "Other"),
        price=str(row["Price"]) if "Price" in row else None,
        score=float(row["Score_100"]),
    )


@router.get("/categories", response_model=list[str])
async def list_categories(request: Request) -> list[str]:
    """
    List available product categories.
    """
    sample_products = request.app.state.sample_products

    if sample_products is None or sample_products.empty:
        return []

    return sample_products["Category"].dropna().unique().tolist()
