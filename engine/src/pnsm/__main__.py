"""CLI: ``python -m pnsm <command>``."""

from __future__ import annotations

import argparse
import sys

from pnsm import load


def cmd_fetch(args: argparse.Namespace) -> int:
    match_ids = load.fetch_season(args.competition, args.season, team=args.team)
    print(f"{len(match_ids)} partidas em cache em {load.DEFAULT_CACHE_DIR}")
    for match_id in match_ids:
        print(f"  {match_id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pnsm", description="F.I.L · Passing Network + Shot Map")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="baixa e cacheia partidas, eventos e escalações de uma temporada")
    fetch.add_argument("--competition", type=int, required=True)
    fetch.add_argument("--season", type=int, required=True)
    fetch.add_argument("--team", help="só as partidas desta equipe (nome StatsBomb, ex.: Brazil)")
    fetch.set_defaults(func=cmd_fetch)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
