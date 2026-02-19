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
[Route("api/transactions")]
public class TransactionsController(FinanceDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IEnumerable<TransactionResponse>>> GetMine()
    {
        var userId = GetUserId();
        var transactions = await db.Transactions
            .Where(x => x.UserId == userId)
            .OrderByDescending(x => x.CreatedAtUtc)
            .Select(x => new TransactionResponse(x.Id, x.AccountId, x.Type, x.Category, x.Amount, x.Description, x.CreatedAtUtc))
            .ToListAsync();

        return Ok(transactions);
    }

    [HttpPost]
    public async Task<ActionResult<TransactionResponse>> Create(CreateTransactionRequest request)
    {
        var userId = GetUserId();
        var account = await db.Accounts.SingleOrDefaultAsync(x => x.Id == request.AccountId && x.UserId == userId);
        if (account is null)
        {
            return NotFound("Account not found.");
        }

        var type = request.Type.Trim().ToLowerInvariant();
        if (type is not ("income" or "expense"))
        {
            return BadRequest("Transaction type must be income or expense.");
        }

        var transaction = new Transaction
        {
            AccountId = account.Id,
            UserId = userId,
            Type = type,
            Category = request.Category.Trim(),
            Amount = request.Amount,
            Description = request.Description.Trim(),
            CreatedAtUtc = DateTime.UtcNow
        };

        account.Balance += type == "income" ? request.Amount : -request.Amount;
        db.Transactions.Add(transaction);
        await db.SaveChangesAsync();

        return Ok(new TransactionResponse(
            transaction.Id,
            transaction.AccountId,
            transaction.Type,
            transaction.Category,
            transaction.Amount,
            transaction.Description,
            transaction.CreatedAtUtc));
    }

    private int GetUserId()
    {
        var sub = User.FindFirstValue(ClaimTypes.NameIdentifier) ?? User.FindFirstValue("sub");
        return int.TryParse(sub, out var id)
            ? id
            : throw new UnauthorizedAccessException("Invalid user token");
    }
}
