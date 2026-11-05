from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Numeric,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    location = Column(String, nullable=False)
    latitude = Column(Float, default=12.9716)
    longitude = Column(Float, default=77.5946)

    listings = relationship("MaterialListing", back_populates="business")
    requirements = relationship("BuyerRequirement", back_populates="business")


class MaterialListing(Base):
    __tablename__ = "material_listings"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    material_type = Column(String, nullable=False)
    material_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="kg")
    quality = Column(String, default="Grade B")
    price_per_unit = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="listings")


class BuyerRequirement(Base):
    __tablename__ = "buyer_requirements"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    material_type = Column(String, nullable=False)
    min_quantity = Column(Float, nullable=False)
    max_quantity = Column(Float, nullable=False)
    acceptable_quality = Column(String, default="Grade B")
    max_price = Column(Float, nullable=False)
    location = Column(String, nullable=False)

    business = relationship("Business", back_populates="requirements")


class ExchangeRequest(Base):
    __tablename__ = "exchange_requests"

    id = Column(Integer, primary_key=True)
    listing_id = Column(
        Integer,
        ForeignKey("material_listings.id"),
        nullable=False,
    )
    buyer_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("MaterialListing")
    buyer = relationship("Business")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business")


class ExchangeFinancialRecord(Base):
    """
    Stores a fixed financial snapshot for an accepted exchange.

    The fee and reward are only earned after both businesses
    confirm that the physical exchange has taken place.
    """

    __tablename__ = "exchange_financial_records"

    id = Column(Integer, primary_key=True, index=True)

    exchange_request_id = Column(
        Integer,
        ForeignKey("exchange_requests.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    buyer_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)

    # Snapshot of the accepted exchange.
    quantity = Column(Numeric(18, 6), nullable=False)
    unit_price = Column(Numeric(18, 2), nullable=False)
    gross_value = Column(Numeric(18, 2), nullable=False)

    # Proposed platform rates.
    seller_fee_rate = Column(Numeric(7, 4), nullable=False, default=0.0200)
    buyer_reward_rate = Column(Numeric(7, 4), nullable=False, default=0.0050)

    seller_fee_amount = Column(Numeric(18, 2), nullable=False)
    buyer_reward_amount = Column(Numeric(18, 2), nullable=False)

    # Confirmation tracking.
    buyer_confirmed = Column(Boolean, nullable=False, default=False)
    seller_confirmed = Column(Boolean, nullable=False, default=False)

    buyer_confirmed_at = Column(DateTime, nullable=True)
    seller_confirmed_at = Column(DateTime, nullable=True)

    # pending_confirmation -> completed
    status = Column(
        String,
        nullable=False,
        default="pending_confirmation",
    )

    # No real charge or payout is made by this feature.
    seller_fee_status = Column(
        String,
        nullable=False,
        default="not_due",
    )

    buyer_reward_status = Column(
        String,
        nullable=False,
        default="not_earned",
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "exchange_request_id",
            name="uq_financial_record_exchange_request",
        ),
    )