# Architecture

## Goal

Sadangu Sampradayam is a Tamil-first mobile application that reduces the day-to-day administration required for a Purohit: bookings, customer history, ceremony preparation, payments, and reminders.

## System diagram

```text
┌─────────────────────────────┐
│ Flet Mobile App             │
│ Python                      │
│                             │
│ Dashboard / Booking         │
│ Customers / Pooja List      │
│ Payments / Reminders        │
└──────────────┬──────────────┘
               │ HTTPS / JSON
               ▼
┌─────────────────────────────┐
│ FastAPI Backend             │
│ Python                      │
│                             │
│ Validation / Business Rules │
│ Booking Conflict Checks     │
└──────────────┬──────────────┘
               │ SQLAlchemy
               ▼
┌─────────────────────────────┐
│ PostgreSQL                  │
│ Supabase (production)       │
│ SQLite (local fallback)     │
└─────────────────────────────┘
```

## Core modules

### Customer
Stores name, mobile, address, gotram, rasi, nakshatram and notes.

### Ceremony
Data-driven ceremony list. Pooja item templates are associated with ceremony types so lists are editable without changing the mobile UI.

### Booking
Stores ceremony, customer, date, start/end time, location, total amount, advance and status. The API blocks overlapping confirmed bookings.

### Payment
Supports multiple payments per booking. Balance is derived from booking total minus all recorded payments.

### Reminder
V1 derives the upcoming seven-day reminder list from bookings. A later version can persist notification schedules and use Firebase Cloud Messaging.

## Design system

The app follows the generated Sadangu Sampradayam visual identity:

- Cream background
- Deep maroon primary actions
- Warm gold highlights
- Saffron accents
- Rounded cards
- Kuthu-vilakku logo
- Tamil-first labels with English support planned

## Production path

V1 stays a modular monolith. If the app later supports many Purohits, organizations and customer self-service, scale the database and API horizontally before considering service decomposition.
