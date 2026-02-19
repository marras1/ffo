# Finance Hub Spec (Modern Rebuild)

## Technology stack
- ASP.NET Core 8 Web API
- Entity Framework Core 8
- PostgreSQL / SQL Server capable (implemented with PostgreSQL provider)
- JWT Bearer Authentication with role claims
- Swagger/OpenAPI
- PWA frontend (manifest + service worker)

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
5. Admin management:
   - seeded startup admin user
   - user administration (grant/revoke admin)
   - account administration (set balances)
   - transaction audit visibility
6. Startup resiliency:
   - database schema auto-initialization (`Migrate` if migrations exist, `EnsureCreated` otherwise)
   - backward-compatible `Users.IsAdmin` patch on startup
   - configurable HTTPS redirection for environments without TLS termination.
