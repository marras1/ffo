# Family Finance Planner Specification

## Goal
Build a lightweight planner that models a family household with multiple users, multiple accounts, a shared budget, and segmented asset allocations.

## Functional requirements
1. Ingest household data from JSON.
2. Support user roles and account ownership (joint/personal).
3. Calculate:
   - total net assets
   - target dollar allocation per segment from target percentages
   - current allocation by segment based on account-to-segment mapping
   - drift by segment (current - target)
4. Track budget totals:
   - shared required
   - shared flexible
   - per-user discretionary totals
   - overall planned monthly spend
5. Emit a plain-text report with:
   - household summary
   - budget summary
   - allocation summary sorted by largest absolute drift

## Non-functional requirements
- Pure Python 3.10+.
- No external dependencies.
- Include unit tests for calculations and report generation.
- Provide a small executable CLI entrypoint.

## Input shape
JSON object with keys:
- household
- accounts
- budget
- asset_segments
- account_segment_allocations (optional; defaults to 100% operations)

## Output
A deterministic text report suitable for terminal and CI logs.
