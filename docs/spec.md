# Finance Hub Spec (Modern Rebuild)

## Technology stack
- ASP.NET Core 8 Web API
- Entity Framework Core 8
- PostgreSQL / SQL Server capable (implemented with PostgreSQL provider)
- JWT Bearer Authentication
- Swagger/OpenAPI

## Functional scope
1. User registration/login with secure password hashing.
2. JWT-based authorization for protected resources.
3. Account management:
   - create account
   - list own accounts
4. Transaction management:
   - create income/expense transactions
   - list own transactions
   - auto-update account balance after transaction writes
5. Minimal modern web UI for auth + account/transaction operations.

## Non-functional
- Clear API-first architecture with EF Core data model.
- Swagger enabled in development.
- Static SPA-like UI served by ASP.NET app.
