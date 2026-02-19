using System.Security.Claims;
using FinanceApi.Data;
using FinanceApi.Dtos;
using FinanceApi.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace FinanceApi.Controllers;

[ApiController]
[Authorize]
[Route("api/accounts")]
public class AccountsController(FinanceDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IEnumerable<AccountResponse>>> GetMine()
    {
        var userId = GetUserId();
        var accounts = await db.Accounts
            .Where(x => x.UserId == userId)
            .OrderBy(x => x.Id)
            .Select(x => new AccountResponse(x.Id, x.Name, x.Type, x.Balance))
            .ToListAsync();

        return Ok(accounts);
    }

    [HttpPost]
    public async Task<ActionResult<AccountResponse>> Create(CreateAccountRequest request)
    {
        var userId = GetUserId();
        var account = new Account
        {
            UserId = userId,
            Name = request.Name.Trim(),
            Type = request.Type.Trim().ToLowerInvariant(),
            Balance = request.OpeningBalance
        };

        db.Accounts.Add(account);
        await db.SaveChangesAsync();

        return CreatedAtAction(nameof(GetMine), new { id = account.Id },
            new AccountResponse(account.Id, account.Name, account.Type, account.Balance));
    }

    private int GetUserId()
    {
        var sub = User.FindFirstValue(ClaimTypes.NameIdentifier) ?? User.FindFirstValue("sub");
        return int.TryParse(sub, out var id)
            ? id
            : throw new UnauthorizedAccessException("Invalid user token");
    }
}
