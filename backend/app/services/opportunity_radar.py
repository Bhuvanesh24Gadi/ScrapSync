from .matching_engine import compatibility
from app.database.models import BuyerRequirement, Business

def find_matches(db, listing):
    requirements = db.query(BuyerRequirement).all()
    results = []
    for req in requirements:
        buyer = db.query(Business).filter(Business.id == req.business_id).first()
        if not buyer or buyer.id == listing.business_id:
            continue
        result = compatibility(listing, req, buyer)
        if result:
            results.append({
                "listing_id": listing.id,
                "business_id": buyer.id,
                "business_name": buyer.name,
                "industry": buyer.industry,
                "location": buyer.location,
                "material_type": listing.material_type,
                "quantity": req.min_quantity,
                "max_quantity": req.max_quantity,
                "max_price": req.max_price,
                **result
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)