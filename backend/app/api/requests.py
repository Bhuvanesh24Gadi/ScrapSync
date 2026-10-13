from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import (
    ExchangeRequest,
    MaterialListing,
    User,
)
from app.auth_dependencies import get_current_user

router = APIRouter()


class RequestIn(BaseModel):
    listing_id: int
    quantity: float = Field(gt=0)


@router.get("/requests")
def get_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business_id = current_user.business_id

    rows = (
        db.query(ExchangeRequest)
        .join(
            MaterialListing,
            ExchangeRequest.listing_id == MaterialListing.id,
        )
        .filter(
            or_(
                ExchangeRequest.buyer_id == business_id,
                MaterialListing.business_id == business_id,
            )
        )
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


@router.post("/requests", status_code=201)
def create_request(
    body: RequestIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    buyer_id = current_user.business_id

    listing = (
        db.query(MaterialListing)
        .filter(MaterialListing.id == body.listing_id)
        .first()
    )

    if not listing or listing.status != "active":
        raise HTTPException(
            status_code=404,
            detail="Active material listing not found",
        )

    if listing.business_id == buyer_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot request your own listing",
        )

    if body.quantity > listing.quantity:
        raise HTTPException(
            status_code=400,
            detail="Invalid requested quantity",
        )

    existing = (
        db.query(ExchangeRequest)
        .filter(
            ExchangeRequest.listing_id == listing.id,
            ExchangeRequest.buyer_id == buyer_id,
            ExchangeRequest.status == "pending",
        )
        .first()
    )

    if existing:
        return {
            "id": existing.id,
            "status": existing.status,
            "message": "You already have a pending request for this listing",
        }

    exchange_request = ExchangeRequest(
        listing_id=listing.id,
        buyer_id=buyer_id,
        quantity=body.quantity,
        status="pending",
    )

    db.add(exchange_request)
    db.commit()
    db.refresh(exchange_request)

    return {
        "id": exchange_request.id,
        "status": exchange_request.status,
        "message": "Exchange request created successfully",
    }


@router.patch("/requests/{request_id}/accept")
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exchange_request = (
        db.query(ExchangeRequest)
        .filter(ExchangeRequest.id == request_id)
        .first()
    )

    if not exchange_request:
        raise HTTPException(
            status_code=404,
            detail="Exchange request not found",
        )

    listing = exchange_request.listing

    if not listing or listing.business_id != current_user.business_id:
        raise HTTPException(
            status_code=404,
            detail="Exchange request not found",
        )

    if exchange_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only pending requests can be accepted. "
                f"Current status: '{exchange_request.status}'"
            ),
        )

    if listing.status != "active" or exchange_request.quantity > listing.quantity:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity is no longer available",
        )

    exchange_request.status = "accepted"
    listing.quantity -= exchange_request.quantity

    if listing.quantity <= 0:
        listing.quantity = 0
        listing.status = "exchanged"

    db.commit()
    db.refresh(exchange_request)

    return {
        "id": exchange_request.id,
        "status": exchange_request.status,
        "quantity": exchange_request.quantity,
        "message": "Exchange accepted successfully",
    }


@router.patch("/requests/{request_id}/reject")
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exchange_request = (
        db.query(ExchangeRequest)
        .filter(ExchangeRequest.id == request_id)
        .first()
    )

    if not exchange_request:
        raise HTTPException(
            status_code=404,
            detail="Exchange request not found",
        )

    listing = exchange_request.listing

    if not listing or listing.business_id != current_user.business_id:
        raise HTTPException(
            status_code=404,
            detail="Exchange request not found",
        )

    if exchange_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only pending requests can be rejected. "
                f"Current status: '{exchange_request.status}'"
            ),
        )

    exchange_request.status = "rejected"
    db.commit()
    db.refresh(exchange_request)

    return {
        "id": exchange_request.id,
        "status": exchange_request.status,
        "message": "Exchange request rejected successfully",
    }