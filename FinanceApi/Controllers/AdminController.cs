using FinanceApi.Data;
using FinanceApi.Dtos;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace FinanceApi.Controllers;

[ApiController]
[Authorize(Roles = "Admin")]
[Route("api/admin")]
public class AdminController(FinanceDbContext db) : ControllerBase
{
    [HttpGet("users")]
    public async Task<ActionResult<IEnumerable<AdminUserResponse>>> GetUsers()
    {
        var users = await db.Users
            .OrderBy(x => x.Id)
            .Select(x => new AdminUserResponse(x.Id, x.FullName, x.Email, x.IsAdmin))
            .ToListAsync();
        return Ok(users);
    }

    [HttpPatch("users/{id:int}/role")]
    public async Task<ActionResult> UpdateUserRole(int id, UpdateUserRoleRequest request)
    {
        var user = await db.Users.FindAsync(id);
        if (user is null) return NotFound();

        user.IsAdmin = request.IsAdmin;
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpGet("accounts")]
    public async Task<ActionResult<IEnumerable<AdminAccountResponse>>> GetAccounts()
    {
        var accounts = await db.Accounts
            .Include(x => x.User)
            .OrderBy(x => x.Id)
            .Select(x => new AdminAccountResponse(x.Id, x.UserId, x.User!.Email, x.Name, x.Type, x.Balance))
            .ToListAsync();
        return Ok(accounts);
    }

    [HttpPatch("accounts/{id:int}/balance")]
    public async Task<ActionResult> SetAccountBalance(int id, UpdateAccountBalanceRequest request)
    {
        var account = await db.Accounts.FindAsync(id);
        if (account is null) return NotFound();

        account.Balance = request.Balance;
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpGet("transactions")]
    public async Task<ActionResult<IEnumerable<AdminTransactionResponse>>> GetTransactions()
    {
        var transactions = await db.Transactions
            .Include(x => x.User)
            .OrderByDescending(x => x.CreatedAtUtc)
            .Select(x => new AdminTransactionResponse(
                x.Id,
                x.UserId,
                x.User!.Email,
                x.AccountId,
                x.Type,
                x.Category,
                x.Amount,
                x.Description,
                x.CreatedAtUtc))
            .ToListAsync();
        return Ok(transactions);
    }
}
