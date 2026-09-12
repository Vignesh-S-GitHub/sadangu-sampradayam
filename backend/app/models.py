from __future__ import annotations

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(Text(), index=True)
    mobile_number: Mapped[str] = mapped_column(Text(), index=True)
    alternate_mobile: Mapped[str | None] = mapped_column(Text(), nullable=True)
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    gotram: Mapped[str | None] = mapped_column(Text(), nullable=True)
    rasi: Mapped[str | None] = mapped_column(Text(), nullable=True)
    nakshatram: Mapped[str | None] = mapped_column(Text(), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    bookings: Mapped[list[Booking]] = relationship(back_populates="customer")


class CeremonyType(Base):
    __tablename__ = "ceremony_types"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    name_tamil: Mapped[str] = mapped_column(Text(), unique=True)
    name_english: Mapped[str] = mapped_column(Text(), unique=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    default_duration_minutes: Mapped[int] = mapped_column(Integer(), default=120)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    templates: Mapped[list[PoojaTemplate]] = relationship(back_populates="ceremony", cascade="all, delete-orphan")
    bookings: Mapped[list[Booking]] = relationship(back_populates="ceremony")


class PoojaTemplate(Base):
    __tablename__ = "pooja_templates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    ceremony_type_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("ceremony_types.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    ceremony: Mapped[CeremonyType] = relationship(back_populates="templates")
    items: Mapped[list[PoojaItem]] = relationship(back_populates="template", cascade="all, delete-orphan")


class PoojaItem(Base):
    __tablename__ = "pooja_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    template_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("pooja_templates.id", ondelete="CASCADE"), index=True)
    item_name_tamil: Mapped[str] = mapped_column(Text())
    item_name_english: Mapped[str | None] = mapped_column(Text(), nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(), nullable=True)
    unit: Mapped[str | None] = mapped_column(Text(), nullable=True)
    mandatory: Mapped[bool] = mapped_column(Boolean(), default=True)
    sort_order: Mapped[int] = mapped_column(Integer(), default=0)

    template: Mapped[PoojaTemplate] = relationship(back_populates="items")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("customers.id"), index=True)
    ceremony_type_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("ceremony_types.id"), index=True)
    event_date: Mapped[date] = mapped_column(Date(), index=True)
    start_time: Mapped[time] = mapped_column(Time())
    end_time: Mapped[time] = mapped_column(Time())
    muhurtham_time: Mapped[time | None] = mapped_column(Time(), nullable=True)
    arrival_time: Mapped[time | None] = mapped_column(Time(), nullable=True)
    location: Mapped[str | None] = mapped_column(Text(), nullable=True)
    google_maps_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    advance_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(Text(), default="CONFIRMED")
    payment_status: Mapped[str] = mapped_column(Text(), default="UNPAID")
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    customer: Mapped[Customer] = relationship(back_populates="bookings")
    ceremony: Mapped[CeremonyType] = relationship(back_populates="bookings")
    payments: Mapped[list[Payment]] = relationship(back_populates="booking", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    booking_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[str] = mapped_column(Text(), default="CASH")
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    booking: Mapped[Booking] = relationship(back_populates="payments")
