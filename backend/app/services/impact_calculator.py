from app.database.models import Business, MaterialListing, ExchangeRequest


def dashboard(db):
    listings = (
        db.query(MaterialListing)
        .filter(MaterialListing.status == "active")
        .all()
    )

    accepted = (
        db.query(ExchangeRequest)
        .filter(ExchangeRequest.status == "accepted")
        .all()
    )

    total_kg = sum(float(listing.quantity or 0) for listing in listings)
    diverted = 0.0
    potential_value = 0.0

    for request in accepted:
        quantity = float(request.quantity or 0)
        diverted += quantity

        listing = (
            db.query(MaterialListing)
            .filter(MaterialListing.id == request.listing_id)
            .first()
        )

        if listing:
            price = float(listing.price_per_unit or 0)
            potential_value += quantity * price

    return {
        "total_material_kg": round(total_kg, 1),
        "opportunities": 0,
        "potential_value": round(potential_value, 2),
        "diverted_kg": round(diverted, 1),
        "businesses": db.query(Business).count(),
        "accepted_requests": len(accepted),
        "material_mix": []
    }
