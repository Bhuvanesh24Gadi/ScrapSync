from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Business

router=APIRouter()
@router.get("/businesses")
def businesses(db:Session=Depends(get_db)):
    return [{"id":x.id,"name":x.name,"industry":x.industry,"location":x.location} for x in db.query(Business).all()]