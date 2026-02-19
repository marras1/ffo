# Family Finances Overview

This overview proposes a practical structure for managing **multiple users**, **multiple accounts**, a **shared budget**, and **segmented assets with allocations**.

## 1) Core model

### Users
Each family member is a user with role-based permissions.

- `Owner`: full control (typically one or two adults)
- `Member`: can view shared data, manage own accounts/categories
- `Viewer` (optional): read-only

### Accounts
Accounts represent where money exists or moves.

- Checking
- Savings
- Credit cards
- Brokerage
- Retirement
- Cash wallets
- Loans (as liability accounts)

Each account can be:
- **Personal** (owned by one user)
- **Joint** (shared by multiple users)

### Budget scope
Budgets should support two scopes:
- **Shared household budget** (rent, groceries, utilities, school, transport)
- **Personal budgets** (individual spending and goals)

### Assets and allocations
Assets are grouped into segments to support planning and reporting.

Example segments:
- Emergency fund
- Daily operations (cash flow)
- Medium-term goals (vacation, home projects)
- Long-term investments (retirement, college)

Allocations define target percentages or fixed amounts by segment.

---

## 2) Suggested data entities

- `users`
- `households`
- `household_members` (user ↔ household mapping)
- `accounts`
- `account_owners` (user ↔ account ownership split)
- `transactions`
- `categories`
- `budgets`
- `budget_lines` (category caps/targets)
- `asset_segments`
- `allocation_targets` (segment %, account %, or dollar targets)

---

## 3) Ownership and visibility rules

1. A user can always view/edit accounts they own.
2. Joint account visibility is granted to all listed owners.
3. Shared budget categories are visible to all household members.
4. Personal categories/budgets are private unless explicitly shared.
5. Segment allocations can be:
   - household-level (default),
   - or user-level overlays (optional advanced mode).

---

## 4) Allocation strategy example

Assume total net assets = **$250,000**.

| Segment | Target % | Target Amount |
|---|---:|---:|
| Emergency Fund | 15% | $37,500 |
| Operations (0-3 months) | 10% | $25,000 |
| Medium-Term Goals | 20% | $50,000 |
| Long-Term Investments | 55% | $137,500 |

You can also allocate by account constraints:
- Checking and cash accounts prioritized for Emergency + Operations
- Brokerage/retirement prioritized for Long-Term
- High-yield savings split between Emergency and Medium-Term

---

## 5) Shared budget pattern

A clean approach is a **three-layer budget**:

1. **Household Required**
   - Mortgage/rent
   - Utilities
   - Insurance
   - Debt minimums

2. **Household Flexible**
   - Groceries
   - Dining
   - Transport
   - Family entertainment

3. **Personal Discretionary** (per user)
   - Personal shopping
   - Hobbies
   - Personal subscriptions

Track each line with:
- monthly target
- actual spend
- variance
- owner (household vs specific user)

---

## 6) Monthly workflow

1. **Ingest transactions** from all accounts.
2. **Auto-categorize** then review exceptions.
3. **Reconcile shared budget** (required + flexible).
4. **Reconcile personal budgets**.
5. **Recompute asset allocation drift**.
6. **Recommend transfers/rebalancing** to restore target allocations.
7. **Publish family dashboard**:
   - net worth trend
   - spend vs budget
   - allocation vs target
   - goal progress

---

## 7) Useful dashboard views

- Household net worth (monthly trend)
- Cash runway (months of expenses covered)
- Budget variance by category
- User-level discretionary spend
- Allocation heatmap by segment and account
- Goal funding progress (e.g., vacation, college, home)

---

## 8) Example JSON shape

```json
{
  "household": {
    "id": "fam_001",
    "name": "Rivera Family",
    "members": [
      {"user_id": "u_anna", "role": "owner"},
      {"user_id": "u_miguel", "role": "owner"},
      {"user_id": "u_lee", "role": "member"}
    ]
  },
  "accounts": [
    {"id": "acc_check_joint", "type": "checking", "owners": ["u_anna", "u_miguel"], "balance": 12000},
    {"id": "acc_brokerage", "type": "brokerage", "owners": ["u_anna", "u_miguel"], "balance": 85000},
    {"id": "acc_roth_anna", "type": "retirement", "owners": ["u_anna"], "balance": 60000}
  ],
  "budget": {
    "period": "2026-02",
    "shared": {
      "required": 6200,
      "flexible": 2100
    },
    "personal": {
      "u_anna": 500,
      "u_miguel": 500
    }
  },
  "asset_segments": [
    {"name": "emergency", "target_pct": 15},
    {"name": "operations", "target_pct": 10},
    {"name": "medium_term", "target_pct": 20},
    {"name": "long_term", "target_pct": 55}
  ]
}
```

---

## 9) Implementation notes (if building software)

- Use immutable transaction ledgers and derived reporting tables.
- Separate permissions from ownership to support advisors/auditors.
- Keep category taxonomy stable; avoid frequent renames.
- Support split transactions (one payment, multiple categories/users).
- Add audit logs for category edits and allocation changes.

This structure keeps collaboration simple while preserving personal autonomy and clear long-term planning.
