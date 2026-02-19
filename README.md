# Finance Hub (ASP.NET Core 8)

A modernized Revolut-like starter backend + lightweight web UI built with:

- ASP.NET Core 8 Web API
- Entity Framework Core 8
- PostgreSQL (Npgsql provider)
- JWT Authentication
- Swagger / OpenAPI

## Project structure

- `FinanceApi/Program.cs` – service registration, JWT auth, Swagger, static file hosting
- `FinanceApi/Data/FinanceDbContext.cs` – EF Core DbContext
- `FinanceApi/Models/*` – entities (`User`, `Account`, `Transaction`)
- `FinanceApi/Controllers/*` – auth/accounts/transactions APIs
- `FinanceApi/Services/TokenService.cs` – JWT token generation
- `FinanceApi/wwwroot/*` – minimal modern single-page UI (auth + accounts + transactions)

## Run

1. Install .NET 8 SDK and PostgreSQL.
2. Set `FinanceApi/appsettings.json` connection string and JWT secret.
3. From `FinanceApi/`:

```bash
dotnet restore
dotnet ef database update
dotnet run
```

4. Open:
- UI: `https://localhost:5001` (or printed URL)
- Swagger: `https://localhost:5001/swagger`

## API summary

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET/POST /api/accounts` (JWT)
- `GET/POST /api/transactions` (JWT)

