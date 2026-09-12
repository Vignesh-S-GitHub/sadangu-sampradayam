import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..models import Booking, CeremonyType, Customer, Payment, PoojaItem, PoojaTemplate
from ..schemas import (
    BookingCreate, BookingOut, BookingStatusUpdate, BookingUpdate, CeremonyOut,
    CustomerCreate, CustomerOut, CustomerUpdate, PaymentCreate, PaymentOut, PoojaItemOut,
)
from ..service import booking_to_out, create_booking
from ..security import require_auth

router = APIRouter(prefix="/api", dependencies=[Depends(require_auth)])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    today = date.today()
    today_count = db.scalar(select(func.count()).select_from(Booking).where(Booking.event_date == today, Booking.status != "CANCELLED")) or 0
    upcoming = db.scalar(select(func.count()).select_from(Booking).where(Booking.event_date >= today, Booking.status != "CANCELLED")) or 0
    totals = db.execute(select(Booking.id, Booking.total_amount).where(Booking.status != "CANCELLED")).all()
    pending = Decimal("0")
    for booking_id, total_amount in totals:
        paid = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.booking_id == booking_id)) or Decimal("0")
        pending += max(Decimal("0"), Decimal(total_amount or 0) - Decimal(paid))

    next_booking = db.scalar(
        select(Booking)
        .options(joinedload(Booking.customer), joinedload(Booking.ceremony))
        .where(Booking.event_date >= today, Booking.status != "CANCELLED")
        .order_by(Booking.event_date, Booking.start_time)
        .limit(1)
    )
    return {
        "today_bookings": today_count,
        "upcoming_bookings": upcoming,
        "pending_amount": float(pending),
        "next_booking": booking_to_out(db, next_booking).model_dump(mode="json") if next_booking else None,
    }


@router.get("/ceremonies", response_model=list[CeremonyOut])
def ceremonies(db: Session = Depends(get_db)):
    return list(db.scalars(select(CeremonyType).where(CeremonyType.is_active.is_(True)).order_by(CeremonyType.name_tamil)))


@router.get("/ceremonies/{ceremony_id}/pooja-items", response_model=list[PoojaItemOut])
def pooja_items(ceremony_id: uuid.UUID, db: Session = Depends(get_db)):
    if not db.get(CeremonyType, ceremony_id):
        raise HTTPException(status_code=404, detail="Ceremony not found")
    rows = db.execute(
        select(PoojaItem)
        .join(PoojaTemplate, PoojaItem.template_id == PoojaTemplate.id)
        .where(PoojaTemplate.ceremony_type_id == ceremony_id)
        .order_by(PoojaItem.sort_order, PoojaItem.item_name_tamil)
    ).scalars().all()
    return [
        PoojaItemOut(
            id=row.id,
            name_tamil=row.item_name_tamil,
            name_english=row.item_name_english,
            quantity=row.quantity,
            unit=row.unit,
            mandatory=row.mandatory,
        )
        for row in rows
    ]


@router.get("/customers", response_model=list[CustomerOut])
def customers(db: Session = Depends(get_db)):
    return list(db.scalars(select(Customer).order_by(Customer.name)))


@router.post("/customers", response_model=CustomerOut, status_code=201)
def add_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Customer).where(Customer.mobile_number == payload.mobile_number))
    if existing:
        raise HTTPException(status_code=409, detail="Mobile number already exists")
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: uuid.UUID, payload: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    changes = payload.model_dump(exclude_unset=True)
    mobile = changes.get("mobile_number")
    if mobile and mobile != customer.mobile_number:
        duplicate = db.scalar(select(Customer.id).where(Customer.mobile_number == mobile, Customer.id != customer_id))
        if duplicate:
            raise HTTPException(status_code=409, detail="Mobile number already exists")
    for key, value in changes.items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/bookings", response_model=list[BookingOut])
def bookings(db: Session = Depends(get_db)):
    rows = list(db.scalars(select(Booking).options(joinedload(Booking.customer), joinedload(Booking.ceremony)).order_by(Booking.event_date, Booking.start_time)))
    return [booking_to_out(db, row) for row in rows]


@router.post("/bookings", response_model=BookingOut, status_code=201)
def add_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    return create_booking(db, payload)


@router.put("/bookings/{booking_id}", response_model=BookingOut)
def update_booking(booking_id: uuid.UUID, payload: BookingUpdate, db: Session = Depends(get_db)):
    booking = db.scalar(
        select(Booking)
        .options(joinedload(Booking.customer), joinedload(Booking.ceremony))
        .where(Booking.id == booking_id)
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    changes = payload.model_dump(exclude_unset=True)
    event_date = changes.get("event_date", booking.event_date)
    start_time = changes.get("start_time", booking.start_time)
    end_time = changes.get("end_time", booking.end_time)
    if end_time <= start_time:
        raise HTTPException(status_code=422, detail="End time must be after start time")

    conflict = db.scalar(
        select(Booking.id).where(
            Booking.id != booking_id,
            Booking.event_date == event_date,
            Booking.status != "CANCELLED",
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        ).limit(1)
    )
    if conflict:
        raise HTTPException(status_code=409, detail="Booking conflict detected for this time slot")

    if "total_amount" in changes:
        paid = Decimal(db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.booking_id == booking.id)) or 0)
        if changes["total_amount"] < paid:
            raise HTTPException(status_code=422, detail="Total amount cannot be less than amount already paid")

    for key, value in changes.items():
        setattr(booking, key, value)
    db.commit()
    booking = db.scalar(
        select(Booking)
        .options(joinedload(Booking.customer), joinedload(Booking.ceremony))
        .where(Booking.id == booking_id)
    )
    return booking_to_out(db, booking)


@router.patch("/bookings/{booking_id}/status", response_model=BookingOut)
def update_booking_status(booking_id: uuid.UUID, payload: BookingStatusUpdate, db: Session = Depends(get_db)):
    booking = db.scalar(
        select(Booking)
        .options(joinedload(Booking.customer), joinedload(Booking.ceremony))
        .where(Booking.id == booking_id)
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = payload.status
    db.commit()
    db.refresh(booking)
    return booking_to_out(db, booking)


@router.get("/payments", response_model=list[PaymentOut])
def payments(db: Session = Depends(get_db)):
    rows = list(db.scalars(select(Payment).order_by(Payment.payment_date.desc(), Payment.id.desc())))
    return [PaymentOut(id=x.id, booking_id=x.booking_id, amount=x.amount, method=x.payment_method, payment_date=x.payment_date, notes=x.notes) for x in rows]


@router.post("/payments", response_model=PaymentOut, status_code=201)
def add_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    booking = db.get(Booking, payload.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    current_paid = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.booking_id == booking.id)) or Decimal("0")
    total = Decimal(booking.total_amount or 0)
    if total <= 0:
        raise HTTPException(status_code=422, detail="Cannot record payment for a zero-total booking")
    if Decimal(current_paid) + payload.amount > total:
        raise HTTPException(status_code=422, detail="Payment exceeds the outstanding balance")
    payment = Payment(booking_id=payload.booking_id, amount=payload.amount, payment_method=payload.method, payment_date=payload.payment_date, notes=payload.notes)
    db.add(payment)
    db.flush()
    paid = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.booking_id == booking.id)) or Decimal("0")
    booking.payment_status = "PAID" if Decimal(paid) >= total else ("PARTIAL" if Decimal(paid) > 0 else "UNPAID")
    db.commit()
    db.refresh(payment)
    return PaymentOut(id=payment.id, booking_id=payment.booking_id, amount=payment.amount, method=payment.payment_method, payment_date=payment.payment_date, notes=payment.notes)


@router.get("/reminders")
def reminders(db: Session = Depends(get_db)):
    today = date.today()
    until = today + timedelta(days=7)
    rows = list(db.scalars(select(Booking).options(joinedload(Booking.customer), joinedload(Booking.ceremony)).where(Booking.event_date.between(today, until), Booking.status != "CANCELLED").order_by(Booking.event_date, Booking.start_time)))
    return [{"id": str(row.id), "title": f"{row.ceremony.name_tamil} - {row.customer.name}", "event_date": row.event_date.isoformat(), "start_time": row.start_time.strftime("%H:%M"), "location": row.location or ""} for row in rows]
