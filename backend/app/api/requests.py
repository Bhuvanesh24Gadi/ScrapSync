from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import (
    ExchangeRequest,
    ExchangeFinancialRecord,
    MaterialListing,
    User,
)
from app.auth_dependencies import get_current_user


router = APIRouter()


# Proposed rates:
# Seller pays 2% of the exchange value.
# Buyer earns a 0.5% cash reward after completion.
SELLER_FEE_RATE = Decimal("0.0200")
BUYER_REWARD_RATE = Decimal("0.0050")
MONEY_PLACES = Decimal("0.01")


class RequestIn(BaseModel):
    listing_id: int
    quantity: float = Field(gt=0)


def money(value: Decimal) -> Decimal:
    """Round a monetary amount to two decimal places."""
    return value.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


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


def create_financial_record(
    db: Session,
    exchange_request: ExchangeRequest,
    listing: MaterialListing,
):
    """
    Create one immutable financial snapshot for an accepted request.
    A unique request ID prevents duplicate financial records.
    """

    existing = (
        db.query(ExchangeFinancialRecord)
        .filter(
            ExchangeFinancialRecord.exchange_request_id
            == exchange_request.id
        )
        .first()
    )

    if existing:
        return existing

    quantity = Decimal(str(exchange_request.quantity))
    unit_price = money(Decimal(str(listing.price_per_unit)))
    gross_value = money(quantity * unit_price)

    seller_fee = money(gross_value * SELLER_FEE_RATE)
    buyer_reward = money(gross_value * BUYER_REWARD_RATE)

    record = ExchangeFinancialRecord(
        exchange_request_id=exchange_request.id,
        buyer_id=exchange_request.buyer_id,
        seller_id=listing.business_id,
        quantity=quantity,
        unit_price=unit_price,
        gross_value=gross_value,
        seller_fee_rate=SELLER_FEE_RATE,
        buyer_reward_rate=BUYER_REWARD_RATE,
        seller_fee_amount=seller_fee,
        buyer_reward_amount=buyer_reward,
        buyer_confirmed=False,
        seller_confirmed=False,
        status="pending_confirmation",
        seller_fee_status="not_due",
        buyer_reward_status="not_earned",
    )

    db.add(record)
    return record


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

    response = []

    for request in rows:
        financial = (
            db.query(ExchangeFinancialRecord)
            .filter(
                ExchangeFinancialRecord.exchange_request_id
                == request.id
            )
            .first()
        )

        item = {
            "id": request.id,
            "buyer_name": request.buyer.name,
            "material_name": request.listing.material_name,
            "quantity": request.quantity,
            "status": request.status,
            "can_manage": (
                request.listing.business_id == business_id
            ),
            "value": round(
                request.quantity * request.listing.price_per_unit,
                2,
            ),
            "financial_record": None,
        }

        if financial:
            item["financial_record"] = {
                "status": financial.status,
                "gross_value": float(financial.gross_value),
                "seller_fee_amount": float(
                    financial.seller_fee_amount
                ),
                "buyer_reward_amount": float(
                    financial.buyer_reward_amount
                ),
                "buyer_confirmed": financial.buyer_confirmed,
                "seller_confirmed": financial.seller_confirmed,
                "seller_fee_status": financial.seller_fee_status,
                "buyer_reward_status": financial.buyer_reward_status,
            }

        response.append(item)

    return response


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
        available = max(
            0.0,
            float(listing.quantity) - reserved,
        )

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

        # Exclude this request's own reservation.
        other_pending = (
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
            float(row[0]) for row in other_pending
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

        # Preserve the existing stock deduction behaviour.
        listing.quantity -= exchange_request.quantity
        exchange_request.status = "accepted"

        if listing.quantity <= 0:
            listing.quantity = 0
            listing.status = "exchanged"

        # Snapshot the price and calculate proposed fee/reward.
        create_financial_record(
            db,
            exchange_request,
            listing,
        )

        # Request acceptance and financial record are committed together.
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


@router.patch("/requests/{request_id}/confirm")
def confirm_exchange(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    The buyer or seller confirms the physical exchange.
    The exchange completes only after both businesses confirm.
    """

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

        if exchange_request.status != "accepted":
            raise HTTPException(
                status_code=400,
                detail="Only accepted exchanges can be confirmed",
            )

        listing = (
            db.query(MaterialListing)
            .filter(
                MaterialListing.id == exchange_request.listing_id
            )
            .first()
        )

        if not listing:
            raise HTTPException(
                status_code=404,
                detail="Material listing not found",
            )

        business_id = current_user.business_id

        if business_id not in (
            exchange_request.buyer_id,
            listing.business_id,
        ):
            raise HTTPException(
                status_code=403,
                detail="You are not part of this exchange",
            )

        financial = (
            db.query(ExchangeFinancialRecord)
            .filter(
                ExchangeFinancialRecord.exchange_request_id
                == exchange_request.id
            )
            .with_for_update()
            .first()
        )

        if not financial:
            raise HTTPException(
                status_code=409,
                detail=(
                    "No financial record exists for this exchange. "
                    "Only exchanges accepted after this feature "
                    "is deployed can be confirmed here."
                ),
            )

        if financial.status == "completed":
            return {
                "id": exchange_request.id,
                "status": "completed",
                "buyer_confirmed": financial.buyer_confirmed,
                "seller_confirmed": financial.seller_confirmed,
                "seller_fee_status": financial.seller_fee_status,
                "buyer_reward_status": financial.buyer_reward_status,
                "message": "This exchange is already completed",
            }

        now = datetime.utcnow()

        if business_id == exchange_request.buyer_id:
            if not financial.buyer_confirmed:
                financial.buyer_confirmed = True
                financial.buyer_confirmed_at = now
        else:
            if not financial.seller_confirmed:
                financial.seller_confirmed = True
                financial.seller_confirmed_at = now

        # Earn fee/reward only after both confirmations.
        if (
            financial.buyer_confirmed
            and financial.seller_confirmed
        ):
            financial.status = "completed"
            financial.completed_at = now
            financial.seller_fee_status = "due"
            financial.buyer_reward_status = "pending_payout"

        db.commit()
        db.refresh(financial)

        return {
            "id": exchange_request.id,
            "status": financial.status,
            "buyer_confirmed": financial.buyer_confirmed,
            "seller_confirmed": financial.seller_confirmed,
            "gross_value": float(financial.gross_value),
            "seller_fee_amount": float(
                financial.seller_fee_amount
            ),
            "buyer_reward_amount": float(
                financial.buyer_reward_amount
            ),
            "seller_fee_status": financial.seller_fee_status,
            "buyer_reward_status": financial.buyer_reward_status,
            "message": (
                "Exchange completed. Both businesses confirmed."
                if financial.status == "completed"
                else "Your confirmation has been recorded. "
                     "Waiting for the other business to confirm."
            ),
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