from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__, render
from .plan import load, validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="adoptkit",
                                     description="Write the adoption pack a tool needs before it ships.")
    parser.add_argument("--version", action="version", version=f"adoptkit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="validate the plan and write the pack")
    run.add_argument("--config", default="config/plan.json")
    run.add_argument("--out", default="out")
    run.add_argument("--json", action="store_true")

    check = sub.add_parser("check", help="validate only, exit 2 on gaps")
    check.add_argument("--config", default="config/plan.json")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        plan = load(args.config)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    problems = validate(plan)
    if problems:
        print("not adoptable yet:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 2

    if args.command == "check":
        print(f"ok: {render.short_summary(plan)}")
        return 0

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "adoption-pack.md")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render.render(plan))
    if args.json:
        print(json.dumps({"tool": plan.tool, "owner": plan.owner,
                          "ritual": plan.ritual.name if plan.ritual else "",
                          "metric": plan.metric.name if plan.metric else "",
                          "weeks": plan.weeks(), "pack": path}, indent=2))
    else:
        print(f"ok · {render.short_summary(plan)} · pack: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
