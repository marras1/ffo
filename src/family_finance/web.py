from __future__ import annotations

import html
import os
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from .auth import AuthStore, User
from .planner import load_snapshot_from_json, render_report


class WebApp:
    def __init__(self, db_path: str | Path = "family_finance.db") -> None:
        self.auth = AuthStore(db_path)

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET")
        token = _cookie_value(environ.get("HTTP_COOKIE", ""), "session")
        user = self.auth.user_for_token(token)

        if path == "/":
            return self._response(start_response, self._home_html(user))
        if path == "/register" and method == "GET":
            return self._response(start_response, self._register_html())
        if path == "/register" and method == "POST":
            params = _post_params(environ)
            ok = self.auth.register(params.get("username", [""])[0], params.get("password", [""])[0])
            if ok:
                return self._redirect(start_response, "/login")
            return self._response(start_response, self._register_html("Username already exists or invalid input."))
        if path == "/login" and method == "GET":
            return self._response(start_response, self._login_html())
        if path == "/login" and method == "POST":
            params = _post_params(environ)
            token = self.auth.authenticate(params.get("username", [""])[0], params.get("password", [""])[0])
            if token:
                headers = [("Set-Cookie", f"session={token}; HttpOnly; Path=/")]
                return self._redirect(start_response, "/dashboard", extra_headers=headers)
            return self._response(start_response, self._login_html("Invalid credentials."))
        if path == "/logout":
            if token:
                self.auth.logout(token)
            headers = [("Set-Cookie", "session=; Max-Age=0; Path=/")]
            return self._redirect(start_response, "/", extra_headers=headers)

        if path == "/dashboard":
            if user is None:
                return self._redirect(start_response, "/login")
            return self._response(start_response, self._dashboard_html(user))

        if path == "/accounts" and method == "POST":
            if user is None:
                return self._redirect(start_response, "/login")
            params = _post_params(environ)
            name = params.get("name", [""])[0]
            account_type = params.get("account_type", [""])[0]
            balance_raw = params.get("opening_balance", ["0"])[0]
            try:
                opening_balance = float(balance_raw)
            except ValueError:
                return self._response(start_response, self._dashboard_html(user, "Opening balance must be numeric."))
            ok = self.auth.create_account(user.id, name, account_type, opening_balance)
            if not ok:
                return self._response(start_response, self._dashboard_html(user, "Could not create account."))
            return self._redirect(start_response, "/dashboard")

        if path == "/transactions" and method == "POST":
            if user is None:
                return self._redirect(start_response, "/login")
            params = _post_params(environ)
            kind = params.get("kind", [""])[0]
            description = params.get("description", [""])[0]
            try:
                account_id = int(params.get("account_id", ["0"])[0])
                amount = float(params.get("amount", ["0"])[0])
            except ValueError:
                return self._response(start_response, self._dashboard_html(user, "Invalid account or amount."))
            ok = self.auth.create_transaction(user.id, account_id, kind, amount, description)
            if not ok:
                return self._response(start_response, self._dashboard_html(user, "Could not create transaction."))
            return self._redirect(start_response, "/dashboard")

        if path == "/report" and method == "POST":
            if user is None:
                return self._redirect(start_response, "/login")
            params = _post_params(environ)
            snapshot_raw = params.get("snapshot_json", [""])[0]
            try:
                report = render_report(load_snapshot_from_json(snapshot_raw))
            except Exception as exc:  # noqa: BLE001
                return self._response(start_response, self._dashboard_html(user, f"Invalid JSON snapshot: {exc}"))
            return self._response(start_response, self._dashboard_html(user, report=report))

        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not Found"]

    def _response(self, start_response, body: str):
        data = body.encode("utf-8")
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(data)))])
        return [data]

    def _redirect(self, start_response, location: str, extra_headers=None):
        headers = [("Location", location)]
        if extra_headers:
            headers.extend(extra_headers)
        start_response("302 Found", headers)
        return [b""]

    def _home_html(self, user: User | None) -> str:
        auth_link = '<a href="/dashboard">Dashboard</a>' if user else '<a href="/login">Login</a> | <a href="/register">Register</a>'
        return f"""
        <html><body>
          <h1>Family Finance Planner</h1>
          <p>Manage accounts, expenses, and salary transactions from the dashboard.</p>
          <p>{auth_link}</p>
        </body></html>
        """

    def _register_html(self, error: str = "") -> str:
        err = f"<p style='color:red'>{html.escape(error)}</p>" if error else ""
        return f"""
        <html><body>
          <h1>Register</h1>
          {err}
          <form method="post" action="/register">
            <label>Username <input name="username" /></label><br/>
            <label>Password <input type="password" name="password" /></label><br/>
            <button type="submit">Create account</button>
          </form>
          <a href="/login">Login</a>
        </body></html>
        """

    def _login_html(self, error: str = "") -> str:
        err = f"<p style='color:red'>{html.escape(error)}</p>" if error else ""
        return f"""
        <html><body>
          <h1>Login</h1>
          {err}
          <form method="post" action="/login">
            <label>Username <input name="username" /></label><br/>
            <label>Password <input type="password" name="password" /></label><br/>
            <button type="submit">Sign in</button>
          </form>
          <a href="/register">Register</a>
        </body></html>
        """

    def _dashboard_html(self, user: User, message: str = "", report: str = "") -> str:
        accounts = self.auth.list_accounts(user.id)
        transactions = self.auth.list_transactions(user.id)
        msg = f"<p style='color:red'>{html.escape(message)}</p>" if message else ""
        rendered = f"<pre>{html.escape(report)}</pre>" if report else ""

        accounts_list = "".join(
            f"<li>#{a.id} {html.escape(a.name)} ({html.escape(a.account_type)}): ${a.balance:,.2f}</li>" for a in accounts
        ) or "<li>No accounts yet.</li>"

        tx_list = "".join(
            f"<li>#{t.id} [{html.escape(t.kind)}] account={t.account_id} amount=${t.amount:,.2f} - {html.escape(t.description)}</li>"
            for t in transactions
        ) or "<li>No transactions yet.</li>"

        account_options = "".join(
            f"<option value='{a.id}'>#{a.id} {html.escape(a.name)}</option>" for a in accounts
        )

        sample_json = '{"household":{"id":"fam","name":"My Family","members":[]},"accounts":[],"budget":{"period":"2026-02","shared":{"required":0,"flexible":0},"personal":{}},"asset_segments":[]}'

        return f"""
        <html><body>
          <h1>Dashboard</h1>
          <p>Welcome, {html.escape(user.username)}. <a href="/logout">Logout</a></p>
          {msg}

          <h2>Accounts</h2>
          <ul>{accounts_list}</ul>
          <form method="post" action="/accounts">
            <label>Name <input name="name" /></label>
            <label>Type <input name="account_type" placeholder="checking/savings/brokerage" /></label>
            <label>Opening balance <input name="opening_balance" value="0" /></label>
            <button type="submit">Add account</button>
          </form>

          <h2>Transactions (expense/salary)</h2>
          <ul>{tx_list}</ul>
          <form method="post" action="/transactions">
            <label>Account <select name="account_id">{account_options}</select></label>
            <label>Kind
              <select name="kind">
                <option value="expense">expense</option>
                <option value="income">income (salary)</option>
              </select>
            </label>
            <label>Amount <input name="amount" value="0" /></label>
            <label>Description <input name="description" placeholder="groceries / monthly salary" /></label>
            <button type="submit">Add transaction</button>
          </form>

          <h2>Planner report from JSON snapshot</h2>
          <form method="post" action="/report">
            <label>Finance snapshot JSON</label><br/>
            <textarea name="snapshot_json" rows="12" cols="100">{html.escape(sample_json)}</textarea><br/>
            <button type="submit">Generate report</button>
          </form>
          {rendered}
        </body></html>
        """


def _post_params(environ):
    length = int(environ.get("CONTENT_LENGTH") or 0)
    payload = environ["wsgi.input"].read(length).decode("utf-8")
    return parse_qs(payload)


def _cookie_value(cookie_header: str, name: str) -> str:
    for item in cookie_header.split(";"):
        item = item.strip()
        if not item or "=" not in item:
            continue
        key, value = item.split("=", maxsplit=1)
        if key == name:
            return value
    return ""


def run() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    app = WebApp(os.getenv("FAMILY_FINANCE_DB", "family_finance.db"))
    with make_server(host, port, app) as server:
        print(f"Serving Family Finance Planner on http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    run()
