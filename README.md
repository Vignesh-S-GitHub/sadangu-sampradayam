<div align="center">

# சடங்கு சம்பிரதாயம்
### Sadangu Sampradayam

**Tamil-first ceremony management for Purohit services**

*Bookings · pooja checklists · customer records · payment tracking*

</div>

A mobile-first service-management application for organizing ceremony bookings and the details around each event. The visual system follows the project’s approved brand: a cream canvas, deep maroon, warm gold, Tamil-first typography, and the kuthu-vilakku mark.

## Product capabilities

| Plan ceremonies | Prepare for the day | Keep records |
|---|---|---|
| Booking calendar and conflict prevention | Ceremony-specific pooja checklists | Customer directory and location links |
| Seven-day reminders | WhatsApp checklist sharing | Advance, balance, and payment tracking |

## Architecture

```text
Flet web / Android client
        │ HTTPS + bearer token
        ▼
FastAPI application API
        │ PostgreSQL connection
        ▼
Supabase PostgreSQL
```

The client accesses application data through FastAPI; it does not connect directly to Supabase tables. Web and Android APK builds are configured in GitHub Actions.

## Technology

- **Mobile and web UI:** Python with Flet
- **API:** FastAPI
- **Database:** Supabase PostgreSQL
- **Delivery:** Docker Compose and GitHub Actions

## Development notes

Start with the files in `docs/` and `.env.example` to understand the configuration and product workflow. Keep secrets in local environment configuration and route database operations through the API.

## Brand palette

| Color | Hex |
|---|---|
| Deep maroon | `#570B17` |
| Maroon | `#7A1020` |
| Warm gold | `#C58A1A` |
| Saffron | `#F2A019` |

---

<p align="center"><sub>Thoughtful ceremony planning, rooted in Tamil tradition.</sub></p>
