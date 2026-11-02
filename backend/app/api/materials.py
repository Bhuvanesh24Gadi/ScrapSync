
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


class MaterialUpdate(BaseModel):
    material_type: str | None = None
    material_name: str | None = None
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = None
    quality: str | None = None
    price_per_unit: float | None = Field(default=None, ge=0)
    location: str | None = None


def material_response(material):
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


@router.get("/materials")
def list_materials(db: Session = Depends(get_db)):
    materials = (
        db.query(MaterialListing)
        .filter(MaterialListing.status == "active")
        .order_by(MaterialListing.id.desc())
        .all()
    )

    return [material_response(x) for x in materials]


@router.post("/materials")
def create_material(
    body: MaterialIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    return material_response(material)


@router.put("/materials/{material_id}")
def update_material(
    material_id: int,
    body: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = (
        db.query(MaterialListing)
        .filter(MaterialListing.id == material_id)
        .first()
    )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material listing not found",
        )

    if material.business_id != current_user.business_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own listings",
        )

    updates = body.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No update fields provided",
        )

    if any(value is None for value in updates.values()):
        raise HTTPException(
            status_code=422,
            detail="Update fields cannot be null",
        )

    for field, value in updates.items():
        setattr(material, field, value)

    db.commit()
    db.refresh(material)

    return material_response(material)
