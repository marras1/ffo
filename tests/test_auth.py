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
