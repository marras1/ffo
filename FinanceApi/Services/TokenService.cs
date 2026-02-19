using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using FinanceApi.Models;
using Microsoft.IdentityModel.Tokens;

namespace FinanceApi.Services;

public class TokenService(IConfiguration configuration) : ITokenService
{
    public string CreateToken(User user)
    {
        var jwt = configuration.GetSection("Jwt");
        var secret = jwt["Secret"] ?? throw new InvalidOperationException("JWT secret is not configured.");
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new(JwtRegisteredClaimNames.Email, user.Email),
            new(ClaimTypes.Email, user.Email),
            new("name", user.FullName),
            new(ClaimTypes.Role, user.IsAdmin ? "Admin" : "User")
        };

        var token = new JwtSecurityToken(
            issuer: jwt["Issuer"],
            audience: jwt["Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddHours(8),
            signingCredentials: creds);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
