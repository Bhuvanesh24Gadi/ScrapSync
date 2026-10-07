from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import MaterialListing
from app.services.opportunity_radar import find_matches

router=APIRouter()
@router.get("/matches")
def matches(listing_id:int|None=None, db:Session=Depends(get_db)):
    if listing_id:
        listing=db.query(MaterialListing).filter(MaterialListing.id==listing_id).first()
        if not listing: raise HTTPException(404,"Listing not found")
        return find_matches(db,listing)
    results=[]
    for listing in db.query(MaterialListing).filter(MaterialListing.status=="active").all():
        results.extend(find_matches(db,listing))
    return sorted(results,key=lambda x:x["score"],reverse=True)[:20]