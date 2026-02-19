namespace FinanceApi.Dtos;

public record AdminUserResponse(int Id, string FullName, string Email, bool IsAdmin);
public record UpdateUserRoleRequest(bool IsAdmin);
public record AdminAccountResponse(int Id, int UserId, string OwnerEmail, string Name, string Type, decimal Balance);
public record UpdateAccountBalanceRequest(decimal Balance);
public record AdminTransactionResponse(int Id, int UserId, string OwnerEmail, int AccountId, string Type, string Category, decimal Amount, string Description, DateTime CreatedAtUtc);
