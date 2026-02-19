namespace FinanceApi.Dtos;

public record CreateTransactionRequest(int AccountId, string Type, string Category, decimal Amount, string Description);
public record TransactionResponse(
    int Id,
    int AccountId,
    string Type,
    string Category,
    decimal Amount,
    string Description,
    DateTime CreatedAtUtc);
