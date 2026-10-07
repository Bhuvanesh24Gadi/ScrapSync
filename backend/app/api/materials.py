from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import MaterialListing, Business

router = APIRouter()

class MaterialIn(BaseModel):
    business_id: int = 1
    material_type: str
    material_name: str
    quantity: float
    unit: str = "kg"
    quality: str = "Grade B"
    price_per_unit: float
    location: str

@router.get("/materials")
def list_materials(db: Session=Depends(get_db)):
    return [dict(id=x.id,business_id=x.business_id,material_type=x.material_type,material_name=x.material_name,quantity=x.quantity,unit=x.unit,quality=x.quality,price_per_unit=x.price_per_unit,location=x.location,status=x.status) for x in db.query(MaterialListing).filter(MaterialListing.status=="active").order_by(MaterialListing.id.desc()).all()]

@router.post("/materials")
def create_material(body: MaterialIn, db: Session=Depends(get_db)):
    if body.quantity <= 0 or body.price_per_unit < 0: raise HTTPException(400,"Quantity must be positive and price cannot be negative")
    business = db.query(Business).filter(Business.id==body.business_id).first()
    if not business: raise HTTPException(404,"Business not found")
    x = MaterialListing(**body.model_dump())
    db.add(x); db.commit(); db.refresh(x)
    return {"id":x.id, **body.model_dump()}