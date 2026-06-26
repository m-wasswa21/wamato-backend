"""
Seed the database with sample Wamato properties (mirrors Flutter sample data).
Run: python scripts/seed.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.property import Property, PropertyPhoto, PropertyType, PropertyStatus, ListingPackage


SEED_PROPERTIES = [
    dict(title="Modern 3BR House in Kololo", type=PropertyType.house, status=PropertyStatus.for_rent, price=2500000, district="Kampala", area="Kololo", description="Spacious 3-bedroom house in a serene neighborhood with garden and parking.", exact_location="Plot 14, Acacia Avenue, Kololo, Kampala", bedrooms=3, bathrooms=2, parking_spaces=2, floor_size=180, is_verified=True, listing_package=ListingPackage.featured, has_security=True, has_internet=True, latitude=0.3241, longitude=32.5825),
    dict(title="Executive Apartment – Ntinda", type=PropertyType.apartment, status=PropertyStatus.for_rent, price=1200000, district="Kampala", area="Ntinda", description="2-bedroom executive apartment on 4th floor with city views.", bedrooms=2, bathrooms=2, is_verified=True, listing_package=ListingPackage.premium, has_internet=True, has_security=True, latitude=0.3380, longitude=32.6070),
    dict(title="50x100 Plot – Wakiso", type=PropertyType.land, status=PropertyStatus.for_sale, price=85000000, district="Wakiso", area="Gayaza Road", description="Prime mailo land 50×100 ft, ready title, near tarmac road.", plot_size=5000, listing_package=ListingPackage.basic, latitude=0.4100, longitude=32.6200),
    dict(title="5BR Villa with Pool – Muyenga", type=PropertyType.house, status=PropertyStatus.for_sale, price=650000000, district="Kampala", area="Muyenga", description="Luxury 5-bed villa with private pool, gym, and panoramic views of Lake Victoria.", bedrooms=5, bathrooms=4, parking_spaces=4, floor_size=450, is_verified=True, listing_package=ListingPackage.featured, has_security=True, has_furnishing=True, has_internet=True, has_swimming_pool=True, latitude=0.2950, longitude=32.6030),
    dict(title="Office Space – Nakasero", type=PropertyType.office, status=PropertyStatus.for_lease, price=3500000, district="Kampala", area="Nakasero", description="Grade A office space, 200 sqm, fully fitted, prime business district.", floor_size=200, is_verified=True, listing_package=ListingPackage.premium, has_internet=True, has_security=True, latitude=0.3160, longitude=32.5780),
    dict(title="Luxury Short-Stay – Kololo Hill", type=PropertyType.short_stay, status=PropertyStatus.for_rent, price=120000, district="Kampala", area="Kololo", description="Stunning 2-bedroom short-stay in the heart of Kololo.", bedrooms=2, bathrooms=2, floor_size=110, is_verified=True, listing_package=ListingPackage.featured, has_furnishing=True, has_internet=True, has_security=True, latitude=0.3250, longitude=32.5830, is_short_stay=True, price_per_night=120000, max_guests=4, min_nights=1, cleaning_fee=30000, rating=4.9, review_count=87),
    dict(title="Modern Studio – Ntinda", type=PropertyType.short_stay, status=PropertyStatus.for_rent, price=75000, district="Kampala", area="Ntinda", description="Cozy self-contained studio for solo travellers or couples.", bedrooms=1, bathrooms=1, floor_size=45, is_verified=True, listing_package=ListingPackage.premium, has_furnishing=True, has_internet=True, latitude=0.3390, longitude=32.6080, is_short_stay=True, price_per_night=75000, max_guests=2, min_nights=1, cleaning_fee=20000, rating=4.7, review_count=53),
    dict(title="Holiday Cottage – Entebbe", type=PropertyType.holiday_apt, status=PropertyStatus.for_rent, price=350000, district="Wakiso", area="Entebbe", description="Charming lakeshore cottage near Entebbe International Airport.", bedrooms=3, bathrooms=2, floor_size=140, is_verified=True, listing_package=ListingPackage.featured, has_furnishing=True, has_internet=True, has_swimming_pool=True, latitude=0.0539, longitude=32.4635, is_short_stay=True, price_per_night=350000, max_guests=6, min_nights=2, cleaning_fee=70000, rating=5.0, review_count=29),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Admin user
        from sqlalchemy import select
        existing = await db.execute(select(User).where(User.email == "admin@wamato.ug"))
        admin = existing.scalar_one_or_none()
        if not admin:
            admin = User(
                full_name="Wamato Admin",
                email="admin@wamato.ug",
                hashed_password=hash_password("Admin@1234!"),
                role=UserRole.admin,
                is_verified=True,
            )
            db.add(admin)
            await db.flush()

        # Demo owner
        existing2 = await db.execute(select(User).where(User.email == "demo@wamato.ug"))
        owner = existing2.scalar_one_or_none()
        if not owner:
            owner = User(
                full_name="Demo Owner",
                email="demo@wamato.ug",
                hashed_password=hash_password("Demo@1234"),
                phone="+256700000000",
            )
            db.add(owner)
            await db.flush()

        # Properties
        for p in SEED_PROPERTIES:
            prop = Property(owner_id=owner.id, **p)
            db.add(prop)

        await db.commit()
        print(f"Seeded {len(SEED_PROPERTIES)} properties + admin + demo owner.")


if __name__ == "__main__":
    asyncio.run(seed())
