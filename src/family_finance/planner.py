from __future__ import annotations

import json
from dataclasses import asdict
from typing import Dict, List

from .models import Account, AssetSegment, Budget, FinanceSnapshot, Household, HouseholdMember


def load_snapshot_from_json(raw: str) -> FinanceSnapshot:
    payload = json.loads(raw)

    household = Household(
        id=payload["household"]["id"],
        name=payload["household"]["name"],
        members=[HouseholdMember(**m) for m in payload["household"].get("members", [])],
    )

    accounts = [Account(**acc) for acc in payload.get("accounts", [])]

    budget_obj = payload.get("budget", {})
    shared = budget_obj.get("shared", {})
    budget = Budget(
        period=budget_obj.get("period", "unknown"),
        shared_required=float(shared.get("required", 0.0)),
        shared_flexible=float(shared.get("flexible", 0.0)),
        personal={k: float(v) for k, v in budget_obj.get("personal", {}).items()},
    )

    asset_segments = [AssetSegment(**seg) for seg in payload.get("asset_segments", [])]

    default_allocations = {account.id: {"operations": 100.0} for account in accounts}
    incoming_allocations = payload.get("account_segment_allocations", {})
    for account_id, allocations in incoming_allocations.items():
        default_allocations[account_id] = {k: float(v) for k, v in allocations.items()}

    return FinanceSnapshot(
        household=household,
        accounts=accounts,
        budget=budget,
        asset_segments=asset_segments,
        account_segment_allocations=default_allocations,
    )


def total_net_assets(snapshot: FinanceSnapshot) -> float:
    return sum(account.balance for account in snapshot.accounts)


def segment_target_amounts(snapshot: FinanceSnapshot) -> Dict[str, float]:
    total = total_net_assets(snapshot)
    return {segment.name: total * (segment.target_pct / 100.0) for segment in snapshot.asset_segments}


def segment_current_amounts(snapshot: FinanceSnapshot) -> Dict[str, float]:
    current: Dict[str, float] = {}
    for account in snapshot.accounts:
        allocations = snapshot.account_segment_allocations.get(account.id, {"operations": 100.0})
        for segment_name, pct in allocations.items():
            current[segment_name] = current.get(segment_name, 0.0) + account.balance * (pct / 100.0)
    return current


def segment_drift(snapshot: FinanceSnapshot) -> Dict[str, float]:
    target = segment_target_amounts(snapshot)
    current = segment_current_amounts(snapshot)
    names = set(target.keys()) | set(current.keys())
    return {name: current.get(name, 0.0) - target.get(name, 0.0) for name in names}


def planned_monthly_budget_total(snapshot: FinanceSnapshot) -> float:
    return snapshot.budget.shared_required + snapshot.budget.shared_flexible + sum(snapshot.budget.personal.values())


def render_report(snapshot: FinanceSnapshot) -> str:
    total_assets = total_net_assets(snapshot)
    targets = segment_target_amounts(snapshot)
    current = segment_current_amounts(snapshot)
    drift = segment_drift(snapshot)

    lines: List[str] = []
    lines.append(f"Household: {snapshot.household.name} ({snapshot.household.id})")
    lines.append(f"Members: {len(snapshot.household.members)} | Accounts: {len(snapshot.accounts)}")
    lines.append(f"Total net assets: ${total_assets:,.2f}")
    lines.append("")
    lines.append(f"Budget period: {snapshot.budget.period}")
    lines.append(f"Shared required: ${snapshot.budget.shared_required:,.2f}")
    lines.append(f"Shared flexible: ${snapshot.budget.shared_flexible:,.2f}")
    lines.append(f"Personal discretionary total: ${sum(snapshot.budget.personal.values()):,.2f}")
    lines.append(f"Planned monthly total: ${planned_monthly_budget_total(snapshot):,.2f}")
    lines.append("")
    lines.append("Segment allocations:")

    ranked = sorted(drift.items(), key=lambda item: abs(item[1]), reverse=True)
    for name, drift_value in ranked:
        lines.append(
            "- "
            f"{name}: current=${current.get(name, 0.0):,.2f}, "
            f"target=${targets.get(name, 0.0):,.2f}, "
            f"drift=${drift_value:,.2f}"
        )

    return "\n".join(lines)


def snapshot_to_dict(snapshot: FinanceSnapshot) -> Dict[str, object]:
    return asdict(snapshot)
