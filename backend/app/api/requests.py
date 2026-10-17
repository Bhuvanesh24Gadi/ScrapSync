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


def get_reserved_quantity(db: Session, listing_id: int) -> float:
    """Sum quantities reserved by pending requests for a listing."""
    total = (
        db.query(ExchangeRequest)
        .filter(
            ExchangeRequest.listing_id == listing_id,
            ExchangeRequest.status == "pending",
        )
        .with_entities(ExchangeRequest.quantity)
        .all()
    )

    return sum(float(row[0]) for row in total)


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
                r.quantity * r.listing.price_per_unit, 2
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

    try:
        listing = (
            db.query(MaterialListing)
            .filter(MaterialListing.id == body.listing_id)
            .with_for_update()
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
                "message": (
                    "You already have a pending request "
                    "for this listing"
                ),
            }

        reserved = get_reserved_quantity(db, listing.id)
        available = max(0.0, float(listing.quantity) - reserved)

        if body.quantity > available:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Only {available:g} {listing.unit} "
                    "is available for new requests"
                ),
            )

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

    except Exception:
        db.rollback()
        raise


@router.patch("/requests/{request_id}/accept")
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
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

        listing = (
            db.query(MaterialListing)
            .filter(
                MaterialListing.id == exchange_request.listing_id
            )
            .with_for_update()
            .first()
        )

        if (
            not listing
            or listing.business_id != current_user.business_id
        ):
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

        # Other pending requests remain reserved, but this
        # request's own reservation is excluded from that total.
        other_reserved = (
            db.query(ExchangeRequest)
            .filter(
                ExchangeRequest.listing_id == listing.id,
                ExchangeRequest.status == "pending",
                ExchangeRequest.id != exchange_request.id,
            )
            .with_entities(ExchangeRequest.quantity)
            .all()
        )

        reserved_by_others = sum(
            float(row[0]) for row in other_reserved
        )

        if (
            listing.status != "active"
            or exchange_request.quantity + reserved_by_others
            > listing.quantity
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "The listing no longer has enough stock "
                    "to accept this request safely"
                ),
            )

        listing.quantity -= exchange_request.quantity
        exchange_request.status = "accepted"

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

    except Exception:
        db.rollback()
        raise


@router.patch("/requests/{request_id}/reject")
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
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

        if (
            not listing
            or listing.business_id != current_user.business_id
        ):
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

    except Exception:
        db.rollback()
        raise