from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Booking, CeremonyType, Customer, Payment, PoojaItem, PoojaTemplate


CEREMONIES = [
    ("திருமணம்", "Marriage", "திருமண வைதீக சடங்கு", 180, [("தேங்காய்", 5, "எண்"), ("மஞ்சள்", 1, "பொதி"), ("குங்குமம்", 1, "பொதி"), ("வெற்றிலை", 25, "இலை"), ("பாக்கு", 25, "எண்"), ("பழங்கள்", 1, "தட்டு"), ("மலர்கள்", 1, "தொகுப்பு"), ("அட்சதை", 1, "பொதி")]),
    ("கிரகப்பிரவேசம்", "Griha Pravesam", "புது வீடு புகும் சடங்கு", 150, [("தேங்காய்", 5, "எண்"), ("மஞ்சள்", 1, "பொதி"), ("குங்குமம்", 1, "பொதி"), ("மாமர இலை", 1, "தொகுப்பு"), ("கலசம்", 1, "எண்"), ("அரிசி", 2, "கிலோ"), ("நெய்", 1, "பாட்டில்"), ("ஹோமப் பொருட்கள்", 1, "தொகுப்பு")]),
    ("கணபதி ஹோமம்", "Ganapathi Homam", "விநாயகர் ஹோமம்", 120, [("தேங்காய்", 3, "எண்"), ("அருகம்புல்", 1, "தொகுப்பு"), ("வாழைப்பழம்", 12, "எண்"), ("மலர்கள்", 1, "தொகுப்பு"), ("நெய்", 1, "பாட்டில்"), ("ஹோமப் பொருட்கள்", 1, "தொகுப்பு")]),
    ("ஆயுஷ் ஹோமம்", "Ayush Homam", "ஆயுள் ஆரோக்கிய ஹோமம்", 120, [("கலசம்", 1, "எண்"), ("நெய்", 1, "பாட்டில்"), ("ஹோமப் பொருட்கள்", 1, "தொகுப்பு"), ("பழங்கள்", 1, "தட்டு"), ("மலர்கள்", 1, "தொகுப்பு")]),
    ("நாமகரணம்", "Naming Ceremony", "குழந்தை பெயரிடும் சடங்கு", 90, [("மஞ்சள்", 1, "பொதி"), ("குங்குமம்", 1, "பொதி"), ("பழங்கள்", 1, "தட்டு"), ("மலர்கள்", 1, "தொகுப்பு"), ("வெற்றிலை", 15, "இலை"), ("பாக்கு", 15, "எண்")]),
    ("நிச்சயதார்த்தம்", "Engagement", "திருமண நிச்சய சடங்கு", 90, [("தேங்காய்", 3, "எண்"), ("மஞ்சள்", 1, "பொதி"), ("குங்குமம்", 1, "பொதி"), ("வெற்றிலை", 25, "இலை"), ("பாக்கு", 25, "எண்"), ("மலர்கள்", 1, "தொகுப்பு"), ("பழங்கள்", 1, "தட்டு")]),
    ("சீமந்தம்", "Seemantham", "மங்கள சடங்கு", 120, []),
    ("உபநயனம்", "Upanayanam", "பூணூல் சடங்கு", 180, []),
]


def seed(db: Session) -> None:
    for tamil, english, description, duration, items in CEREMONIES:
        ceremony = db.scalar(select(CeremonyType).where(CeremonyType.name_english == english))
        if not ceremony:
            ceremony = CeremonyType(name_tamil=tamil, name_english=english, description=description, default_duration_minutes=duration, is_active=True)
            db.add(ceremony)
            db.flush()
        template = db.scalar(select(PoojaTemplate).where(PoojaTemplate.ceremony_type_id == ceremony.id))
        if not template:
            template = PoojaTemplate(ceremony_type_id=ceremony.id, name=f"{tamil} - பொதுப் பட்டியல்")
            db.add(template)
            db.flush()
        existing = {x.item_name_tamil for x in db.scalars(select(PoojaItem).where(PoojaItem.template_id == template.id))}
        for idx, (item_name, qty, unit) in enumerate(items, 1):
            if item_name not in existing:
                db.add(PoojaItem(template_id=template.id, item_name_tamil=item_name, quantity=Decimal(str(qty)), unit=unit, mandatory=True, sort_order=idx))
    db.commit()

    if not db.scalar(select(Customer.id).limit(1)):
        customer = Customer(name="Kumar", mobile_number="9876543210", address="Nagercoil")
        db.add(customer)
        db.flush()
        ceremony = db.scalar(select(CeremonyType).where(CeremonyType.name_english == "Marriage"))
        booking = Booking(customer_id=customer.id, ceremony_type_id=ceremony.id, event_date=date.today() + timedelta(days=1), start_time=time(6, 0), end_time=time(9, 0), location="Nagercoil", total_amount=Decimal("10000"), advance_amount=Decimal("3000"), status="CONFIRMED", payment_status="PARTIAL")
        db.add(booking)
        db.flush()
        db.add(Payment(booking_id=booking.id, amount=Decimal("3000"), payment_method="UPI", payment_date=datetime.now(timezone.utc), notes="Booking advance"))
        db.commit()
