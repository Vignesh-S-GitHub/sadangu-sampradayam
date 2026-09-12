import re
import uuid
from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class LoginRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=20)
    pin: str = Field(min_length=4, max_length=20)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int
    user_name: str = "Purohit"


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    mobile_number: str = Field(min_length=8, max_length=20)
    alternate_mobile: str | None = None
    address: str | None = None
    gotram: str | None = None
    rasi: str | None = None
    nakshatram: str | None = None
    notes: str | None = None

    @field_validator("mobile_number", "alternate_mobile")
    @classmethod
    def validate_phone(cls, value: str | None):
        if value is None:
            return value
        cleaned = value.replace(" ", "").replace("-", "")
        if not re.fullmatch(r"\+?[0-9]{8,15}", cleaned):
            raise ValueError("Invalid mobile number")
        return cleaned


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    mobile_number: str | None = Field(default=None, min_length=8, max_length=20)
    alternate_mobile: str | None = None
    address: str | None = None
    gotram: str | None = None
    rasi: str | None = None
    nakshatram: str | None = None
    notes: str | None = None

    @field_validator("mobile_number", "alternate_mobile")
    @classmethod
    def validate_phone(cls, value: str | None):
        if value is None or value == "":
            return value or None
        cleaned = value.replace(" ", "").replace("-", "")
        if not re.fullmatch(r"\+?[0-9]{8,15}", cleaned):
            raise ValueError("Invalid mobile number")
        return cleaned


class CustomerOut(CustomerCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class CeremonyOut(BaseModel):
    id: uuid.UUID
    name_tamil: str
    name_english: str
    description: str | None = None
    default_duration_minutes: int
    model_config = ConfigDict(from_attributes=True)


class PoojaItemOut(BaseModel):
    id: uuid.UUID
    name_tamil: str
    name_english: str | None = None
    quantity: Decimal | None = None
    unit: str | None = None
    mandatory: bool


class BookingCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    mobile_number: str = Field(min_length=8, max_length=20)
    ceremony_id: uuid.UUID
    event_date: date
    start_time: time
    end_time: time
    location: str = Field(min_length=2, max_length=500)
    google_maps_url: str | None = Field(default=None, max_length=1000)
    muhurtham_time: time | None = None
    arrival_time: time | None = None
    total_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    advance_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("mobile_number")
    @classmethod
    def validate_phone(cls, value: str):
        cleaned = value.replace(" ", "").replace("-", "")
        if not re.fullmatch(r"\+?[0-9]{8,15}", cleaned):
            raise ValueError("Invalid mobile number")
        return cleaned

    @model_validator(mode="after")
    def validate_times_and_amounts(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        if self.advance_amount > self.total_amount:
            raise ValueError("Advance amount cannot exceed total amount")
        return self


class BookingUpdate(BaseModel):
    event_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    location: str | None = Field(default=None, min_length=2, max_length=500)
    google_maps_url: str | None = Field(default=None, max_length=1000)
    muhurtham_time: time | None = None
    arrival_time: time | None = None
    total_amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    notes: str | None = Field(default=None, max_length=2000)


class BookingStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        value = value.upper()
        if value not in {"PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"}:
            raise ValueError("Unsupported booking status")
        return value


class BookingOut(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    customer_name: str
    mobile_number: str
    ceremony_id: uuid.UUID
    ceremony_tamil: str
    ceremony_english: str
    event_date: date
    start_time: time
    end_time: time
    location: str | None
    google_maps_url: str | None = None
    total_amount: Decimal
    advance_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    status: str
    payment_status: str


class PaymentCreate(BaseModel):
    booking_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    method: str = "CASH"
    payment_date: datetime = Field(default_factory=datetime.now)
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("method")
    @classmethod
    def validate_method(cls, value: str):
        allowed = {"CASH", "UPI", "BANK_TRANSFER", "OTHER"}
        value = value.upper()
        if value not in allowed:
            raise ValueError("Unsupported payment method")
        return value


class PaymentOut(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    amount: Decimal
    method: str
    payment_date: datetime
    notes: str | None
