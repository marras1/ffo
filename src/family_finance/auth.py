from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class User:
    id: int
    username: str


@dataclass(frozen=True)
class ManagedAccount:
    id: int
    user_id: int
    name: str
    account_type: str
    balance: float


@dataclass(frozen=True)
class ManagedTransaction:
    id: int
    user_id: int
    account_id: int
    kind: str
    amount: float
    description: str


class AuthStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    balance REAL NOT NULL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    account_id INTEGER NOT NULL,
                    kind TEXT NOT NULL CHECK(kind IN ('income', 'expense')),
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
                """
            )

    def register(self, username: str, password: str) -> bool:
        if not username or not password:
            return False
        password_hash = _hash_password(password)
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users(username, password_hash) VALUES (?, ?)",
                    (username, password_hash),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate(self, username: str, password: str) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, password_hash FROM users WHERE username = ?", (username,)
            ).fetchone()
            if row is None:
                return None
            if not _verify_password(password, str(row["password_hash"])):
                return None

            token = secrets.token_urlsafe(32)
            conn.execute("INSERT INTO sessions(token, user_id) VALUES(?, ?)", (token, int(row["id"])))
            return token

    def user_for_token(self, token: str) -> Optional[User]:
        if not token:
            return None
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT u.id, u.username
                FROM sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token = ?
                """,
                (token,),
            ).fetchone()
        if row is None:
            return None
        return User(id=int(row["id"]), username=str(row["username"]))

    def logout(self, token: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))

    def create_account(self, user_id: int, name: str, account_type: str, opening_balance: float) -> bool:
        if not name.strip() or not account_type.strip():
            return False
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO accounts(user_id, name, account_type, balance) VALUES (?, ?, ?, ?)",
                (user_id, name.strip(), account_type.strip(), float(opening_balance)),
            )
        return True

    def list_accounts(self, user_id: int) -> List[ManagedAccount]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, user_id, name, account_type, balance FROM accounts WHERE user_id = ? ORDER BY id",
                (user_id,),
            ).fetchall()
        return [
            ManagedAccount(
                id=int(r["id"]),
                user_id=int(r["user_id"]),
                name=str(r["name"]),
                account_type=str(r["account_type"]),
                balance=float(r["balance"]),
            )
            for r in rows
        ]

    def create_transaction(self, user_id: int, account_id: int, kind: str, amount: float, description: str) -> bool:
        if kind not in {"income", "expense"}:
            return False
        if amount <= 0:
            return False
        if not description.strip():
            return False

        with self._connect() as conn:
            owner_row = conn.execute(
                "SELECT id FROM accounts WHERE id = ? AND user_id = ?",
                (account_id, user_id),
            ).fetchone()
            if owner_row is None:
                return False

            signed_amount = float(amount) if kind == "income" else -float(amount)
            conn.execute(
                "INSERT INTO transactions(user_id, account_id, kind, amount, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, account_id, kind, float(amount), description.strip()),
            )
            conn.execute(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                (signed_amount, account_id),
            )
        return True

    def list_transactions(self, user_id: int) -> List[ManagedTransaction]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, user_id, account_id, kind, amount, description
                FROM transactions
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()
        return [
            ManagedTransaction(
                id=int(r["id"]),
                user_id=int(r["user_id"]),
                account_id=int(r["account_id"]),
                kind=str(r["kind"]),
                amount=float(r["amount"]),
                description=str(r["description"]),
            )
            for r in rows
        ]


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return f"{salt.hex()}:{digest.hex()}"


def _verify_password(password: str, combined: str) -> bool:
    try:
        salt_hex, digest_hex = combined.split(":", maxsplit=1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    provided = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return secrets.compare_digest(expected, provided)
