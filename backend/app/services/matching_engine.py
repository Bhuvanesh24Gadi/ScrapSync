QUALITY = {
    "Grade A": 100,
    "Grade B": 85,
    "Grade C": 65,
}


def compatibility(listing, requirement, buyer):
    """Return an explainable compatibility score, or None if ineligible."""

    # 1. Hard eligibility checks
    listing_type = (listing.material_type or "").strip().casefold()
    required_type = (requirement.material_type or "").strip().casefold()

    if listing_type != required_type:
        return None

    if listing.business_id == requirement.business_id:
        return None

    # 2. Material score
    material_score = 100

    # 3. Quantity score
    quantity = float(listing.quantity)
    min_qty = float(requirement.min_quantity)
    max_qty = float(requirement.max_quantity)

    if (
        min_qty < 0
        or max_qty <= 0
        or min_qty > max_qty
        or quantity <= 0
    ):
        return None

    if min_qty <= quantity <= max_qty:
        midpoint = (min_qty + max_qty) / 2
        half_range = max((max_qty - min_qty) / 2, 1)
        distance = abs(quantity - midpoint)
        quantity_score = 100 - 20 * (distance / half_range)

    elif quantity < min_qty:
        gap_ratio = (min_qty - quantity) / max(min_qty, 1)
        quantity_score = max(0, 75 - 75 * gap_ratio)

    else:
        excess_ratio = (quantity - max_qty) / max(max_qty, 1)
        quantity_score = max(0, 75 - 75 * excess_ratio)

    quantity_score = max(0, min(100, quantity_score))

    # 4. Quality score
    listing_quality = QUALITY.get(listing.quality, 70)
    required_quality = QUALITY.get(requirement.acceptable_quality, 70)

    if listing_quality == required_quality:
        quality_score = 100
    elif listing_quality > required_quality:
        quality_score = 95
    elif listing_quality >= required_quality - 20:
        quality_score = 70
    else:
        quality_score = 40

    # 5. Price score
    price = float(listing.price_per_unit)
    max_price = float(requirement.max_price)

    if price < 0 or max_price <= 0:
        return None

    # Reject a match if the supplier exceeds the buyer's price limit.
    if price > max_price:
        return None

    price_ratio = price / max_price

    if price_ratio <= 0.50:
        price_score = 100
    elif price_ratio <= 0.75:
        price_score = (
            95 - (price_ratio - 0.50) / 0.25 * 10
        )
    else:
        price_score = (
            85 - (price_ratio - 0.75) / 0.25 * 20
        )

    price_score = max(0, min(100, price_score))

    # 6. Location score
    listing_location = (listing.location or "").strip().casefold()
    required_location = (requirement.location or "").strip().casefold()

    if listing_location and listing_location == required_location:
        location_score = 100
    else:
        location_score = 55

    # 7. Weighted compatibility score
    score = round(
        material_score * 0.30
        + quantity_score * 0.25
        + quality_score * 0.20
        + price_score * 0.15
        + location_score * 0.10
    )

    # 8. Evidence-based explanations
    reasons = [
        f"Material type matches: {listing.material_type}"
    ]

    if min_qty <= quantity <= max_qty:
        reasons.append(
            f"Quantity {quantity:g} is within the buyer's "
            f"range of {min_qty:g}-{max_qty:g}"
        )
    elif quantity < min_qty:
        reasons.append(
            f"Quantity {quantity:g} is below the buyer's "
            f"minimum of {min_qty:g}"
        )
    else:
        reasons.append(
            f"Quantity {quantity:g} exceeds the buyer's "
            f"maximum of {max_qty:g}"
        )

    if listing_quality == required_quality:
        reasons.append(
            f"{listing.quality} quality matches the requirement"
        )
    elif listing_quality > required_quality:
        reasons.append(
            f"{listing.quality} quality exceeds the required quality"
        )
    elif quality_score >= 70:
        reasons.append(
            f"{listing.quality} quality is below the preferred grade "
            "and may need buyer confirmation"
        )
    else:
        reasons.append(
            f"{listing.quality} quality is substantially below "
            "the required grade"
        )

    reasons.append(
        f"Price ₹{price:g}/unit is within the buyer's "
        f"limit of ₹{max_price:g}/unit"
    )

    if location_score == 100:
        reasons.append(
            f"Listing and buyer requirement both specify "
            f"{listing.location}"
        )
    else:
        reasons.append(
            "Location differs from the buyer's preferred location"
        )

    # 9. Potential value estimate, not a confirmed transaction value.
    # Partial quantities may be exchanged; actual stock reservation
    # must be enforced by the request workflow.
    potential_quantity = min(quantity, max_qty)
    potential_value = round(potential_quantity * price, 2)

    return {
        "score": score,
        "material_score": round(material_score),
        "quantity_score": round(quantity_score),
        "quality_score": round(quality_score),
        "price_score": round(price_score),
        "location_score": round(location_score),
        "reasons": reasons,
        "potential_value": potential_value,
    }
