from .models import (
    Business,
    MaterialListing,
    BuyerRequirement,
    ExchangeRequest,
)


def force_seed(db):
    # Clear existing demo data
    db.query(ExchangeRequest).delete()
    db.query(BuyerRequirement).delete()
    db.query(MaterialListing).delete()
    db.query(Business).delete()
    db.commit()

    # ---------------------------------------------------------
    # BUSINESSES
    # ---------------------------------------------------------

    businesses = [
        Business(
            name="EcoWorks Demo",
            industry="Garment manufacturing",
            location="Bengaluru",
        ),
        Business(
            name="EcoThreads",
            industry="Textile recycling",
            location="Bengaluru",
        ),
        Business(
            name="ReFab Studio",
            industry="Upcycling & circular design",
            location="Bengaluru",
        ),
        Business(
            name="GreenFiber Labs",
            industry="Recycled fiber processing",
            location="Bengaluru",
        ),
        Business(
            name="PackLoop",
            industry="Sustainable packaging",
            location="Bengaluru",
        ),
        Business(
            name="BoardCycle",
            industry="Paper recycling",
            location="Bengaluru",
        ),
        Business(
            name="UrbanWeave Textiles",
            industry="Apparel manufacturing",
            location="Bengaluru",
        ),
        Business(
            name="StitchCraft Bengaluru",
            industry="Fashion manufacturing",
            location="Bengaluru",
        ),
        Business(
            name="CircularCrafts",
            industry="Interior & product design",
            location="Bengaluru",
        ),
        Business(
            name="FiberForm Labs",
            industry="Material innovation",
            location="Bengaluru",
        ),
    ]

    db.add_all(businesses)
    db.flush()

    # ---------------------------------------------------------
    # MATERIAL LISTINGS
    # ---------------------------------------------------------

    listings = [
        # EcoWorks Demo
        MaterialListing(
            business_id=1,
            material_type="Textile",
            material_name="Cotton fabric scraps",
            quantity=42,
            quality="Grade B",
            price_per_unit=18,
            location="Bengaluru",
        ),
        MaterialListing(
            business_id=1,
            material_type="Cardboard",
            material_name="Corrugated cardboard offcuts",
            quantity=80,
            quality="Grade A",
            price_per_unit=7,
            location="Bengaluru",
        ),
        MaterialListing(
            business_id=1,
            material_type="Textile",
            material_name="Mixed cotton remnants",
            quantity=65,
            quality="Grade B",
            price_per_unit=15,
            location="Bengaluru",
        ),

        # UrbanWeave Textiles
        MaterialListing(
            business_id=7,
            material_type="Textile",
            material_name="Denim cutting offcuts",
            quantity=85,
            quality="Grade B",
            price_per_unit=22,
            location="Bengaluru",
        ),
        MaterialListing(
            business_id=7,
            material_type="Textile",
            material_name="Polyester fabric rolls",
            quantity=120,
            quality="Grade A",
            price_per_unit=26,
            location="Bengaluru",
        ),

        # StitchCraft Bengaluru
        MaterialListing(
            business_id=8,
            material_type="Textile",
            material_name="Cotton jersey remnants",
            quantity=55,
            quality="Grade B",
            price_per_unit=19,
            location="Bengaluru",
        ),
        MaterialListing(
            business_id=8,
            material_type="Textile",
            material_name="Printed textile rejects",
            quantity=38,
            quality="Grade C",
            price_per_unit=10,
            location="Bengaluru",
        ),

        # ReFab Studio
        MaterialListing(
            business_id=3,
            material_type="Textile",
            material_name="Denim offcuts",
            quantity=26,
            quality="Grade B",
            price_per_unit=22,
            location="Bengaluru",
        ),
        MaterialListing(
            business_id=3,
            material_type="Cardboard",
            material_name="Clean packaging sheets",
            quantity=48,
            quality="Grade A",
            price_per_unit=8,
            location="Bengaluru",
        ),

        # PackLoop
        MaterialListing(
            business_id=5,
            material_type="Cardboard",
            material_name="Packaging board rejects",
            quantity=110,
            quality="Grade A",
            price_per_unit=9,
            location="Bengaluru",
        ),

        # BoardCycle
        MaterialListing(
            business_id=6,
            material_type="Cardboard",
            material_name="Used carton sheets",
            quantity=150,
            quality="Grade A",
            price_per_unit=6,
            location="Bengaluru",
        ),

        # CircularCrafts
        MaterialListing(
            business_id=9,
            material_type="Wood",
            material_name="Plywood workshop offcuts",
            quantity=72,
            quality="Grade B",
            price_per_unit=14,
            location="Bengaluru",
        ),

        # FiberForm Labs
        MaterialListing(
            business_id=10,
            material_type="Textile",
            material_name="Industrial textile remnants",
            quantity=95,
            quality="Grade B",
            price_per_unit=16,
            location="Bengaluru",
        ),

        # GreenFiber Labs
        MaterialListing(
            business_id=4,
            material_type="Textile",
            material_name="Fiber-grade cotton scraps",
            quantity=140,
            quality="Grade B",
            price_per_unit=20,
            location="Bengaluru",
        ),

        # Another cardboard listing
        MaterialListing(
            business_id=5,
            material_type="Cardboard",
            material_name="Corrugated carton surplus",
            quantity=95,
            quality="Grade A",
            price_per_unit=8,
            location="Bengaluru",
        ),
    ]

    db.add_all(listings)
    db.flush()

    # ---------------------------------------------------------
    # BUYER REQUIREMENTS
    # ---------------------------------------------------------

    requirements = [
        # EcoThreads
        BuyerRequirement(
            business_id=2,
            material_type="Textile",
            min_quantity=20,
            max_quantity=100,
            acceptable_quality="Grade B",
            max_price=25,
            location="Bengaluru",
        ),

        # ReFab Studio
        BuyerRequirement(
            business_id=3,
            material_type="Textile",
            min_quantity=15,
            max_quantity=60,
            acceptable_quality="Grade B",
            max_price=30,
            location="Bengaluru",
        ),

        # GreenFiber Labs
        BuyerRequirement(
            business_id=4,
            material_type="Textile",
            min_quantity=30,
            max_quantity=150,
            acceptable_quality="Grade B",
            max_price=24,
            location="Bengaluru",
        ),

        # PackLoop
        BuyerRequirement(
            business_id=5,
            material_type="Cardboard",
            min_quantity=40,
            max_quantity=200,
            acceptable_quality="Grade A",
            max_price=12,
            location="Bengaluru",
        ),

        # BoardCycle
        BuyerRequirement(
            business_id=6,
            material_type="Cardboard",
            min_quantity=50,
            max_quantity=300,
            acceptable_quality="Grade A",
            max_price=10,
            location="Bengaluru",
        ),

        # UrbanWeave Textiles
        BuyerRequirement(
            business_id=7,
            material_type="Textile",
            min_quantity=20,
            max_quantity=120,
            acceptable_quality="Grade B",
            max_price=28,
            location="Bengaluru",
        ),

        # StitchCraft
        BuyerRequirement(
            business_id=8,
            material_type="Textile",
            min_quantity=15,
            max_quantity=80,
            acceptable_quality="Grade B",
            max_price=24,
            location="Bengaluru",
        ),

        # CircularCrafts - wood
        BuyerRequirement(
            business_id=9,
            material_type="Wood",
            min_quantity=30,
            max_quantity=100,
            acceptable_quality="Grade B",
            max_price=20,
            location="Bengaluru",
        ),

        # FiberForm Labs
        BuyerRequirement(
            business_id=10,
            material_type="Textile",
            min_quantity=40,
            max_quantity=150,
            acceptable_quality="Grade B",
            max_price=22,
            location="Bengaluru",
        ),

        # FiberForm Labs - cardboard
        BuyerRequirement(
            business_id=10,
            material_type="Cardboard",
            min_quantity=50,
            max_quantity=180,
            acceptable_quality="Grade A",
            max_price=11,
            location="Bengaluru",
        ),

        # EcoThreads second requirement
        BuyerRequirement(
            business_id=2,
            material_type="Textile",
            min_quantity=50,
            max_quantity=200,
            acceptable_quality="Grade B",
            max_price=21,
            location="Bengaluru",
        ),

        # PackLoop second requirement
        BuyerRequirement(
            business_id=5,
            material_type="Cardboard",
            min_quantity=60,
            max_quantity=250,
            acceptable_quality="Grade A",
            max_price=10,
            location="Bengaluru",
        ),
    ]

    db.add_all(requirements)
    db.commit()


def seed_if_empty(db):
    if db.query(Business).count() == 0:
        force_seed(db)