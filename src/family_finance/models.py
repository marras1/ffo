from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class HouseholdMember:
    user_id: str
    role: str


@dataclass(frozen=True)
class Household:
    id: str
    name: str
    members: List[HouseholdMember]


@dataclass(frozen=True)
class Account:
    id: str
    type: str
    owners: List[str]
    balance: float


@dataclass(frozen=True)
class Budget:
    period: str
    shared_required: float
    shared_flexible: float
    personal: Dict[str, float]


@dataclass(frozen=True)
class AssetSegment:
    name: str
    target_pct: float


@dataclass(frozen=True)
class FinanceSnapshot:
    household: Household
    accounts: List[Account]
    budget: Budget
    asset_segments: List[AssetSegment]
    account_segment_allocations: Dict[str, Dict[str, float]]
