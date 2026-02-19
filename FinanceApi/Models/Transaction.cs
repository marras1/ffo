namespace FinanceApi.Models;

public class Transaction
{
    public int Id { get; set; }
    public int AccountId { get; set; }
    public Account? Account { get; set; }

    public int UserId { get; set; }
    public User? User { get; set; }

    public string Category { get; set; } = string.Empty;
    public string Type { get; set; } = "expense";
    public decimal Amount { get; set; }
    public string Description { get; set; } = string.Empty;
    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
}
