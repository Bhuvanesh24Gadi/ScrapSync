from sqlalchemy import func
from app.database.models import Business, MaterialListing, ExchangeRequest

def dashboard(db):
    listings = db.query(MaterialListing).filter(MaterialListing.status=="active").all()
    requests = db.query(ExchangeRequest).all()
    accepted = [r for r in requests if r.status == "accepted"]
    total_kg = sum(x.quantity for x in listings)
    diverted = sum(x.quantity for x in accepted)
    potential_value = sum(x.quantity * (x.listing.price_per_unit if x.listing else 0) for x in accepted)
    return {
        "total_material_kg": round(total_kg,1),
        "opportunities": 0,
        "potential_value": round(potential_value),
        "diverted_kg": round(diverted,1),
        "businesses": db.query(Business).count(),
        "accepted_requests": len(accepted),
        "material_mix": []
    }