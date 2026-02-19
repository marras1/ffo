from family_finance.planner import (
    load_snapshot_from_json,
    planned_monthly_budget_total,
    render_report,
    segment_current_amounts,
    segment_drift,
    segment_target_amounts,
    total_net_assets,
)

SAMPLE = """
{
  "household": {
    "id": "fam_001",
    "name": "Rivera Family",
    "members": [
      {"user_id": "u_anna", "role": "owner"},
      {"user_id": "u_miguel", "role": "owner"}
    ]
  },
  "accounts": [
    {"id": "acc_check_joint", "type": "checking", "owners": ["u_anna", "u_miguel"], "balance": 10000},
    {"id": "acc_brokerage", "type": "brokerage", "owners": ["u_anna", "u_miguel"], "balance": 90000}
  ],
  "budget": {
    "period": "2026-02",
    "shared": {"required": 6000, "flexible": 2000},
    "personal": {"u_anna": 500, "u_miguel": 400}
  },
  "asset_segments": [
    {"name": "operations", "target_pct": 20},
    {"name": "long_term", "target_pct": 80}
  ],
  "account_segment_allocations": {
    "acc_check_joint": {"operations": 100},
    "acc_brokerage": {"long_term": 100}
  }
}
"""


def test_core_calculations():
    snapshot = load_snapshot_from_json(SAMPLE)

    assert total_net_assets(snapshot) == 100000
    assert planned_monthly_budget_total(snapshot) == 8900

    targets = segment_target_amounts(snapshot)
    assert targets["operations"] == 20000
    assert targets["long_term"] == 80000

    current = segment_current_amounts(snapshot)
    assert current["operations"] == 10000
    assert current["long_term"] == 90000

    drift = segment_drift(snapshot)
    assert drift["operations"] == -10000
    assert drift["long_term"] == 10000


def test_report_contains_key_sections():
    snapshot = load_snapshot_from_json(SAMPLE)
    report = render_report(snapshot)

    assert "Household: Rivera Family (fam_001)" in report
    assert "Total net assets: $100,000.00" in report
    assert "Planned monthly total: $8,900.00" in report
    assert "Segment allocations:" in report
