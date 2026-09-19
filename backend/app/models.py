from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db

user_roles = Table(
    "user_roles",
    db.metadata,
    db.Column(
        "user_id", ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    ),
    db.Column(
        "role_id", ForeignKey("roles.role_id", ondelete="RESTRICT"), primary_key=True
    ),
    db.Column("assigned_at", db.DateTime, default=datetime.utcnow, nullable=False),
)


property_amenities = Table(
    "property_amenities",
    db.metadata,
    db.Column(
        "property_id",
        ForeignKey("properties.property_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "amenity_id",
        ForeignKey("amenities.amenity_id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class Role(db.Model):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(db.String(30), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )


class User(db.Model):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        db.String(150), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(db.String(20), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    roles: Mapped[list[Role]] = relationship(secondary=user_roles, lazy="selectin")
    properties: Mapped[list[Property]] = relationship(back_populates="host")
    bookings: Mapped[list[Booking]] = relationship(back_populates="guest")

    @property
    def role_names(self) -> set[str]:
        return {role.role_name for role in self.roles}


class Property(db.Model):
    __tablename__ = "properties"
    __table_args__ = (
        CheckConstraint("capacity BETWEEN 1 AND 50", name="chk_properties_capacity"),
        CheckConstraint("base_price > 0", name="chk_properties_price"),
        Index("idx_properties_search", "city", "is_active", "capacity", "base_price"),
    )

    property_id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(db.String(150), nullable=False)
    slug: Mapped[str] = mapped_column(db.String(180), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=False)
    address_line: Mapped[str] = mapped_column(db.String(255), nullable=False)
    city: Mapped[str] = mapped_column(db.String(100), nullable=False)
    country: Mapped[str] = mapped_column(
        db.String(100), default="India", nullable=False
    )
    capacity: Mapped[int] = mapped_column(nullable=False)
    bedrooms: Mapped[int] = mapped_column(default=1, nullable=False)
    bathrooms: Mapped[Decimal] = mapped_column(
        db.Numeric(3, 1), default=1, nullable=False
    )
    base_price: Mapped[Decimal] = mapped_column(db.Numeric(10, 2), nullable=False)
    average_rating: Mapped[Decimal] = mapped_column(
        db.Numeric(3, 2), default=0, nullable=False
    )
    review_count: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    host: Mapped[User] = relationship(back_populates="properties")
    images: Mapped[list[PropertyImage]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="PropertyImage.display_order",
        lazy="selectin",
    )
    amenities: Mapped[list[Amenity]] = relationship(
        secondary=property_amenities,
        lazy="selectin",
    )
    availability_windows: Mapped[list[AvailabilityWindow]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list[Booking]] = relationship(back_populates="property")


class PropertyImage(db.Model):
    __tablename__ = "property_images"
    __table_args__ = (UniqueConstraint("property_id", "display_order"),)

    image_id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(db.String(500), nullable=False)
    alt_text: Mapped[str] = mapped_column(db.String(180), nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)

    property: Mapped[Property] = relationship(back_populates="images")


class Amenity(db.Model):
    __tablename__ = "amenities"

    amenity_id: Mapped[int] = mapped_column(primary_key=True)
    amenity_name: Mapped[str] = mapped_column(
        db.String(60), unique=True, nullable=False
    )


class AvailabilityWindow(db.Model):
    __tablename__ = "availability_windows"
    __table_args__ = (
        UniqueConstraint("property_id", "start_date", "end_date"),
        CheckConstraint("start_date < end_date", name="chk_availability_dates"),
        CheckConstraint("price_per_night > 0", name="chk_availability_price"),
        Index(
            "idx_availability_search",
            "property_id",
            "is_active",
            "start_date",
            "end_date",
        ),
    )

    availability_id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    price_per_night: Mapped[Decimal] = mapped_column(db.Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    note: Mapped[str | None] = mapped_column(db.String(255))
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )

    property: Mapped[Property] = relationship(back_populates="availability_windows")


class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("check_in < check_out", name="chk_bookings_dates"),
        CheckConstraint("guest_count > 0", name="chk_bookings_guests"),
        CheckConstraint(
            "status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED')",
            name="chk_bookings_status",
        ),
        Index("idx_bookings_overlap", "property_id", "status", "check_in", "check_out"),
    )

    booking_id: Mapped[int] = mapped_column(primary_key=True)
    guest_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.property_id", ondelete="RESTRICT"), nullable=False
    )
    check_in: Mapped[date] = mapped_column(nullable=False)
    check_out: Mapped[date] = mapped_column(nullable=False)
    guest_count: Mapped[int] = mapped_column(nullable=False)
    nightly_rate: Mapped[Decimal] = mapped_column(db.Numeric(10, 2), nullable=False)
    total_nights: Mapped[int] = mapped_column(nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        db.String(20), default="PENDING", nullable=False
    )
    cancellation_reason: Mapped[str | None] = mapped_column(db.String(500))
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    guest: Mapped[User] = relationship(back_populates="bookings")
    property: Mapped[Property] = relationship(back_populates="bookings", lazy="joined")
    payment: Mapped[Payment | None] = relationship(
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
    )
    review: Mapped[Review | None] = relationship(
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Payment(db.Model):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.booking_id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    amount: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(db.String(3), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(
        db.String(20), default="PENDING", nullable=False
    )
    provider_reference: Mapped[str | None] = mapped_column(db.String(100), unique=True)
    paid_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    booking: Mapped[Booking] = relationship(back_populates="payment")


class Review(db.Model):
    __tablename__ = "reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.booking_id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    guest_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
    )
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.property_id", ondelete="RESTRICT"), nullable=False
    )
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str | None] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    booking: Mapped[Booking] = relationship(back_populates="review")


class Favorite(db.Model):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.property_id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )


class BookingStatusHistory(db.Model):
    __tablename__ = "booking_status_history"

    history_id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False
    )
    old_status: Mapped[str | None] = mapped_column(db.String(20))
    new_status: Mapped[str] = mapped_column(db.String(20), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
