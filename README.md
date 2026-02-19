# Finance Hub (ASP.NET Core 8)

Finance Hub is a modernized personal-finance starter app (Revolut-like direction) with:

- ASP.NET Core 8 Web API
- Entity Framework Core 8
- PostgreSQL (Npgsql provider)
- JWT authentication + role-based authorization
- Admin panel + admin APIs
- PWA shell (manifest + service worker)

## What is implemented

- User registration and login (`/api/auth/register`, `/api/auth/login`)
- JWT-secured APIs for personal accounts and transactions
- Automatic account balance updates when transactions are created
- Admin-only APIs to:
  - list users
  - grant/revoke admin role
  - list all accounts and override balances
  - list all transactions for audit
- Startup DB initialization (`Migrate` if migrations exist, otherwise `EnsureCreated`)
- Startup admin seeding from configuration
- Frontend SPA-like dashboard with admin section
- PWA metadata and service worker for install/offline shell behavior

## Prerequisites

Install these tools on your machine:

1. **.NET SDK 8.0**
   - Verify with: `dotnet --version`
2. **PostgreSQL 14+** (or compatible)
   - Ensure a database user and database are created
3. (Optional but recommended) **EF Core CLI tools**
   - Install globally: `dotnet tool install --global dotnet-ef`

## Configuration

All runtime configuration is in:

- `FinanceApi/appsettings.json`

### 1) Database connection

Set `ConnectionStrings:DefaultConnection`:

```json
"ConnectionStrings": {
  "DefaultConnection": "Host=localhost;Port=5432;Database=finance_db;Username=postgres;Password=postgres"
}
```

### 2) JWT settings

Set `Jwt:Secret` to a long, random secret (32+ chars minimum):

```json
"Jwt": {
  "Issuer": "FinanceApi",
  "Audience": "FinanceApiClients",
  "Secret": "YOUR_LONG_RANDOM_SECRET"
}
```

### 3) Seeded admin user credentials

Set initial admin credentials in:

```json
"AdminUser": {
  "FullName": "Finance Administrator",
  "Email": "admin@finance.local",
  "Password": "Admin123!ChangeMe"
}
```

> Change these values before production.

### 4) HTTPS redirection behavior

For local HTTP-only development, keep:

```json
"UseHttpsRedirection": false
```

Enable in production behind proper TLS configuration.

## Run locally

From repository root:

```bash
cd FinanceApi
dotnet restore
dotnet ef database update
dotnet run
```

If no migrations are present, startup fallback still creates schema via `EnsureCreated()`.

## How to use

1. Open the app URL printed by `dotnet run` (usually `http://localhost:5000` or `https://localhost:5001`).
2. Login with the seeded admin user from `appsettings.json` **or** register a normal user.
3. Create accounts (checking/savings/etc.).
4. Create transactions (income/expense); balances update automatically.
5. If logged in as admin, use the Admin panel to manage users and balances.
6. Open Swagger at `/swagger` to test API endpoints directly.

## Notes about binaries

This repository intentionally avoids binary web assets for compatibility with your PR constraints.
PWA icons are stored as text-based SVG files:

- `FinanceApi/wwwroot/icon-192.svg`
- `FinanceApi/wwwroot/icon-512.svg`

## Additional validation steps (recommended)

Apart from:

```bash
dotnet restore
dotnet ef database update
dotnet run
```

also run:

1. **Build check**
```bash
dotnet build
```

2. **Smoke API checks** (replace token with real JWT)
```bash
# health of startup/auth path
curl -i http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@finance.local","password":"Admin123!ChangeMe"}'

# swagger availability
curl -I http://localhost:5000/swagger
```

3. **Database sanity** (inside PostgreSQL)
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema='public';
SELECT COUNT(*) FROM "Users";
```

4. **PWA check in browser**
- Open DevTools → Application → Manifest/Service Workers
- Confirm manifest loads and service worker is active.


## Troubleshooting startup errors

If you hit errors like `relation "Users" does not exist`:

1. Ensure connection string points to the DB you expect.
2. Run:
   ```bash
   dotnet ef database update
   ```
3. Verify schema exists in PostgreSQL:
   ```sql
   SELECT table_schema, table_name
   FROM information_schema.tables
   WHERE lower(table_name) IN ('users','accounts','transactions');
   ```
4. If migration history is inconsistent, recreate local DB (dev only) and rerun migrations.

The startup code now includes defensive checks:
- migrate/ensure-created fallback
- case-insensitive `Users` table existence check
- skip admin seeding safely if `Users` is still missing

