from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from .models import Booking, CeremonyType, Customer, Payment
from .schemas import BookingCreate, BookingOut


def booking_to_out(db: Session, booking: Booking) -> BookingOut:
    paid = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.booking_id == booking.id)) or Decimal("0")
    total = Decimal(booking.total_amount or 0)
    return BookingOut(
        id=booking.id,
        customer_id=booking.customer_id,
        customer_name=booking.customer.name,
        mobile_number=booking.customer.mobile_number,
        ceremony_id=booking.ceremony_id,
        ceremony_tamil=booking.ceremony.name_tamil,
        ceremony_english=booking.ceremony.name_english,
        event_date=booking.event_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        location=booking.location,
        total_amount=total,
        advance_amount=Decimal(booking.advance_amount or 0),
        paid_amount=Decimal(paid),
        balance_amount=max(Decimal("0"), total - Decimal(paid)),
        status=booking.status,
    )


def create_booking(db: Session, payload: BookingCreate) -> BookingOut:
    ceremony = db.get(CeremonyType, payload.ceremony_id)
    if not ceremony:
        raise HTTPException(status_code=404, detail="Ceremony type not found")

    overlap = db.scalar(
        select(Booking.id).where(
            Booking.event_date == payload.event_date,
            Booking.status != "CANCELLED",
            Booking.start_time < payload.end_time,
            Booking.end_time > payload.start_time,
        ).limit(1)
    )
    if overlap:
        raise HTTPException(status_code=409, detail="Booking conflict detected for this time slot")

    customer = db.scalar(select(Customer).where(Customer.mobile_number == payload.mobile_number))
    if not customer:
        customer = Customer(name=payload.customer_name, mobile_number=payload.mobile_number, address=payload.location)
        db.add(customer)
        db.flush()
    elif customer.name != payload.customer_name:
        customer.name = payload.customer_name

    booking = Booking(
        customer_id=customer.id,
        ceremony_id=payload.ceremony_id,
        event_date=payload.event_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=payload.location,
        total_amount=payload.total_amount,
        advance_amount=payload.advance_amount,
        notes=payload.notes,
        status="CONFIRMED",
    )
    db.add(booking)
    db.flush()
    if payload.advance_amount > 0:
        payment_date = payload.event_date if payload.event_date < datetime.now().date() else datetime.now().date()
        db.add(Payment(booking_id=booking.id, amount=payload.advance_amount, method="ADVANCE", payment_date=payment_date))
    db.commit()
    db.refresh(booking)
    booking = db.scalar(select(Booking).options(joinedload(Booking.customer), joinedload(Booking.ceremony)).where(Booking.id == booking.id))
    return booking_to_out(db, booking)
