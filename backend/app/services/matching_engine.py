QUALITY = {
    "Grade A": 100,
    "Grade B": 85,
    "Grade C": 65,
}


def compatibility(listing, requirement, buyer):
    """
    Calculate an explainable compatibility score between a material
    listing and a buyer requirement.

    The score is intentionally continuous rather than binary:
    quantity, quality, price, and location all contribute differently.
    """

    # ---------------------------------------------------------
    # 1. HARD ELIGIBILITY CHECKS
    # ---------------------------------------------------------

    # Material type must match.
    if listing.material_type.lower() != requirement.material_type.lower():
        return None

    # Do not match a business with itself.
    if listing.business_id == requirement.business_id:
        return None

    # Location mismatch is allowed only as a weaker match.
    # Material and business relevance remain the primary constraints.

    # ---------------------------------------------------------
    # 2. MATERIAL SCORE
    # ---------------------------------------------------------

    material_score = 100

    # ---------------------------------------------------------
    # 3. QUANTITY SCORE
    # ---------------------------------------------------------

    min_qty = requirement.min_quantity
    max_qty = requirement.max_quantity
    quantity = listing.quantity

    if min_qty <= quantity <= max_qty:
        # Best score is achieved near the middle of the buyer's
        # preferred quantity range.

        midpoint = (min_qty + max_qty) / 2
        half_range = max((max_qty - min_qty) / 2, 1)

        distance = abs(quantity - midpoint)

        quantity_score = 100 - (
            25 * min(distance / half_range, 1)
        )

    elif quantity < min_qty:
        # Slightly below minimum can still be useful.
        gap_ratio = (min_qty - quantity) / max(min_qty, 1)

        quantity_score = max(
            45,
            80 - (gap_ratio * 60)
        )

    else:
        # Above the maximum can still be useful, but creates
        # handling/storage constraints.
        excess_ratio = (quantity - max_qty) / max(max_qty, 1)

        quantity_score = max(
            45,
            80 - (excess_ratio * 60)
        )

    quantity_score = max(0, min(100, quantity_score))

    # ---------------------------------------------------------
    # 4. QUALITY SCORE
    # ---------------------------------------------------------

    listing_quality = QUALITY.get(listing.quality, 70)
    required_quality = QUALITY.get(
        requirement.acceptable_quality,
        70
    )

    if listing.quality == requirement.acceptable_quality:
        quality_score = 100

    elif listing_quality > required_quality:
        # Better-than-required material is highly desirable.
        quality_score = 95

    elif listing_quality >= required_quality - 20:
        # Slightly lower quality can still potentially work.
        quality_score = 75

    else:
        quality_score = 50

    # ---------------------------------------------------------
    # 5. PRICE SCORE
    # ---------------------------------------------------------

    max_price = max(requirement.max_price, 1)
    price_ratio = listing.price_per_unit / max_price

    if price_ratio <= 0.50:
        # Very attractive price.
        price_score = 100

    elif price_ratio <= 0.75:
        # Good price.
        price_score = 95 - (
            (price_ratio - 0.50) / 0.25 * 10
        )

    elif price_ratio <= 1.00:
        # Still within buyer budget, but increasingly expensive.
        price_score = 85 - (
            (price_ratio - 0.75) / 0.25 * 20
        )

    elif price_ratio <= 1.25:
        # Slightly above target.
        price_score = 65 - (
            (price_ratio - 1.00) / 0.25 * 20
        )

    elif price_ratio <= 1.50:
        # Expensive, but potentially negotiable.
        price_score = 45 - (
            (price_ratio - 1.25) / 0.25 * 25
        )

    else:
        # Too expensive to be considered.
        return None

    price_score = max(0, min(100, price_score))

    # ---------------------------------------------------------
    # 6. LOCATION SCORE
    # ---------------------------------------------------------

    if listing.location.lower() == requirement.location.lower():
        location_score = 100
    else:
        location_score = 55

    # ---------------------------------------------------------
    # 7. FINAL WEIGHTED SCORE
    # ---------------------------------------------------------

    score = round(
        material_score * 0.30
        + quantity_score * 0.25
        + quality_score * 0.20
        + price_score * 0.15
        + location_score * 0.10
    )

    # ---------------------------------------------------------
    # 8. EXPLAINABLE REASONS
    # ---------------------------------------------------------

    reasons = []

    reasons.append(
        "Material type matches buyer requirement"
    )

    if quantity_score >= 90:
        reasons.append(
            "Quantity is a strong fit for the buyer's preferred range"
        )
    elif quantity_score >= 75:
        reasons.append(
            "Quantity is reasonably close to the buyer's preferred range"
        )
    else:
        reasons.append(
            "Quantity may require adjustment or partial fulfillment"
        )

    if quality_score >= 95:
        if listing.quality == requirement.acceptable_quality:
            reasons.append(
                f"{listing.quality} quality directly matches the requirement"
            )
        else:
            reasons.append(
                f"{listing.quality} quality exceeds the buyer's requirement"
            )
    elif quality_score >= 75:
        reasons.append(
            f"{listing.quality} quality may be usable with processing"
        )
    else:
        reasons.append(
            f"{listing.quality} quality is below the preferred requirement"
        )

    if price_score >= 95:
        reasons.append(
            "Listed price is highly attractive for the buyer"
        )
    elif price_score >= 80:
        reasons.append(
            "Listed price is within a reasonable target range"
        )
    elif price_score >= 60:
        reasons.append(
            "Listed price is slightly above the buyer's preferred range"
        )
    else:
        reasons.append(
            "Listed price is relatively high for this requirement"
        )

    if location_score == 100:
        reasons.append(
            f"Both businesses are in {listing.location}"
        )
    else:
        reasons.append(
            "Location differs from the buyer's preferred location"
        )

    # ---------------------------------------------------------
    # 9. POTENTIAL VALUE
    # ---------------------------------------------------------

    potential_value = round(
        min(listing.quantity, requirement.max_quantity)
        * listing.price_per_unit
    )

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