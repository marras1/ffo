using System.Text;
using FinanceApi.Data;
using FinanceApi.Models;
using FinanceApi.Services;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo { Title = "Finance API", Version = "v1" });
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "bearer",
        BearerFormat = "JWT",
        In = ParameterLocation.Header,
        Description = "Enter JWT Bearer token"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

builder.Services.AddDbContext<FinanceDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddScoped<ITokenService, TokenService>();

var jwtSection = builder.Configuration.GetSection("Jwt");
var secret = jwtSection["Secret"] ?? throw new InvalidOperationException("JWT secret is missing.");
var key = Encoding.UTF8.GetBytes(secret);

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateIssuerSigningKey = true,
            ValidateLifetime = true,
            ValidIssuer = jwtSection["Issuer"],
            ValidAudience = jwtSection["Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(key)
        };
    });

builder.Services.AddAuthorization();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<FinanceDbContext>();
    var logger = scope.ServiceProvider.GetRequiredService<ILoggerFactory>().CreateLogger("Startup");

    try
    {
        var hasMigrations = db.Database.GetMigrations().Any();
        if (hasMigrations)
        {
            db.Database.Migrate();
        }
        else
        {
            db.Database.EnsureCreated();
        }
    }
    catch (Exception ex)
    {
        logger.LogWarning(ex, "Migration/initialization attempt failed; retrying with EnsureCreated.");
        db.Database.EnsureCreated();
    }

    var usersTableExists = TableExists(db, "Users");
    if (!usersTableExists)
    {
        // Second chance initialization for edge cases where migrate path completed without creating domain tables.
        db.Database.EnsureCreated();
        usersTableExists = TableExists(db, "Users");
    }

    if (usersTableExists)
    {
        // Backward-compatible patch for existing DBs created before IsAdmin existed.
        db.Database.ExecuteSqlRaw("ALTER TABLE \"Users\" ADD COLUMN IF NOT EXISTS \"IsAdmin\" boolean NOT NULL DEFAULT FALSE;");

        var adminEmail = app.Configuration["AdminUser:Email"]?.Trim().ToLowerInvariant();
        var adminPassword = app.Configuration["AdminUser:Password"];
        var adminFullName = app.Configuration["AdminUser:FullName"] ?? "System Admin";

        if (!string.IsNullOrWhiteSpace(adminEmail) && !string.IsNullOrWhiteSpace(adminPassword))
        {
            var admin = db.Users.SingleOrDefault(x => x.Email == adminEmail);
            if (admin is null)
            {
                db.Users.Add(new User
                {
                    FullName = adminFullName,
                    Email = adminEmail,
                    PasswordHash = BCrypt.Net.BCrypt.HashPassword(adminPassword),
                    IsAdmin = true
                });
                db.SaveChanges();
            }
            else if (!admin.IsAdmin)
            {
                admin.IsAdmin = true;
                db.SaveChanges();
            }
        }
    }
    else
    {
        logger.LogWarning("Users table is still missing after initialization; admin seeding skipped.");
    }
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseDefaultFiles();
app.UseStaticFiles();

var useHttpsRedirection = app.Configuration.GetValue<bool?>("UseHttpsRedirection") ?? app.Environment.IsProduction();
if (useHttpsRedirection)
{
    app.UseHttpsRedirection();
}

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();

static bool TableExists(FinanceDbContext db, string tableName)
{
    // Handles case sensitivity from quoted table names by comparing lowercase.
    return db.Database
        .SqlQueryRaw<bool>(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = current_schema() AND lower(table_name) = lower({0}));",
            tableName)
        .AsEnumerable()
        .FirstOrDefault();
}
