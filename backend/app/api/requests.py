from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import (
    ExchangeRequest,
    MaterialListing,
    Business,
)

router = APIRouter()


class RequestIn(BaseModel):
    listing_id: int
    buyer_id: int
    quantity: float


@router.get("/requests")
def get_requests(db: Session = Depends(get_db)):
    rows = (
        db.query(ExchangeRequest)
        .order_by(ExchangeRequest.id.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "buyer_name": r.buyer.name,
            "material_name": r.listing.material_name,
            "quantity": r.quantity,
            "status": r.status,
            "value": round(
                r.quantity * r.listing.price_per_unit
            ),
        }
        for r in rows
    ]


@router.post("/requests")
def create_request(
    body: RequestIn,
    db: Session = Depends(get_db),
):
    listing = (
        db.query(MaterialListing)
        .filter(MaterialListing.id == body.listing_id)
        .first()
    )

    buyer = (
        db.query(Business)
        .filter(Business.id == body.buyer_id)
        .first()
    )

    if not listing or not buyer:
        raise HTTPException(
            status_code=404,
            detail="Listing or buyer not found",
        )

    if body.quantity <= 0 or body.quantity > listing.quantity:
        raise HTTPException(
            status_code=400,
            detail="Invalid requested quantity",
        )

    existing = (
        db.query(ExchangeRequest)
        .filter(
            ExchangeRequest.listing_id == body.listing_id,
            ExchangeRequest.buyer_id == body.buyer_id,
            ExchangeRequest.status == "pending",
        )
        .first()
    )

    if existing:
        return {
            "id": existing.id,
            "status": existing.status,
        }

    r = ExchangeRequest(
        listing_id=body.listing_id,
        buyer_id=body.buyer_id,
        quantity=body.quantity,
        status="pending",
    )

    db.add(r)
    db.commit()
    db.refresh(r)

    return {
        "id": r.id,
        "status": r.status,
    }


@router.patch("/requests/{request_id}/accept")
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    request = (
        db.query(ExchangeRequest)
        .filter(ExchangeRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Exchange request not found",
        )

    if request.status == "accepted":
        return {
            "id": request.id,
            "status": "accepted",
            "message": "Request is already accepted",
        }

    if request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot accept a request with status '{request.status}'",
        )

    listing = request.listing

    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Material listing not found",
        )

    if request.quantity > listing.quantity:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity is no longer available",
        )

    # Accept the exchange.
    request.status = "accepted"

    # Remove the exchanged quantity from the available listing.
    listing.quantity -= request.quantity

    # If nothing remains, close the listing.
    if listing.quantity <= 0:
        listing.quantity = 0
        listing.status = "exchanged"

    db.commit()
    db.refresh(request)

    return {
        "id": request.id,
        "status": request.status,
        "quantity": request.quantity,
        "message": "Exchange accepted successfully",
    }