from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    mobile_number: Mapped[str] = mapped_column(String(20), index=True)
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    gotram: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rasi: Mapped[str | None] = mapped_column(String(120), nullable=True)
    nakshatram: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)

    bookings: Mapped[list[Booking]] = relationship(back_populates="customer")


class CeremonyType(Base):
    __tablename__ = "ceremony_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_tamil: Mapped[str] = mapped_column(String(120), unique=True)
    name_english: Mapped[str] = mapped_column(String(120), unique=True)
    default_duration_minutes: Mapped[int] = mapped_column(default=120)
    active: Mapped[bool] = mapped_column(Boolean(), default=True)

    pooja_items: Mapped[list[PoojaItem]] = relationship(back_populates="ceremony", cascade="all, delete-orphan")
    bookings: Mapped[list[Booking]] = relationship(back_populates="ceremony")


class PoojaItem(Base):
    __tablename__ = "pooja_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    ceremony_id: Mapped[int] = mapped_column(ForeignKey("ceremony_types.id"), index=True)
    name_tamil: Mapped[str] = mapped_column(String(160))
    name_english: Mapped[str | None] = mapped_column(String(160), nullable=True)
    quantity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mandatory: Mapped[bool] = mapped_column(Boolean(), default=True)

    ceremony: Mapped[CeremonyType] = relationship(back_populates="pooja_items")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    ceremony_id: Mapped[int] = mapped_column(ForeignKey("ceremony_types.id"), index=True)
    event_date: Mapped[date] = mapped_column(Date(), index=True)
    start_time: Mapped[time] = mapped_column(Time())
    end_time: Mapped[time] = mapped_column(Time())
    muhurtham_time: Mapped[time | None] = mapped_column(Time(), nullable=True)
    arrival_time: Mapped[time | None] = mapped_column(Time(), nullable=True)
    location: Mapped[str] = mapped_column(Text())
    maps_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    advance_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(30), default="CONFIRMED")
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)

    customer: Mapped[Customer] = relationship(back_populates="bookings")
    ceremony: Mapped[CeremonyType] = relationship(back_populates="bookings")
    payments: Mapped[list[Payment]] = relationship(back_populates="booking", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    method: Mapped[str] = mapped_column(String(30), default="CASH")
    payment_date: Mapped[date] = mapped_column(Date(), default=date.today)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)

    booking: Mapped[Booking] = relationship(back_populates="payments")
