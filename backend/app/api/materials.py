from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import MaterialListing, Business, User
from app.auth_dependencies import get_current_user

router = APIRouter()


class MaterialIn(BaseModel):
    material_type: str
    material_name: str
    quantity: float = Field(gt=0)
    unit: str = "kg"
    quality: str = "Grade B"
    price_per_unit: float = Field(ge=0)
    location: str


@router.get("/materials")
def list_materials(db: Session = Depends(get_db)):
    materials = (
        db.query(MaterialListing)
        .filter(MaterialListing.status == "active")
        .order_by(MaterialListing.id.desc())
        .all()
    )

    return [
        {
            "id": x.id,
            "business_id": x.business_id,
            "material_type": x.material_type,
            "material_name": x.material_name,
            "quantity": x.quantity,
            "unit": x.unit,
            "quality": x.quality,
            "price_per_unit": x.price_per_unit,
            "location": x.location,
            "status": x.status,
        }
        for x in materials
    ]


@router.post("/materials")
def create_material(
    body: MaterialIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Determine ownership from the authenticated user.
    business = (
        db.query(Business)
        .filter(Business.id == current_user.business_id)
        .first()
    )

    if not business:
        raise HTTPException(
            status_code=404,
            detail="Your business was not found",
        )

    material = MaterialListing(
        business_id=current_user.business_id,
        material_type=body.material_type,
        material_name=body.material_name,
        quantity=body.quantity,
        unit=body.unit,
        quality=body.quality,
        price_per_unit=body.price_per_unit,
        location=body.location,
    )

    db.add(material)
    db.commit()
    db.refresh(material)

    return {
        "id": material.id,
        "business_id": material.business_id,
        "material_type": material.material_type,
        "material_name": material.material_name,
        "quantity": material.quantity,
        "unit": material.unit,
        "quality": material.quality,
        "price_per_unit": material.price_per_unit,
        "location": material.location,
        "status": material.status,
    }