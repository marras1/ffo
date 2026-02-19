namespace FinanceApi.Dtos;

public record CreateAccountRequest(string Name, string Type, decimal OpeningBalance);
public record AccountResponse(int Id, string Name, string Type, decimal Balance);
