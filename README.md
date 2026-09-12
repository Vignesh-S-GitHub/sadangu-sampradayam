# சடங்கு சம்பிரதாயம் — Sadangu Sampradayam

Mobile-first Purohit service management application built with **Python + Flet + FastAPI + Supabase/PostgreSQL**.

The visual system is based on the approved Sadangu Sampradayam brand: **cream canvas, deep maroon primary, warm gold accents, Tamil-first typography, and the approved kuthu-vilakku logo**.

## Production V1

- Secure phone + PIN sign-in through FastAPI
- Tamil-first mobile dashboard
- Ceremony booking and time-conflict prevention
- Booking/calendar list
- Customer directory
- Ceremony-specific pooja checklist
- WhatsApp checklist sharing
- Advance/payment/balance tracking
- Overpayment protection
- Seven-day reminders
- Google Maps link storage
- Supabase PostgreSQL UUID schema
- Direct Supabase Data API table access blocked; application data flows through FastAPI
- Web and Android APK GitHub Actions builds

## Architecture

```text
Flet Web / Android App
        │ HTTPS + Bearer token
        ▼
FastAPI backend
        │ PostgreSQL connection
        ▼
Supabase PostgreSQL
```

The Flet client **does not connect directly to Supabase tables**.

## Brand tokens

| Token | Value |
|---|---|
| Primary maroon | `#7A1020` |
| Deep maroon | `#570B17` |
| Gold | `#C58A1A` |
| Saffron | `#F2A019` |
| Cream | `#FFF8E8` |
| Card | `#FFFCF5` |
| Ink | `#3F2723` |

Approved assets are under `mobile/src/assets/`.

## Local web verification

### 1. Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

$env:ADMIN_PHONE="9000000000"
$env:ADMIN_PIN="1234"
$env:JWT_SECRET="local-development-secret-change-before-production"
$env:AUTH_REQUIRED="true"

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: `http://127.0.0.1:8000/docs`

### 2. Flet web

```powershell
cd mobile
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
$env:SADANGU_API_URL="http://127.0.0.1:8000"
flet run --web --port 8550 src/main.py
```

Open `http://127.0.0.1:8550`.

## Production backend configuration

Configure these as environment variables in the backend host. **Do not commit them.**

```env
APP_ENV=production
DATABASE_URL=postgresql+psycopg://...
CORS_ORIGINS=https://your-web-app.example
AUTH_REQUIRED=true
ADMIN_PHONE=<your-father-phone>
ADMIN_PIN=<strong-pin>
JWT_SECRET=<32+-character-random-secret>
TOKEN_TTL_MINUTES=720
AUTO_CREATE_SCHEMA=false
SEED_DEMO_DATA=false
```

The Supabase connection string belongs only in the backend environment / GitHub secret. Never embed it in the Flet web or APK bundle.

## GitHub repository settings

Create these repository values:

### Secret

- `DATABASE_URL` — Supabase PostgreSQL connection string used only by the read-only CI smoke test.

### Variable

- `SADANGU_API_URL` — public HTTPS URL of the deployed FastAPI backend used when building web/APK artifacts.

## Testing

Backend tests:

```powershell
cd backend
pytest -q
```

The suite checks:

- public health endpoint
- protected API routes
- correct/incorrect login
- booking creation
- booking time conflict
- invalid advance amount
- overpayment rejection
- payment settlement and zero balance

CI additionally:

- compiles backend and Flet Python sources
- connects to the configured Supabase database
- checks production master ceremony data exists
- builds Flet web output
- builds Android APK artifacts

## Android preview

Before generating an APK, put phone and PC on the same Wi-Fi.

Backend:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Flet mobile preview:

```powershell
cd mobile
$env:SADANGU_API_URL="http://YOUR_PC_LAN_IP:8000"
flet run --android src/main.py
```

## APK

For a local Android build:

```powershell
cd mobile
$env:SADANGU_API_URL="https://YOUR-PUBLIC-FASTAPI-URL"
flet build apk . --yes --split-per-abi
```

For Google Play later:

```powershell
flet build aab . --yes
```

GitHub Actions also produces downloadable web and APK artifacts from `.github/workflows/build-app.yml`.

## Supabase

The live project contains master data only:

- 8 ceremony types
- 8 pooja templates
- 40 pooja items
- no demo customers/bookings

Schema and hardening SQL are versioned under `supabase/migrations/`.
