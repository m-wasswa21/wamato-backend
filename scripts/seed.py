"""
Seed the database with sample Wamato properties (mirrors Flutter sample data).
Run: python scripts/seed.py
Idempotent — safe to run multiple times.
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.property import Property, PropertyPhoto, PropertyType, PropertyStatus, ListingPackage

# ── Unsplash photo URLs per property type ────────────────────────────────────
HOUSE_PHOTOS = [
    "https://images.unsplash.com/photo-1570129477492-45c003dc5e4f?w=800&q=80",
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
]
VILLA_PHOTOS = [
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80",
    "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&q=80",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80",
]
APARTMENT_PHOTOS = [
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80",
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80",
]
LAND_PHOTOS = [
    "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80",
    "https://images.unsplash.com/photo-1625602812206-5ec545ca1231?w=800&q=80",
    "https://images.unsplash.com/photo-1536895058696-a69b1c7ba34f?w=800&q=80",
]
OFFICE_PHOTOS = [
    "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80",
    "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800&q=80",
    "https://images.unsplash.com/photo-1604328698692-f76ea9498e76?w=800&q=80",
]
COMMERCIAL_PHOTOS = [
    "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80",
    "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=800&q=80",
    "https://images.unsplash.com/photo-1604328698692-f76ea9498e76?w=800&q=80",
]
SHORTSTAY_PHOTOS = [
    "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=800&q=80",
    "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&q=80",
    "https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800&q=80",
]
HOLIDAY_PHOTOS = [
    "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
    "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",
]

def _photos_for(prop_type):
    return {
        PropertyType.house: HOUSE_PHOTOS,
        PropertyType.apartment: APARTMENT_PHOTOS,
        PropertyType.land: LAND_PHOTOS,
        PropertyType.office: OFFICE_PHOTOS,
        PropertyType.commercial: COMMERCIAL_PHOTOS,
        PropertyType.warehouse: COMMERCIAL_PHOTOS,
        PropertyType.short_stay: SHORTSTAY_PHOTOS,
        PropertyType.holiday_apt: HOLIDAY_PHOTOS,
    }.get(prop_type, HOUSE_PHOTOS)

# ── Seed property definitions ─────────────────────────────────────────────────
SEED_PROPERTIES = [
    dict(title="Modern 3BR House in Kololo", type=PropertyType.house, status=PropertyStatus.for_rent, price=2500000, district="Kampala", area="Kololo", description="Spacious 3-bedroom house in a serene neighborhood with garden and parking.", exact_location="Plot 14, Acacia Avenue, Kololo, Kampala", bedrooms=3, bathrooms=2, parking_spaces=2, floor_size=180, is_verified=True, listing_package=ListingPackage.featured, has_security=True, has_internet=True, latitude=0.3241, longitude=32.5825),
    dict(title="Executive Apartment – Ntinda", type=PropertyType.apartment, status=PropertyStatus.for_rent, price=1200000, district="Kampala", area="Ntinda", description="2-bedroom executive apartment on 4th floor with city views.", bedrooms=2, bathrooms=2, is_verified=True, listing_package=ListingPackage.premium, has_internet=True, has_security=True, latitude=0.3380, longitude=32.6070),
    dict(title="50x100 Plot – Wakiso", type=PropertyType.land, status=PropertyStatus.for_sale, price=85000000, district="Wakiso", area="Gayaza Road", description="Prime mailo land 50×100 ft, ready title, near tarmac road.", plot_size=5000, listing_package=ListingPackage.basic, latitude=0.4100, longitude=32.6200),
    dict(title="5BR Villa with Pool – Muyenga", type=PropertyType.house, status=PropertyStatus.for_sale, price=650000000, district="Kampala", area="Muyenga", description="Luxury 5-bed villa with private pool, gym, and panoramic views of Lake Victoria.", bedrooms=5, bathrooms=4, parking_spaces=4, floor_size=450, is_verified=True, listing_package=ListingPackage.featured, has_security=True, has_furnishing=True, has_internet=True, has_swimming_pool=True, latitude=0.2950, longitude=32.6030),
    dict(title="Office Space – Nakasero", type=PropertyType.office, status=PropertyStatus.for_lease, price=3500000, district="Kampala", area="Nakasero", description="Grade A office space, 200 sqm, fully fitted, prime business district.", floor_size=200, is_verified=True, listing_package=ListingPackage.premium, has_internet=True, has_security=True, latitude=0.3160, longitude=32.5780),
    dict(title="Luxury Short-Stay – Kololo Hill", type=PropertyType.short_stay, status=PropertyStatus.for_rent, price=120000, district="Kampala", area="Kololo", description="Stunning 2-bedroom short-stay in the heart of Kololo.", bedrooms=2, bathrooms=2, floor_size=110, is_verified=True, listing_package=ListingPackage.featured, has_furnishing=True, has_internet=True, has_security=True, latitude=0.3250, longitude=32.5830, is_short_stay=True, price_per_night=120000, max_guests=4, min_nights=1, cleaning_fee=30000, rating=4.9, review_count=87),
    dict(title="Modern Studio – Ntinda", type=PropertyType.short_stay, status=PropertyStatus.for_rent, price=75000, district="Kampala", area="Ntinda", description="Cozy self-contained studio for solo travellers or couples.", bedrooms=1, bathrooms=1, floor_size=45, is_verified=True, listing_package=ListingPackage.premium, has_furnishing=True, has_internet=True, latitude=0.3390, longitude=32.6080, is_short_stay=True, price_per_night=75000, max_guests=2, min_nights=1, cleaning_fee=20000, rating=4.7, review_count=53),
    dict(title="Holiday Cottage – Entebbe", type=PropertyType.holiday_apt, status=PropertyStatus.for_rent, price=350000, district="Wakiso", area="Entebbe", description="Charming lakeshore cottage near Entebbe International Airport.", bedrooms=3, bathrooms=2, floor_size=140, is_verified=True, listing_package=ListingPackage.featured, has_furnishing=True, has_internet=True, has_swimming_pool=True, latitude=0.0539, longitude=32.4635, is_short_stay=True, price_per_night=350000, max_guests=6, min_nights=2, cleaning_fee=70000, rating=5.0, review_count=29),
    dict(title="Luxury Penthouse – Naguru", type=PropertyType.apartment, status=PropertyStatus.for_rent, price=4500000, district="Kampala", area="Naguru", description="Top-floor penthouse with rooftop terrace and city skyline views.", bedrooms=3, bathrooms=3, floor_size=220, is_verified=True, listing_package=ListingPackage.premium, has_security=True, has_internet=True, has_furnishing=True, latitude=0.3310, longitude=32.5990),
    dict(title="Studio – Makerere Hill", type=PropertyType.apartment, status=PropertyStatus.for_rent, price=450000, district="Kampala", area="Makerere", description="Affordable self-contained studio, walking distance to Makerere University.", bedrooms=1, bathrooms=1, floor_size=28, listing_package=ListingPackage.basic, has_internet=True, latitude=0.3340, longitude=32.5700),
    dict(title="100x100 Mailo Land – Entebbe Rd", type=PropertyType.land, status=PropertyStatus.for_sale, price=220000000, district="Wakiso", area="Entebbe Road", description="Corner plot with road frontage, ideal for commercial development.", plot_size=10000, is_verified=True, listing_package=ListingPackage.featured, latitude=0.2800, longitude=32.5500),
    dict(title="Shop Space – Kikuubo", type=PropertyType.commercial, status=PropertyStatus.for_lease, price=800000, district="Kampala", area="Kikuubo", description="Prime ground-floor retail space in Uganda's busiest trading hub.", floor_size=40, is_verified=True, listing_package=ListingPackage.basic, latitude=0.3139, longitude=32.5800),
    dict(title="Luxury Airbnb – Kololo Hill", type=PropertyType.short_stay, status=PropertyStatus.for_rent, price=180000, district="Kampala", area="Kololo", description="Premium Airbnb with infinity pool, fully staffed, city views.", bedrooms=3, bathrooms=3, floor_size=200, is_verified=True, listing_package=ListingPackage.featured, has_furnishing=True, has_internet=True, has_security=True, has_swimming_pool=True, latitude=0.3255, longitude=32.5835, is_short_stay=True, price_per_night=180000, max_guests=6, min_nights=1, cleaning_fee=50000, rating=4.8, review_count=112),
    dict(title="Modern Airbnb Studio – Ntinda", type=PropertyType.short_stay, status=PropertyStatus.for_rent, price=65000, district="Kampala", area="Ntinda", description="Minimalist studio with fast WiFi, perfect for business travellers.", bedrooms=1, bathrooms=1, floor_size=38, is_verified=True, listing_package=ListingPackage.basic, has_furnishing=True, has_internet=True, latitude=0.3395, longitude=32.6085, is_short_stay=True, price_per_night=65000, max_guests=2, min_nights=1, cleaning_fee=15000, rating=4.6, review_count=34),
    dict(title="Holiday Apartment – Munyonyo", type=PropertyType.holiday_apt, status=PropertyStatus.for_rent, price=280000, district="Kampala", area="Munyonyo", description="Lakeside holiday apartment with private beach access on Lake Victoria.", bedrooms=2, bathrooms=2, floor_size=95, is_verified=True, listing_package=ListingPackage.premium, has_furnishing=True, has_internet=True, latitude=0.2720, longitude=32.5980, is_short_stay=True, price_per_night=280000, max_guests=4, min_nights=2, cleaning_fee=40000, rating=4.9, review_count=67),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # ── Users ──────────────────────────────────────────────────────────────
        existing = await db.execute(select(User).where(User.email == "admin@wamato.ug"))
        admin = existing.scalar_one_or_none()
        if not admin:
            admin = User(full_name="Wamato Admin", email="admin@wamato.ug",
                         hashed_password=hash_password("Admin@1234!"),
                         role=UserRole.admin, is_verified=True)
            db.add(admin)
            await db.flush()

        existing2 = await db.execute(select(User).where(User.email == "demo@wamato.ug"))
        owner = existing2.scalar_one_or_none()
        if not owner:
            owner = User(full_name="Demo Owner", email="demo@wamato.ug",
                         hashed_password=hash_password("Demo@1234"),
                         phone="+256700000000")
            db.add(owner)
            await db.flush()

        # ── Wipe old properties and start clean ────────────────────────────────
        await db.execute(delete(PropertyPhoto))
        await db.execute(delete(Property))
        await db.flush()

        # ── Re-seed with photos ────────────────────────────────────────────────
        added = 0
        for p in SEED_PROPERTIES:
            prop_type = p['type']
            prop = Property(owner_id=owner.id, **p)
            db.add(prop)
            await db.flush()

            photos = _photos_for(prop_type)
            for i, url in enumerate(photos):
                db.add(PropertyPhoto(
                    property_id=prop.id,
                    url=url,
                    order=i,
                    is_cover=(i == 0),
                ))
            added += 1

        await db.commit()
        print(f"Seeded {added} properties (each with {len(HOUSE_PHOTOS)} photos) + admin + demo owner.")


if __name__ == "__main__":
    asyncio.run(seed())
