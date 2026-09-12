-- Sadangu Sampradayam initial Supabase schema.
-- UUID-first schema matching the FastAPI domain model.

create extension if not exists pgcrypto;

create table if not exists public.users (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    phone text unique,
    email text unique,
    role text not null default 'PUROHIT',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.customers (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    mobile_number text not null,
    alternate_mobile text,
    address text,
    gotram text,
    rasi text,
    nakshatram text,
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists ix_customers_name on public.customers(name);
create index if not exists ix_customers_mobile on public.customers(mobile_number);

create table if not exists public.family_members (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references public.customers(id) on delete cascade,
    name text not null,
    relationship text,
    rasi text,
    nakshatram text,
    notes text,
    created_at timestamptz not null default now()
);

create table if not exists public.ceremony_types (
    id uuid primary key default gen_random_uuid(),
    name_tamil text not null unique,
    name_english text not null unique,
    description text,
    default_duration_minutes integer not null default 120 check (default_duration_minutes > 0),
    is_active boolean not null default true,
    created_at timestamptz not null default now()
);

create table if not exists public.bookings (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references public.customers(id),
    ceremony_type_id uuid not null references public.ceremony_types(id),
    event_date date not null,
    start_time time not null,
    end_time time not null,
    muhurtham_time time,
    arrival_time time,
    location text,
    google_maps_url text,
    total_amount numeric(12,2) not null default 0 check (total_amount >= 0),
    advance_amount numeric(12,2) not null default 0 check (advance_amount >= 0),
    status text not null default 'PENDING' check (status in ('PENDING','CONFIRMED','COMPLETED','CANCELLED')),
    payment_status text not null default 'UNPAID' check (payment_status in ('UNPAID','PARTIAL','PAID')),
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint ck_booking_time_range check (end_time > start_time)
);
create index if not exists ix_bookings_event_date on public.bookings(event_date);
create index if not exists ix_bookings_customer on public.bookings(customer_id);
create index if not exists ix_bookings_ceremony on public.bookings(ceremony_type_id);

create table if not exists public.pooja_templates (
    id uuid primary key default gen_random_uuid(),
    ceremony_type_id uuid not null references public.ceremony_types(id) on delete cascade,
    name text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.pooja_items (
    id uuid primary key default gen_random_uuid(),
    template_id uuid not null references public.pooja_templates(id) on delete cascade,
    item_name_tamil text not null,
    item_name_english text,
    quantity numeric,
    unit text,
    mandatory boolean not null default true,
    sort_order integer not null default 0
);

create table if not exists public.booking_pooja_items (
    id uuid primary key default gen_random_uuid(),
    booking_id uuid not null references public.bookings(id) on delete cascade,
    pooja_item_id uuid references public.pooja_items(id),
    item_name_tamil text not null,
    quantity numeric,
    unit text,
    is_checked boolean not null default false
);

create table if not exists public.payments (
    id uuid primary key default gen_random_uuid(),
    booking_id uuid not null references public.bookings(id) on delete cascade,
    amount numeric(12,2) not null check (amount > 0),
    payment_method text not null default 'CASH' check (payment_method in ('CASH','UPI','BANK_TRANSFER','OTHER')),
    payment_date timestamptz not null default now(),
    notes text,
    created_at timestamptz not null default now()
);

create table if not exists public.reminders (
    id uuid primary key default gen_random_uuid(),
    booking_id uuid references public.bookings(id) on delete cascade,
    customer_id uuid references public.customers(id) on delete cascade,
    reminder_type text not null,
    remind_at timestamptz not null,
    message text,
    status text not null default 'PENDING' check (status in ('PENDING','SENT','CANCELLED')),
    created_at timestamptz not null default now()
);

alter table public.users enable row level security;
alter table public.customers enable row level security;
alter table public.family_members enable row level security;
alter table public.ceremony_types enable row level security;
alter table public.bookings enable row level security;
alter table public.pooja_templates enable row level security;
alter table public.pooja_items enable row level security;
alter table public.booking_pooja_items enable row level security;
alter table public.payments enable row level security;
alter table public.reminders enable row level security;

-- No public RLS policies by design: Flet talks only to FastAPI.
