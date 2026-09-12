-- Backend-only database hardening for Sadangu Sampradayam.
-- The Flet client talks only to FastAPI; it does not query Supabase Data API directly.

revoke all on table
  public.users,
  public.customers,
  public.family_members,
  public.ceremony_types,
  public.bookings,
  public.pooja_templates,
  public.pooja_items,
  public.booking_pooja_items,
  public.payments,
  public.reminders
from anon, authenticated;

alter default privileges for role postgres in schema public
  revoke select, insert, update, delete on tables from anon, authenticated;
alter default privileges for role postgres in schema public
  revoke usage, select on sequences from anon, authenticated;
alter default privileges for role postgres in schema public
  revoke execute on functions from anon, authenticated;

create unique index if not exists uq_customers_mobile_number
  on public.customers (mobile_number);
create unique index if not exists uq_pooja_template_ceremony
  on public.pooja_templates (ceremony_type_id);
create unique index if not exists uq_pooja_item_template_name
  on public.pooja_items (template_id, item_name_tamil);
create index if not exists ix_bookings_event_date_time
  on public.bookings (event_date, start_time, end_time);
create index if not exists ix_bookings_customer_id
  on public.bookings (customer_id);
create index if not exists ix_payments_booking_id
  on public.payments (booking_id);
create index if not exists ix_reminders_remind_at
  on public.reminders (remind_at);

alter table public.bookings
  drop constraint if exists bookings_time_order_chk;
alter table public.bookings
  add constraint bookings_time_order_chk check (end_time > start_time);

alter table public.bookings
  drop constraint if exists bookings_advance_lte_total_chk;
alter table public.bookings
  add constraint bookings_advance_lte_total_chk check (advance_amount <= total_amount);
