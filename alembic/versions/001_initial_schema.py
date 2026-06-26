"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_enum(name: str, *values: str) -> None:
    """Create a PostgreSQL enum type, silently skip if it already exists."""
    vals = ", ".join(f"'{v}'" for v in values)
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({vals});
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)


def upgrade() -> None:
    _create_enum("userrole", "user", "agent", "admin")
    _create_enum("propertystatus", "for_rent", "for_sale", "for_lease")
    _create_enum("propertytype", "house", "apartment", "office", "land", "warehouse", "commercial", "short_stay", "holiday_apt")
    _create_enum("listingpackage", "basic", "premium", "featured")
    _create_enum("bookingstatus", "pending", "confirmed", "cancelled", "completed", "no_show")
    _create_enum("paymentstatus", "pending", "processing", "success", "failed", "refunded")
    _create_enum("paymenttype", "booking", "listing_package", "unlock_property", "unlock_pack")
    _create_enum("paymentmethod", "mtn_momo", "airtel_money", "card")
    _create_enum("messagetype", "text", "image", "system")
    _create_enum("notificationtype", "booking_request", "booking_confirmed", "booking_cancelled", "new_message", "new_review", "property_unlocked", "payment_success", "system")

    op.create_table("users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("phone", sa.String(20)),
        sa.Column("whatsapp", sa.String(20)),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("user", "agent", "admin", name="userrole"), nullable=False, server_default="user"),
        sa.Column("avatar_url", sa.String(512)),
        sa.Column("bio", sa.Text),
        sa.Column("district", sa.String(100)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_email_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table("properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("type", sa.Enum("house","apartment","office","land","warehouse","commercial","short_stay","holiday_apt", name="propertytype"), nullable=False),
        sa.Column("status", sa.Enum("for_rent","for_sale","for_lease", name="propertystatus"), nullable=False),
        sa.Column("price", sa.Numeric(15, 2), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("area", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("exact_location", sa.String(500)),
        sa.Column("owner_phone", sa.String(20)),
        sa.Column("owner_whatsapp", sa.String(20)),
        sa.Column("bedrooms", sa.Integer),
        sa.Column("bathrooms", sa.Integer),
        sa.Column("parking_spaces", sa.Integer),
        sa.Column("plot_size", sa.Float),
        sa.Column("floor_size", sa.Float),
        sa.Column("has_security", sa.Boolean, server_default="false"),
        sa.Column("has_furnishing", sa.Boolean, server_default="false"),
        sa.Column("has_internet", sa.Boolean, server_default="false"),
        sa.Column("has_swimming_pool", sa.Boolean, server_default="false"),
        sa.Column("has_gym", sa.Boolean, server_default="false"),
        sa.Column("has_generator", sa.Boolean, server_default="false"),
        sa.Column("has_water_tank", sa.Boolean, server_default="false"),
        sa.Column("has_solar", sa.Boolean, server_default="false"),
        sa.Column("latitude", sa.Float),
        sa.Column("longitude", sa.Float),
        sa.Column("is_short_stay", sa.Boolean, server_default="false"),
        sa.Column("price_per_night", sa.Numeric(12, 2)),
        sa.Column("max_guests", sa.Integer),
        sa.Column("min_nights", sa.Integer),
        sa.Column("cleaning_fee", sa.Numeric(10, 2)),
        sa.Column("rating", sa.Float, server_default="0"),
        sa.Column("review_count", sa.Integer, server_default="0"),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("listing_package", sa.Enum("basic","premium","featured", name="listingpackage"), server_default="basic"),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_featured", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_properties_owner_id", "properties", ["owner_id"])
    op.create_index("ix_properties_status", "properties", ["status"])
    op.create_index("ix_properties_is_active", "properties", ["is_active"])

    op.create_table("property_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.String(512), nullable=False),
        sa.Column("thumbnail_url", sa.String(512)),
        sa.Column("order", sa.Integer, server_default="0"),
        sa.Column("is_cover", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table("saved_properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table("unlock_credits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table("bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("guest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("check_in", sa.Date, nullable=False),
        sa.Column("check_out", sa.Date, nullable=False),
        sa.Column("guests", sa.Integer, nullable=False, server_default="1"),
        sa.Column("price_per_night", sa.Numeric(12, 2), nullable=False),
        sa.Column("nights", sa.Integer, nullable=False),
        sa.Column("cleaning_fee", sa.Numeric(10, 2), server_default="0"),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.Enum("pending","confirmed","cancelled","completed","no_show", name="bookingstatus"), server_default="pending"),
        sa.Column("special_requests", sa.Text),
        sa.Column("cancellation_reason", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table("reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="SET NULL")),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("comment", sa.Text),
        sa.Column("cleanliness", sa.Integer),
        sa.Column("location", sa.Integer),
        sa.Column("value", sa.Integer),
        sa.Column("communication", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
    )

    op.create_table("conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id", ondelete="SET NULL")),
        sa.Column("participant_a", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("participant_b", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("last_message_preview", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table("messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("message_type", sa.Enum("text","image","system", name="messagetype"), server_default="text"),
        sa.Column("is_read", sa.Boolean, server_default="false"),
        sa.Column("attachment_url", sa.String(512)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    op.create_table("notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum(
            "booking_request","booking_confirmed","booking_cancelled","new_message",
            "new_review","property_unlocked","payment_success","system",
            name="notificationtype"
        ), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("is_read", sa.Boolean, server_default="false"),
        sa.Column("action_url", sa.String(512)),
        sa.Column("related_id", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.create_table("payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="SET NULL")),
        sa.Column("type", sa.Enum("booking","listing_package","unlock_property","unlock_pack", name="paymenttype"), nullable=False),
        sa.Column("method", sa.Enum("mtn_momo","airtel_money","card", name="paymentmethod"), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(5), server_default="UGX"),
        sa.Column("status", sa.Enum("pending","processing","success","failed","refunded", name="paymentstatus"), server_default="pending"),
        sa.Column("provider_ref", sa.String(255)),
        sa.Column("phone_number", sa.String(20)),
        sa.Column("description", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_status", "payments", ["status"])


def downgrade() -> None:
    for tbl in ["payments","notifications","messages","conversations","reviews","bookings",
                "unlock_credits","saved_properties","property_photos","properties","users"]:
        op.drop_table(tbl)
    for name in ["userrole","propertystatus","propertytype","listingpackage","bookingstatus",
                 "paymentstatus","paymenttype","paymentmethod","messagetype","notificationtype"]:
        op.execute(f"DROP TYPE IF EXISTS {name}")
