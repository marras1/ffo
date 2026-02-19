using FinanceApi.Models;

namespace FinanceApi.Services;

public interface ITokenService
{
    string CreateToken(User user);
}
