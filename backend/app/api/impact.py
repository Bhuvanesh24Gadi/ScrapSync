from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import MaterialListing
from app.services.impact_calculator import dashboard

router=APIRouter()
@router.get("/impact/dashboard")
def impact(db:Session=Depends(get_db)):
    d=dashboard(db)
    # material mix
    rows=db.query(MaterialListing.material_type, __import__("sqlalchemy").func.sum(MaterialListing.quantity)).filter(MaterialListing.status=="active").group_by(MaterialListing.material_type).all()
    total=max(d["total_material_kg"],1)
    d["material_mix"]=[{"name":name,"kg":round(float(kg),1),"percent":round(float(kg)/total*100)} for name,kg in rows]
    # opportunity count is derived from matches
    from app.services.opportunity_radar import find_matches
    all_matches=[]
    for listing in db.query(MaterialListing).filter(MaterialListing.status=="active").all(): all_matches += find_matches(db,listing)
    d["opportunities"]=len(all_matches)
    d["top_matches"]=all_matches[:5]
    return d