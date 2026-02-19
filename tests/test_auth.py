from family_finance.auth import AuthStore


def test_register_login_logout_cycle(tmp_path):
    store = AuthStore(tmp_path / "auth.db")

    assert store.register("alice", "pw123") is True
    assert store.register("alice", "pw123") is False

    token = store.authenticate("alice", "pw123")
    assert token is not None
    user = store.user_for_token(token)
    assert user is not None
    assert user.username == "alice"

    store.logout(token)
    assert store.user_for_token(token) is None


def test_auth_rejects_bad_credentials(tmp_path):
    store = AuthStore(tmp_path / "auth.db")
    store.register("bob", "good")

    assert store.authenticate("bob", "bad") is None
    assert store.authenticate("missing", "good") is None


def test_account_and_transaction_management(tmp_path):
    store = AuthStore(tmp_path / "auth.db")
    store.register("sam", "pw")
    token = store.authenticate("sam", "pw")
    user = store.user_for_token(token)
    assert user is not None

    assert store.create_account(user.id, "Main Checking", "checking", 1000) is True
    accounts = store.list_accounts(user.id)
    assert len(accounts) == 1
    assert accounts[0].balance == 1000

    assert store.create_transaction(user.id, accounts[0].id, "income", 2000, "Salary") is True
    assert store.create_transaction(user.id, accounts[0].id, "expense", 150, "Groceries") is True

    refreshed = store.list_accounts(user.id)
    assert refreshed[0].balance == 2850

    tx = store.list_transactions(user.id)
    assert len(tx) == 2
