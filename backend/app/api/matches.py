from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import MaterialListing
from app.services.opportunity_radar import find_matches

router = APIRouter()


@router.get("/matches")
def matches(
    listing_id: int | None = None,
    db: Session = Depends(get_db),
):
    if listing_id is not None:
        listing = (
            db.query(MaterialListing)
            .filter(
                MaterialListing.id == listing_id,
                MaterialListing.status == "active",
            )
            .first()
        )

        if not listing:
            raise HTTPException(
                status_code=404,
                detail="Active listing not found",
            )

        return find_matches(db, listing)

    active_listings = (
        db.query(MaterialListing)
        .filter(MaterialListing.status == "active")
        .all()
    )

    results = []

    for listing in active_listings:
        results.extend(find_matches(db, listing))

    return sorted(
        results,
        key=lambda match: match["score"],
        reverse=True,
    )[:20]