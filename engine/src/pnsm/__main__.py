"""CLI: ``python -m pnsm <command>``."""

from __future__ import annotations

import argparse
import sys

from pathlib import Path

from pnsm import export, load
from pnsm.config import CollectionConfig

ENGINE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ENGINE_DIR / "config" / "wc1970_brazil.yaml"


def cmd_fetch(args: argparse.Namespace) -> int:
    match_ids = load.fetch_season(args.competition, args.season, team=args.team)
    print(f"{len(match_ids)} partidas em cache em {load.DEFAULT_CACHE_DIR}")
    for match_id in match_ids:
        print(f"  {match_id}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    cfg = CollectionConfig.from_yaml(args.config)
    try:
        written = export.export_collection(cfg)
    except export.validate.ValidationError as err:
        print(f"Export cancelado, validação falhou:\n{err}", file=sys.stderr)
        return 1
    print(f"{len(written)} arquivos em {cfg.output_dir}")
    return 0


def cmd_post(args: argparse.Namespace) -> int:
    from pnsm.report.post import render_post  # matplotlib only needed here

    cfg = CollectionConfig.from_yaml(args.config)
    meta = load.find_match(args.match, cfg.competition_id, cfg.season_id)
    data = export.build_match(meta, load.load_events(args.match), load.load_lineups(args.match), cfg)
    out = Path(args.out) if args.out else ENGINE_DIR / "outputs" / f"post_{args.match}.png"
    print(render_post(data, out, min_pair=cfg.min_pair_passes))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pnsm", description="F.I.L · Passing Network + Shot Map")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="baixa e cacheia partidas, eventos e escalações de uma temporada")
    fetch.add_argument("--competition", type=int, required=True)
    fetch.add_argument("--season", type=int, required=True)
    fetch.add_argument("--team", help="só as partidas desta equipe (nome StatsBomb, ex.: Brazil)")
    fetch.set_defaults(func=cmd_fetch)

    exp = sub.add_parser("export", help="valida e gera os JSONs do site")
    exp.add_argument("--config", required=True, help="ex.: config/wc1970_brazil.yaml")
    exp.set_defaults(func=cmd_export)

    post = sub.add_parser("post", help="gera o PNG 1080×1350 do post do LinkedIn")
    post.add_argument("--match", type=int, required=True)
    post.add_argument("--config", default=str(DEFAULT_CONFIG))
    post.add_argument("--out", help="padrão: engine/outputs/post_{match}.png")
    post.set_defaults(func=cmd_post)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
