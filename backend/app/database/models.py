from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
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
    listing_id = Column(Integer, ForeignKey("material_listings.id"), nullable=False)
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
    business_id = Column(
        Integer,
        ForeignKey("businesses.id"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business")
