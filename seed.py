"""
Seed script — populates the Wamato database with sample properties.
Run inside the Docker container:
  docker exec -it wamato-backend python seed.py
"""
import asyncio
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.property import Property, PropertyStatus, PropertyType, ListingPackage, PropertyPhoto

# ── Sample image URLs (Unsplash) ──────────────────────────────────────────────
IMGS = {
    "house":      "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
    "apartment":  "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800",
    "villa":      "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800",
    "modern":     "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800",
    "land":       "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=800",
    "office":     "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
    "airbnb":     "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800",
    "holiday":    "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=800",
    "warehouse":  "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800",
    "commercial": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800",
}

SEED_PROPERTIES = [
    # ── Houses ────────────────────────────────────────────────────────────────
    dict(
        title="Modern 3BR House in Kololo",
        type=PropertyType.house, status=PropertyStatus.for_rent,
        price=2500000, district="Kampala", area="Kololo",
        description="Spacious 3-bedroom house in a serene neighborhood with garden and parking.",
        exact_location="Plot 14, Acacia Avenue, Kololo, Kampala",
        owner_phone="+256701234567", owner_whatsapp="+256701234567",
        bedrooms=3, bathrooms=2, parking_spaces=2, floor_size=180,
        has_security=True, has_internet=True,
        latitude=0.3241, longitude=32.5825,
        listing_package=ListingPackage.featured, is_verified=True, is_featured=True,
        photo=IMGS["house"],
    ),
    dict(
        title="4BR Townhouse – Naguru",
        type=PropertyType.house, status=PropertyStatus.for_rent,
        price=3200000, district="Kampala", area="Naguru",
        description="Newly built 4-bedroom townhouse in a gated community with garden.",
        exact_location="Naguru Hill, Plot 5, Kampala",
        owner_phone="+256712890123", owner_whatsapp="+256712890123",
        bedrooms=4, bathrooms=3, parking_spaces=2, floor_size=250,
        has_security=True, has_internet=True,
        latitude=0.3300, longitude=32.6050,
        listing_package=ListingPackage.premium, is_verified=True,
        photo=IMGS["modern"],
    ),
    dict(
        title="5BR Villa with Pool – Muyenga",
        type=PropertyType.house, status=PropertyStatus.for_sale,
        price=650000000, district="Kampala", area="Muyenga",
        description="Luxury 5-bed villa with private pool, gym, and panoramic views of Lake Victoria.",
        exact_location="Plot 8, Tank Hill Road, Muyenga, Kampala",
        owner_phone="+256701567890", owner_whatsapp="+256701567890",
        bedrooms=5, bathrooms=4, parking_spaces=4, floor_size=450,
        has_security=True, has_furnishing=True, has_internet=True, has_swimming_pool=True,
        latitude=0.2950, longitude=32.6030,
        listing_package=ListingPackage.featured, is_verified=True, is_featured=True,
        photo=IMGS["villa"],
    ),
    dict(
        title="2BR House – Kira Town",
        type=PropertyType.house, status=PropertyStatus.for_rent,
        price=900000, district="Wakiso", area="Kira",
        description="Affordable 2-bedroom house in quiet Kira estate.",
        exact_location="Kira Town Council, Wakiso",
        owner_phone="+256703000003", owner_whatsapp="+256703000003",
        bedrooms=2, bathrooms=1, parking_spaces=1, floor_size=90,
        latitude=0.3630, longitude=32.6390,
        listing_package=ListingPackage.basic,
        photo=IMGS["house"],
    ),
    dict(
        title="5BR Mansion – Lubowa",
        type=PropertyType.house, status=PropertyStatus.for_sale,
        price=1200000000, district="Wakiso", area="Lubowa",
        description="Grand 5-bedroom mansion in Lubowa Estate with landscaped gardens.",
        exact_location="Lubowa Estate, Entebbe Road, Wakiso",
        owner_phone="+256707000007", owner_whatsapp="+256707000007",
        bedrooms=5, bathrooms=5, parking_spaces=6, floor_size=600, plot_size=5000,
        has_security=True, has_furnishing=True, has_internet=True, has_swimming_pool=True,
        latitude=0.2490, longitude=32.5660,
        listing_package=ListingPackage.featured, is_verified=True, is_featured=True,
        photo=IMGS["villa"],
    ),

    # ── Apartments ────────────────────────────────────────────────────────────
    dict(
        title="Executive Apartment – Ntinda",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=1200000, district="Kampala", area="Ntinda",
        description="2-bedroom executive apartment on 4th floor with city views.",
        exact_location="Ntinda Shopping Mall Road, Kampala",
        owner_phone="+256772345678", owner_whatsapp="+256772345678",
        bedrooms=2, bathrooms=2, floor_size=120,
        has_internet=True, has_security=True,
        latitude=0.3380, longitude=32.6070,
        listing_package=ListingPackage.premium, is_verified=True,
        photo=IMGS["apartment"],
    ),
    dict(
        title="Studio Apartment – Bukoto",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=600000, district="Kampala", area="Bukoto",
        description="Cozy furnished studio, great for young professionals, close to amenities.",
        exact_location="Bukoto Street, Plot 22, Kampala",
        owner_phone="+256789789012", owner_whatsapp="+256789789012",
        bedrooms=1, bathrooms=1,
        has_furnishing=True,
        latitude=0.3370, longitude=32.5950,
        listing_package=ListingPackage.basic,
        photo=IMGS["apartment"],
    ),
    dict(
        title="3BR Apartment – Bugolobi",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=1800000, district="Kampala", area="Bugolobi",
        description="Modern apartment with balcony and lake views.",
        exact_location="Bugolobi Flats, Block C, Kampala",
        owner_phone="+256701000001", owner_whatsapp="+256701000001",
        bedrooms=3, bathrooms=2, floor_size=140,
        has_internet=True, has_security=True,
        latitude=0.3050, longitude=32.6120,
        listing_package=ListingPackage.premium, is_verified=True,
        photo=IMGS["modern"],
    ),
    dict(
        title="Luxury Penthouse – Naguru",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=6500000, district="Kampala", area="Naguru",
        description="Top-floor penthouse with 360° city views, fully serviced.",
        exact_location="Skyz Hotel Road, Naguru, Kampala",
        owner_phone="+256704000004", owner_whatsapp="+256704000004",
        bedrooms=4, bathrooms=3, parking_spaces=2, floor_size=320,
        has_security=True, has_furnishing=True, has_internet=True, has_swimming_pool=True,
        latitude=0.3268, longitude=32.6015,
        listing_package=ListingPackage.featured, is_verified=True, is_featured=True,
        photo=IMGS["modern"],
    ),
    dict(
        title="Studio – Makerere Hill",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=450000, district="Kampala", area="Makerere",
        description="Affordable studio near Makerere University, ideal for students.",
        exact_location="Makerere Hill Road, Kampala",
        owner_phone="+256708000008", owner_whatsapp="+256708000008",
        bedrooms=1, bathrooms=1, has_furnishing=True,
        latitude=0.3354, longitude=32.5685,
        listing_package=ListingPackage.basic,
        photo=IMGS["apartment"],
    ),

    # ── Land ──────────────────────────────────────────────────────────────────
    dict(
        title="50x100 Plot – Wakiso",
        type=PropertyType.land, status=PropertyStatus.for_sale,
        price=85000000, district="Wakiso", area="Gayaza Road",
        description="Prime mailo land 50×100 ft, ready title, near tarmac road.",
        exact_location="Gayaza Road, Km 12, Wakiso",
        owner_phone="+256752456789", owner_whatsapp="+256752456789",
        plot_size=5000,
        latitude=0.4100, longitude=32.6200,
        listing_package=ListingPackage.basic,
        photo=IMGS["land"],
    ),
    dict(
        title="100x100 Mailo Land – Entebbe Rd",
        type=PropertyType.land, status=PropertyStatus.for_sale,
        price=220000000, district="Wakiso", area="Entebbe Road",
        description="Large corner plot on Entebbe Road with ready title.",
        exact_location="Km 8, Entebbe Road, Wakiso",
        owner_phone="+256705000005", owner_whatsapp="+256705000005",
        plot_size=10000,
        latitude=0.2620, longitude=32.5390,
        listing_package=ListingPackage.premium, is_verified=True,
        photo=IMGS["land"],
    ),

    # ── Office / Commercial / Warehouse ───────────────────────────────────────
    dict(
        title="Office Space – Nakasero",
        type=PropertyType.office, status=PropertyStatus.for_lease,
        price=3500000, district="Kampala", area="Nakasero",
        description="Grade A office space, 200 sqm, fully fitted, prime business district.",
        exact_location="Nakasero Road, Plot 3, Kampala",
        owner_phone="+256700678901", owner_whatsapp="+256700678901",
        floor_size=200, has_internet=True, has_security=True,
        latitude=0.3160, longitude=32.5780,
        listing_package=ListingPackage.premium, is_verified=True,
        photo=IMGS["office"],
    ),
    dict(
        title="Shop Space – Kikuubo",
        type=PropertyType.commercial, status=PropertyStatus.for_rent,
        price=2200000, district="Kampala", area="Kikuubo",
        description="Ground-floor shop in Kampala's busiest trading hub.",
        exact_location="Kikuubo Lane, Kampala CBD",
        owner_phone="+256706000006", owner_whatsapp="+256706000006",
        floor_size=45, has_security=True,
        latitude=0.3136, longitude=32.5814,
        listing_package=ListingPackage.basic, is_verified=True,
        photo=IMGS["commercial"],
    ),
    dict(
        title="Commercial Warehouse – Nalukolongo",
        type=PropertyType.warehouse, status=PropertyStatus.for_lease,
        price=8000000, district="Kampala", area="Nalukolongo",
        description="Large industrial warehouse, 1,000 sqm, near industrial area.",
        exact_location="Nalukolongo Industrial Area, Kampala",
        owner_phone="+256702000002", owner_whatsapp="+256702000002",
        floor_size=1000, has_security=True,
        latitude=0.2980, longitude=32.5500,
        listing_package=ListingPackage.basic, is_verified=True,
        photo=IMGS["warehouse"],
    ),

    # ── Short Stays (Airbnb) ──────────────────────────────────────────────────
    dict(
        title="Luxury Airbnb – Kololo Hill",
        type=PropertyType.short_stay, status=PropertyStatus.for_rent,
        price=120000, district="Kampala", area="Kololo",
        description="Stunning 2-bedroom Airbnb in the heart of Kololo. Fully furnished with rooftop terrace, fast Wi-Fi and city views. Perfect for business or leisure stays.",
        exact_location="Kololo Hill Drive, Kampala",
        owner_phone="+256701100001", owner_whatsapp="+256701100001",
        bedrooms=2, bathrooms=2, floor_size=110,
        has_furnishing=True, has_internet=True, has_security=True,
        latitude=0.3250, longitude=32.5830,
        listing_package=ListingPackage.featured, is_verified=True, is_featured=True,
        is_short_stay=True, price_per_night=120000, max_guests=4, min_nights=1, cleaning_fee=30000,
        rating=4.9, review_count=87,
        photo=IMGS["airbnb"],
    ),
    dict(
        title="Modern Airbnb Studio – Ntinda",
        type=PropertyType.short_stay, status=PropertyStatus.for_rent,
        price=75000, district="Kampala", area="Ntinda",
        description="Cozy self-contained studio for solo travellers or couples. Has a kitchenette, smart TV and secure parking.",
        exact_location="Ntinda Road, Kampala",
        owner_phone="+256702100002", owner_whatsapp="+256702100002",
        bedrooms=1, bathrooms=1, floor_size=45,
        has_furnishing=True, has_internet=True,
        latitude=0.3390, longitude=32.6080,
        listing_package=ListingPackage.premium, is_verified=True,
        is_short_stay=True, price_per_night=75000, max_guests=2, min_nights=1, cleaning_fee=20000,
        rating=4.7, review_count=53,
        photo=IMGS["airbnb"],
    ),
    dict(
        title="Airbnb Villa with Pool – Muyenga",
        type=PropertyType.short_stay, status=PropertyStatus.for_rent,
        price=280000, district="Kampala", area="Muyenga",
        description="4-bedroom villa with private pool and lake views. Ideal for groups, family reunions or corporate retreats.",
        exact_location="Tank Hill Road, Muyenga, Kampala",
        owner_phone="+256703100003", owner_whatsapp="+256703100003",
        bedrooms=4, bathrooms=3, floor_size=300,
        has_furnishing=True, has_internet=True, has_security=True, has_swimming_pool=True,
        latitude=0.2960, longitude=32.6010,
        listing_package=ListingPackage.featured, is_verified=True, is_featured=True,
        is_short_stay=True, price_per_night=280000, max_guests=8, min_nights=2, cleaning_fee=60000,
        rating=4.8, review_count=42,
        photo=IMGS["villa"],
    ),

    # ── Holiday Apartments ────────────────────────────────────────────────────
    dict(
        title="Holiday Apartment – Munyonyo",
        type=PropertyType.holiday_apt, status=PropertyStatus.for_rent,
        price=180000, district="Kampala", area="Munyonyo",
        description="Serene 3-bed holiday apartment steps from Lake Victoria. Wake up to lake breeze, enjoy sunset from your balcony.",
        exact_location="Munyonyo Commonwealth Resort Road, Kampala",
        owner_phone="+256704100004", owner_whatsapp="+256704100004",
        bedrooms=3, bathrooms=2, floor_size=160,
        has_furnishing=True, has_internet=True, has_security=True,
        latitude=0.2710, longitude=32.5960,
        listing_package=ListingPackage.featured, is_verified=True, is_featured=True,
        is_short_stay=True, price_per_night=180000, max_guests=6, min_nights=2, cleaning_fee=40000,
        rating=4.9, review_count=61,
        photo=IMGS["holiday"],
    ),
    dict(
        title="Holiday Cottage – Entebbe",
        type=PropertyType.holiday_apt, status=PropertyStatus.for_rent,
        price=350000, district="Wakiso", area="Entebbe",
        description="Charming lakeshore cottage near Entebbe International Airport and botanical gardens. Perfect weekend getaway.",
        exact_location="Lakeshore Drive, Entebbe",
        owner_phone="+256705100005", owner_whatsapp="+256705100005",
        bedrooms=3, bathrooms=2, floor_size=140,
        has_furnishing=True, has_internet=True, has_swimming_pool=True,
        latitude=0.0539, longitude=32.4635,
        listing_package=ListingPackage.featured, is_verified=True, is_featured=True,
        is_short_stay=True, price_per_night=350000, max_guests=6, min_nights=2, cleaning_fee=70000,
        rating=5.0, review_count=29,
        photo=IMGS["holiday"],
    ),
    dict(
        title="Holiday Suite – Naguru",
        type=PropertyType.holiday_apt, status=PropertyStatus.for_rent,
        price=150000, district="Kampala", area="Naguru",
        description="Stylish 2-bedroom holiday suite in quiet Naguru, close to restaurants and Skyz Hotel.",
        exact_location="Naguru Hill, Kampala",
        owner_phone="+256706100006", owner_whatsapp="+256706100006",
        bedrooms=2, bathrooms=1, floor_size=95,
        has_furnishing=True, has_internet=True,
        latitude=0.3280, longitude=32.6020,
        listing_package=ListingPackage.premium,
        is_short_stay=True, price_per_night=150000, max_guests=4, min_nights=1, cleaning_fee=25000,
        rating=4.6, review_count=18,
        photo=IMGS["holiday"],
    ),
]


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # ── Create seed agent user ─────────────────────────────────────────────
        result = await session.execute(
            select(User).where(User.email == "agent@wamato.ug")
        )
        agent = result.scalar_one_or_none()

        if not agent:
            agent = User(
                id=uuid.uuid4(),
                full_name="Wamato Demo Agent",
                email="agent@wamato.ug",
                hashed_password=hash_password("Wamato2026!"),
                role=UserRole.agent,
                phone="+256700000000",
                whatsapp="+256700000000",
                is_active=True,
                is_verified=True,
            )
            session.add(agent)
            await session.flush()
            print(f"Created agent: {agent.email}")
        else:
            print(f"Agent already exists: {agent.email}")

        # ── Check if properties already seeded ────────────────────────────────
        from sqlalchemy import func, select as sa_select
        count_result = await session.execute(
            sa_select(func.count()).select_from(Property)
        )
        count = count_result.scalar()
        if count and count > 0:
            print(f"Database already has {count} properties — skipping seed.")
            await engine.dispose()
            return

        # ── Insert properties ─────────────────────────────────────────────────
        for i, data in enumerate(SEED_PROPERTIES):
            photo_url = data.pop("photo")
            prop = Property(
                id=uuid.uuid4(),
                owner_id=agent.id,
                is_active=True,
                view_count=0,
                **{k: v for k, v in data.items()},
            )
            session.add(prop)
            await session.flush()

            # Add cover photo
            photo = PropertyPhoto(
                id=uuid.uuid4(),
                property_id=prop.id,
                url=photo_url,
                is_cover=True,
                order=0,
            )
            session.add(photo)
            print(f"  [{i+1}/{len(SEED_PROPERTIES)}] {prop.title}")

        await session.commit()
        print(f"\nSeeded {len(SEED_PROPERTIES)} properties successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
