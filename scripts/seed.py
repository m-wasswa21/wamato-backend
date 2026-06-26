"""
Seed the database with beautiful Wamato properties + curated Unsplash photos.
Run: python scripts/seed.py   — safe to run multiple times (idempotent).
"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.property import (
    Property, PropertyPhoto, PropertyType,
    PropertyStatus, ListingPackage,
)

# ─────────────────────────────────────────────────────────────────────────────
# Each property gets its own curated photo list [cover, photo2, photo3, ...]
# ─────────────────────────────────────────────────────────────────────────────
SEED_PROPERTIES = [

    # ── HOUSES ───────────────────────────────────────────────────────────────
    dict(
        title="Modern 3BR House – Kololo",
        type=PropertyType.house, status=PropertyStatus.for_rent,
        price=2_500_000, district="Kampala", area="Kololo",
        description="Spacious 3-bedroom house in a serene neighborhood with manicured garden and double parking. Brand new fittings, 24/7 security and fibre internet.",
        exact_location="Plot 14, Acacia Avenue, Kololo, Kampala",
        bedrooms=3, bathrooms=2, parking_spaces=2, floor_size=180,
        is_verified=True, listing_package=ListingPackage.featured,
        has_security=True, has_internet=True, latitude=0.3241, longitude=32.5825,
        photos=[
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=900&q=85",
            "https://images.unsplash.com/photo-1600573472592-401b489a3cdc?w=900&q=85",
            "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=900&q=85",
            "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=900&q=85",
        ]
    ),
    dict(
        title="5BR Luxury Villa – Muyenga",
        type=PropertyType.house, status=PropertyStatus.for_sale,
        price=650_000_000, district="Kampala", area="Muyenga",
        description="Breathtaking 5-bedroom villa on Muyenga Hill with private infinity pool, gym, cinema room and panoramic views of Lake Victoria.",
        bedrooms=5, bathrooms=4, parking_spaces=4, floor_size=450,
        is_verified=True, listing_package=ListingPackage.featured,
        has_security=True, has_furnishing=True, has_internet=True,
        has_swimming_pool=True, latitude=0.2950, longitude=32.6030,
        photos=[
            "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=900&q=85",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=900&q=85",
            "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=900&q=85",
            "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=900&q=85",
        ]
    ),
    dict(
        title="4BR Family Home – Ntinda",
        type=PropertyType.house, status=PropertyStatus.for_rent,
        price=1_800_000, district="Kampala", area="Ntinda",
        description="Well-maintained 4-bedroom family home with large compound, servants' quarters and backup generator. Quiet estate, close to schools.",
        bedrooms=4, bathrooms=3, parking_spaces=2, floor_size=250,
        is_verified=True, listing_package=ListingPackage.premium,
        has_security=True, has_internet=True, has_generator=True,
        latitude=0.3380, longitude=32.6070,
        photos=[
            "https://images.unsplash.com/photo-1570129477492-45c003dc5e4f?w=900&q=85",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=900&q=85",
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=900&q=85",
        ]
    ),
    dict(
        title="3BR Bungalow – Bukoto",
        type=PropertyType.house, status=PropertyStatus.for_rent,
        price=1_400_000, district="Kampala", area="Bukoto",
        description="Charming bungalow with tropical garden, open-plan kitchen and covered veranda. Perfect for expat families.",
        bedrooms=3, bathrooms=2, parking_spaces=1, floor_size=160,
        listing_package=ListingPackage.basic,
        has_internet=True, latitude=0.3300, longitude=32.5950,
        photos=[
            "https://images.unsplash.com/photo-1592595896551-12b371d546d5?w=900&q=85",
            "https://images.unsplash.com/photo-1575517111839-3a3843ee7f5d?w=900&q=85",
            "https://images.unsplash.com/photo-1449844908441-8829872d2607?w=900&q=85",
        ]
    ),
    dict(
        title="6BR Mansion – Naguru",
        type=PropertyType.house, status=PropertyStatus.for_sale,
        price=1_200_000_000, district="Kampala", area="Naguru",
        description="Grand 6-bedroom mansion on 1 acre with swimming pool, servants' quarters, 3-car garage and state-of-the-art security system.",
        bedrooms=6, bathrooms=5, parking_spaces=4, floor_size=600,
        is_verified=True, listing_package=ListingPackage.featured,
        has_security=True, has_furnishing=True, has_internet=True,
        has_swimming_pool=True, has_generator=True, latitude=0.3310, longitude=32.5990,
        photos=[
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=900&q=85",
            "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=900&q=85",
            "https://images.unsplash.com/photo-1599809275671-b5942cabc7a2?w=900&q=85",
            "https://images.unsplash.com/photo-1628744448840-55bdb2497bd4?w=900&q=85",
        ]
    ),
    dict(
        title="3BR Town House – Kira",
        type=PropertyType.house, status=PropertyStatus.for_sale,
        price=280_000_000, district="Wakiso", area="Kira",
        description="Brand new 3-bedroom town house in a gated community, with modern finishes, solar water heater and fibre internet.",
        bedrooms=3, bathrooms=2, parking_spaces=1, floor_size=140,
        is_verified=True, listing_package=ListingPackage.premium,
        has_security=True, has_internet=True, has_solar=True,
        latitude=0.3600, longitude=32.6400,
        photos=[
            "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=900&q=85",
            "https://images.unsplash.com/photo-1558981285-6f0c94958bb6?w=900&q=85",
            "https://images.unsplash.com/photo-1523217582562-09d0def993a6?w=900&q=85",
        ]
    ),

    # ── APARTMENTS ────────────────────────────────────────────────────────────
    dict(
        title="Executive 2BR Apartment – Ntinda",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=1_200_000, district="Kampala", area="Ntinda",
        description="2-bedroom executive apartment on the 4th floor with balcony city views, modern kitchen and dedicated parking bay.",
        bedrooms=2, bathrooms=2, floor_size=95,
        is_verified=True, listing_package=ListingPackage.premium,
        has_internet=True, has_security=True, latitude=0.3385, longitude=32.6075,
        photos=[
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900&q=85",
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=900&q=85",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=900&q=85",
        ]
    ),
    dict(
        title="Luxury Penthouse – Naguru",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=4_500_000, district="Kampala", area="Naguru",
        description="Top-floor penthouse with wraparound rooftop terrace, Jacuzzi, city skyline views and fully equipped chef's kitchen.",
        bedrooms=3, bathrooms=3, floor_size=220,
        is_verified=True, listing_package=ListingPackage.featured,
        has_security=True, has_internet=True, has_furnishing=True,
        latitude=0.3315, longitude=32.5995,
        photos=[
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=900&q=85",
            "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=900&q=85",
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=900&q=85",
            "https://images.unsplash.com/photo-1631679706909-1844bbd07221?w=900&q=85",
        ]
    ),
    dict(
        title="Studio Apartment – Makerere",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=450_000, district="Kampala", area="Makerere",
        description="Cosy self-contained studio with fast fibre WiFi, walking distance to Makerere University. Water and security included.",
        bedrooms=1, bathrooms=1, floor_size=28,
        listing_package=ListingPackage.basic, has_internet=True,
        latitude=0.3340, longitude=32.5700,
        photos=[
            "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?w=900&q=85",
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=900&q=85",
            "https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=900&q=85",
        ]
    ),
    dict(
        title="3BR Serviced Apartment – Kololo",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=3_800_000, district="Kampala", area="Kololo",
        description="Fully serviced 3-bedroom apartment with housekeeping, concierge, rooftop pool and gym. Ideal for diplomats and executives.",
        bedrooms=3, bathrooms=3, floor_size=180,
        is_verified=True, listing_package=ListingPackage.featured,
        has_security=True, has_internet=True, has_furnishing=True,
        has_swimming_pool=True, latitude=0.3255, longitude=32.5840,
        photos=[
            "https://images.unsplash.com/photo-1567225557594-88d73e55f2cb?w=900&q=85",
            "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=900&q=85",
            "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=900&q=85",
        ]
    ),
    dict(
        title="1BR Modern Flat – Bukoto",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=700_000, district="Kampala", area="Bukoto",
        description="Bright 1-bedroom flat with open-plan living, modern bathroom and covered parking. Water included in rent.",
        bedrooms=1, bathrooms=1, floor_size=52,
        listing_package=ListingPackage.basic, has_internet=True,
        latitude=0.3295, longitude=32.5960,
        photos=[
            "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=900&q=85",
            "https://images.unsplash.com/photo-1617104678098-de229db51175?w=900&q=85",
            "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=900&q=85",
        ]
    ),
    dict(
        title="2BR Apartment – Muyenga",
        type=PropertyType.apartment, status=PropertyStatus.for_rent,
        price=1_600_000, district="Kampala", area="Muyenga",
        description="Elegant 2-bedroom apartment with lake-view balcony, walk-in closets and underground parking.",
        bedrooms=2, bathrooms=2, floor_size=110,
        is_verified=True, listing_package=ListingPackage.premium,
        has_security=True, has_internet=True, latitude=0.2960, longitude=32.6040,
        photos=[
            "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=900&q=85",
            "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=900&q=85",
            "https://images.unsplash.com/photo-1556912167-f556f1f39fdf?w=900&q=85",
        ]
    ),

    # ── LAND / PLOTS ──────────────────────────────────────────────────────────
    dict(
        title="50×100 Plot – Gayaza Road",
        type=PropertyType.land, status=PropertyStatus.for_sale,
        price=85_000_000, district="Wakiso", area="Gayaza Road",
        description="Prime 50×100 mailo land with ready title deed. Good murram road access, suitable for residential development. Near new tarmac road.",
        plot_size=5_000, listing_package=ListingPackage.basic,
        latitude=0.4100, longitude=32.6200,
        photos=[
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&q=85",
            "https://images.unsplash.com/photo-1625602812206-5ec545ca1231?w=900&q=85",
            "https://images.unsplash.com/photo-1536895058696-a69b1c7ba34f?w=900&q=85",
        ]
    ),
    dict(
        title="100×100 Corner Plot – Entebbe Rd",
        type=PropertyType.land, status=PropertyStatus.for_sale,
        price=220_000_000, district="Wakiso", area="Entebbe Road",
        description="Prime 100×100 ft corner plot with tarmac road frontage. Perfect for commercial or high-density residential. Ready title.",
        plot_size=10_000, is_verified=True, listing_package=ListingPackage.featured,
        latitude=0.2800, longitude=32.5500,
        photos=[
            "https://images.unsplash.com/photo-1465056836041-7f40eb9d2e27?w=900&q=85",
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&q=85",
            "https://images.unsplash.com/photo-1567182406470-d7a4ae0c10f5?w=900&q=85",
        ]
    ),
    dict(
        title="1 Acre Mailo Land – Mukono",
        type=PropertyType.land, status=PropertyStatus.for_sale,
        price=150_000_000, district="Mukono", area="Mukono Town",
        description="1 acre of flat mailo land on main road, fully fenced. Electricity and water on plot. Ideal for school, church or apartments.",
        plot_size=40_000, listing_package=ListingPackage.premium,
        latitude=0.3530, longitude=32.7550,
        photos=[
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&q=85",
            "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=900&q=85",
            "https://images.unsplash.com/photo-1448375240586-882707db888b?w=900&q=85",
        ]
    ),
    dict(
        title="50×100 Residential Plot – Kira",
        type=PropertyType.land, status=PropertyStatus.for_sale,
        price=65_000_000, district="Wakiso", area="Kira",
        description="Affordable 50×100 plot in a fast-developing residential area. All utilities nearby. Good road access.",
        plot_size=5_000, listing_package=ListingPackage.basic,
        latitude=0.3620, longitude=32.6380,
        photos=[
            "https://images.unsplash.com/photo-1425913397330-cf8af2ff40a1?w=900&q=85",
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&q=85",
            "https://images.unsplash.com/photo-1599598425947-5202edd56fda?w=900&q=85",
        ]
    ),

    # ── OFFICES ───────────────────────────────────────────────────────────────
    dict(
        title="Grade A Office – Nakasero",
        type=PropertyType.office, status=PropertyStatus.for_lease,
        price=3_500_000, district="Kampala", area="Nakasero",
        description="200 sqm Grade A fully fitted office space in the heart of Kampala's CBD. Fibre internet, boardroom, reception and secure parking.",
        floor_size=200, is_verified=True, listing_package=ListingPackage.premium,
        has_internet=True, has_security=True, latitude=0.3160, longitude=32.5780,
        photos=[
            "https://images.unsplash.com/photo-1497366216548-37526070297c?w=900&q=85",
            "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=900&q=85",
            "https://images.unsplash.com/photo-1604328698692-f76ea9498e76?w=900&q=85",
        ]
    ),
    dict(
        title="Open-Plan Office – Kampala Road",
        type=PropertyType.office, status=PropertyStatus.for_lease,
        price=5_000_000, district="Kampala", area="Kampala Road",
        description="Modern 350 sqm open-plan office floor with glass partitions, kitchen, 2 boardrooms and rooftop terrace.",
        floor_size=350, is_verified=True, listing_package=ListingPackage.featured,
        has_internet=True, has_security=True, latitude=0.3145, longitude=32.5820,
        photos=[
            "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=900&q=85",
            "https://images.unsplash.com/photo-1497215842964-222b430dc094?w=900&q=85",
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=900&q=85",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=900&q=85",
        ]
    ),
    dict(
        title="Small Office Suite – Bugolobi",
        type=PropertyType.office, status=PropertyStatus.for_lease,
        price=1_200_000, district="Kampala", area="Bugolobi",
        description="Compact 60 sqm private office suite in a quiet business park. Includes 2 parking bays, reception access and backup power.",
        floor_size=60, listing_package=ListingPackage.basic,
        has_internet=True, has_security=True, has_generator=True,
        latitude=0.3070, longitude=32.6100,
        photos=[
            "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=900&q=85",
            "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=900&q=85",
            "https://images.unsplash.com/photo-1598257006626-48b0c252070d?w=900&q=85",
        ]
    ),

    # ── COMMERCIAL ────────────────────────────────────────────────────────────
    dict(
        title="Retail Shop – Kikuubo",
        type=PropertyType.commercial, status=PropertyStatus.for_lease,
        price=800_000, district="Kampala", area="Kikuubo",
        description="Prime ground-floor retail space in Uganda's busiest trading hub. High foot traffic, roller shutter door, storage room.",
        floor_size=40, is_verified=True, listing_package=ListingPackage.basic,
        latitude=0.3139, longitude=32.5800,
        photos=[
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=900&q=85",
            "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=900&q=85",
            "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=900&q=85",
        ]
    ),
    dict(
        title="Showroom & Warehouse – Namanve",
        type=PropertyType.warehouse, status=PropertyStatus.for_lease,
        price=6_000_000, district="Mukono", area="Namanve",
        description="1,500 sqm industrial warehouse with showroom, 3-phase power, loading bays and perimeter wall in Namanve Industrial Park.",
        floor_size=1_500, is_verified=True, listing_package=ListingPackage.premium,
        has_security=True, has_generator=True, latitude=0.3100, longitude=32.7200,
        photos=[
            "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=900&q=85",
            "https://images.unsplash.com/photo-1553413077-190dd305871c?w=900&q=85",
            "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=900&q=85",
        ]
    ),

    # ── SHORT STAY / AIRBNB ───────────────────────────────────────────────────
    dict(
        title="Luxury Short-Stay – Kololo Hill",
        type=PropertyType.short_stay, status=PropertyStatus.for_rent,
        price=120_000, district="Kampala", area="Kololo",
        description="Stunning 2-bedroom short-stay in the heart of Kololo with private pool, chef on request and Netflix-equipped lounge.",
        bedrooms=2, bathrooms=2, floor_size=110,
        is_verified=True, listing_package=ListingPackage.featured,
        has_furnishing=True, has_internet=True, has_security=True,
        has_swimming_pool=True, latitude=0.3250, longitude=32.5830,
        is_short_stay=True, price_per_night=120_000, max_guests=4,
        min_nights=1, cleaning_fee=30_000, rating=4.9, review_count=87,
        photos=[
            "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=900&q=85",
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=900&q=85",
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=900&q=85",
            "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=900&q=85",
        ]
    ),
    dict(
        title="Cosy Airbnb Studio – Ntinda",
        type=PropertyType.short_stay, status=PropertyStatus.for_rent,
        price=75_000, district="Kampala", area="Ntinda",
        description="Modern self-contained studio with king bed, rain shower, fast WiFi and smart TV. Perfect for solo travellers or couples.",
        bedrooms=1, bathrooms=1, floor_size=45,
        is_verified=True, listing_package=ListingPackage.premium,
        has_furnishing=True, has_internet=True, latitude=0.3390, longitude=32.6080,
        is_short_stay=True, price_per_night=75_000, max_guests=2,
        min_nights=1, cleaning_fee=20_000, rating=4.7, review_count=53,
        photos=[
            "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=900&q=85",
            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=900&q=85",
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=900&q=85",
        ]
    ),
    dict(
        title="Premium Airbnb Villa – Muyenga",
        type=PropertyType.short_stay, status=PropertyStatus.for_rent,
        price=180_000, district="Kampala", area="Muyenga",
        description="Fully staffed 3-bedroom Airbnb villa with infinity pool, outdoor BBQ, lake views and daily housekeeping.",
        bedrooms=3, bathrooms=3, floor_size=200,
        is_verified=True, listing_package=ListingPackage.featured,
        has_furnishing=True, has_internet=True, has_security=True,
        has_swimming_pool=True, latitude=0.2955, longitude=32.6035,
        is_short_stay=True, price_per_night=180_000, max_guests=6,
        min_nights=1, cleaning_fee=50_000, rating=4.8, review_count=112,
        photos=[
            "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=900&q=85",
            "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=900&q=85",
            "https://images.unsplash.com/photo-1613977257365-aaae5a9817ff?w=900&q=85",
            "https://images.unsplash.com/photo-1601918774946-25832a4be0d6?w=900&q=85",
        ]
    ),
    dict(
        title="Business Traveller Suite – Nakasero",
        type=PropertyType.short_stay, status=PropertyStatus.for_rent,
        price=95_000, district="Kampala", area="Nakasero",
        description="Sleek 1-bed suite with standing desk, 200 Mbps fibre, USB-C ports at every socket. Walking distance to City Hall and Parliament.",
        bedrooms=1, bathrooms=1, floor_size=60,
        is_verified=True, listing_package=ListingPackage.premium,
        has_furnishing=True, has_internet=True, has_security=True,
        latitude=0.3155, longitude=32.5775,
        is_short_stay=True, price_per_night=95_000, max_guests=2,
        min_nights=1, cleaning_fee=25_000, rating=4.6, review_count=41,
        photos=[
            "https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=900&q=85",
            "https://images.unsplash.com/photo-1564078516393-cf04bd966897?w=900&q=85",
            "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=900&q=85",
        ]
    ),

    # ── HOLIDAY APARTMENTS ────────────────────────────────────────────────────
    dict(
        title="Lakeshore Holiday Cottage – Entebbe",
        type=PropertyType.holiday_apt, status=PropertyStatus.for_rent,
        price=350_000, district="Wakiso", area="Entebbe",
        description="Charming 3-bedroom cottage right on the shores of Lake Victoria. Private jetty, outdoor dining, tropical garden. Near Entebbe Airport.",
        bedrooms=3, bathrooms=2, floor_size=140,
        is_verified=True, listing_package=ListingPackage.featured,
        has_furnishing=True, has_internet=True, has_swimming_pool=True,
        latitude=0.0539, longitude=32.4635,
        is_short_stay=True, price_per_night=350_000, max_guests=6,
        min_nights=2, cleaning_fee=70_000, rating=5.0, review_count=29,
        photos=[
            "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=900&q=85",
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=900&q=85",
            "https://images.unsplash.com/photo-1602002418082-a4443978a5d0?w=900&q=85",
            "https://images.unsplash.com/photo-1455587734955-081b22074882?w=900&q=85",
        ]
    ),
    dict(
        title="Lakeside Holiday Apartment – Munyonyo",
        type=PropertyType.holiday_apt, status=PropertyStatus.for_rent,
        price=280_000, district="Kampala", area="Munyonyo",
        description="Stylish 2-bedroom apartment with private beach access, sun deck and canoe hire. Steps from Munyonyo Commonwealth Resort.",
        bedrooms=2, bathrooms=2, floor_size=95,
        is_verified=True, listing_package=ListingPackage.premium,
        has_furnishing=True, has_internet=True, latitude=0.2720, longitude=32.5980,
        is_short_stay=True, price_per_night=280_000, max_guests=4,
        min_nights=2, cleaning_fee=40_000, rating=4.9, review_count=67,
        photos=[
            "https://images.unsplash.com/photo-1610641818989-c2051b5e2cfd?w=900&q=85",
            "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=900&q=85",
            "https://images.unsplash.com/photo-1613977257365-aaae5a9817ff?w=900&q=85",
        ]
    ),
    dict(
        title="Gorilla Trekking Base – Bwindi",
        type=PropertyType.holiday_apt, status=PropertyStatus.for_rent,
        price=500_000, district="Kanungu", area="Bwindi",
        description="Eco-lodge style 2-bedroom cabin on the edge of Bwindi Impenetrable Forest. Fireplace, jungle views, all meals included.",
        bedrooms=2, bathrooms=1, floor_size=70,
        is_verified=True, listing_package=ListingPackage.featured,
        has_furnishing=True, latitude=-1.0400, longitude=29.6800,
        is_short_stay=True, price_per_night=500_000, max_guests=4,
        min_nights=2, cleaning_fee=60_000, rating=5.0, review_count=18,
        photos=[
            "https://images.unsplash.com/photo-1482192505345-5852ba66e28a?w=900&q=85",
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=900&q=85",
            "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=900&q=85",
        ]
    ),
    dict(
        title="Safari Lodge Cabin – Queen Elizabeth NP",
        type=PropertyType.holiday_apt, status=PropertyStatus.for_rent,
        price=650_000, district="Kasese", area="Queen Elizabeth NP",
        description="Luxury tented safari cabin overlooking the Kazinga Channel. Game drives, boat safaris and sundowner cruises available.",
        bedrooms=1, bathrooms=1, floor_size=50,
        is_verified=True, listing_package=ListingPackage.featured,
        has_furnishing=True, latitude=0.1500, longitude=30.0000,
        is_short_stay=True, price_per_night=650_000, max_guests=2,
        min_nights=2, cleaning_fee=80_000, rating=4.9, review_count=44,
        photos=[
            "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?w=900&q=85",
            "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=900&q=85",
            "https://images.unsplash.com/photo-1564069114553-7215e1ff1890?w=900&q=85",
        ]
    ),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # ── Users ──────────────────────────────────────────────────────────────
        res = await db.execute(select(User).where(User.email == "admin@wamato.ug"))
        admin = res.scalar_one_or_none()
        if not admin:
            admin = User(full_name="Wamato Admin", email="admin@wamato.ug",
                         hashed_password=hash_password("Admin@1234!"),
                         role=UserRole.admin, is_verified=True)
            db.add(admin)
            await db.flush()

        res2 = await db.execute(select(User).where(User.email == "demo@wamato.ug"))
        owner = res2.scalar_one_or_none()
        if not owner:
            owner = User(full_name="Demo Owner", email="demo@wamato.ug",
                         hashed_password=hash_password("Demo@1234"),
                         phone="+256700000000")
            db.add(owner)
            await db.flush()

        # ── Wipe existing properties ────────────────────────────────────────────
        await db.execute(delete(PropertyPhoto))
        await db.execute(delete(Property))
        await db.flush()

        # ── Seed properties with photos ────────────────────────────────────────
        for p in SEED_PROPERTIES:
            photo_urls = p.pop("photos", [])
            prop = Property(owner_id=owner.id, **p)
            db.add(prop)
            await db.flush()
            for i, url in enumerate(photo_urls):
                db.add(PropertyPhoto(
                    property_id=prop.id, url=url, order=i, is_cover=(i == 0)
                ))

        await db.commit()
        print(f"✓ Seeded {len(SEED_PROPERTIES)} properties with real photos + admin + demo owner.")


if __name__ == "__main__":
    asyncio.run(seed())
