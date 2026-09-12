from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    mobile_number: str = Field(min_length=8, max_length=20)
    address: str | None = None
    gotram: str | None = None
    rasi: str | None = None
    nakshatram: str | None = None
    notes: str | None = None


class CustomerOut(CustomerCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CeremonyOut(BaseModel):
    id: int
    name_tamil: str
    name_english: str
    default_duration_minutes: int
    model_config = ConfigDict(from_attributes=True)


class PoojaItemOut(BaseModel):
    id: int
    name_tamil: str
    name_english: str | None
    quantity: str | None
    mandatory: bool
    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    customer_name: str
    mobile_number: str
    ceremony_id: int
    event_date: date
    start_time: time
    end_time: time
    location: str
    total_amount: Decimal = Decimal("0")
    advance_amount: Decimal = Decimal("0")
    notes: str | None = None


class BookingOut(BaseModel):
    id: int
    customer_id: int
    customer_name: str
    mobile_number: str
    ceremony_id: int
    ceremony_tamil: str
    ceremony_english: str
    event_date: date
    start_time: time
    end_time: time
    location: str
    total_amount: Decimal
    advance_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    status: str


class PaymentCreate(BaseModel):
    booking_id: int
    amount: Decimal = Field(gt=0)
    method: str = "CASH"
    payment_date: date = Field(default_factory=date.today)
    notes: str | None = None


class PaymentOut(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    method: str
    payment_date: date
    notes: str | None
    model_config = ConfigDict(from_attributes=True)
