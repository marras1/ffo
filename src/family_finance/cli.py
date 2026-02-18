from __future__ import annotations

import argparse
from pathlib import Path

from .planner import load_snapshot_from_json, render_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Family finance planner report")
    parser.add_argument("input", type=Path, help="Path to input JSON file")
    args = parser.parse_args()

    raw = args.input.read_text(encoding="utf-8")
    snapshot = load_snapshot_from_json(raw)
    print(render_report(snapshot))


if __name__ == "__main__":
    main()
