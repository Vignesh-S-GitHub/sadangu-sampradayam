# Supabase setup

Sadangu Sampradayam uses Supabase as managed PostgreSQL only. The Flet client never receives database credentials.

## Schema

Run `migrations/001_initial_schema.sql` on the selected Supabase project, or apply the equivalent migration through the Supabase tooling.

RLS is enabled on all `public` tables and no `anon`/`authenticated` policies are defined. This intentionally blocks direct client/Data API access. FastAPI is the only application data layer.

## Backend connection

Set `DATABASE_URL` only in the backend hosting environment. Do not commit the real value.

Example shape:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/postgres
```

Use the connection details shown by your Supabase project. For hosted/serverless environments, use the pooler connection recommended by Supabase for your deployment model.
