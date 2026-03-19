#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formula", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--sdist-url", required=True)
    parser.add_argument("--sdist-sha256", required=True)
    parser.add_argument("--tag")
    parser.add_argument("--bottle-json-dir")
    return parser.parse_args()


def update_source_fields(text: str, repo: str, sdist_url: str, sdist_sha256: str) -> str:
    text = re.sub(r'  homepage ".*"\n', f'  homepage "https://github.com/{repo}"\n', text, count=1)
    text = re.sub(r'  url ".*"\n', f'  url "{sdist_url}"\n', text, count=1)
    text = re.sub(r'  sha256 ".*"\n', f'  sha256 "{sdist_sha256}"\n', text, count=1)
    return re.sub(r'\n  bottle do\n(?:    .*\n)+?  end\n', "\n", text, count=1)


def build_bottle_block(repo: str, tag: str, bottle_json_dir: Path) -> str:
    entries: list[str] = []
    rebuilds: set[int] = set()
    for json_path in sorted(bottle_json_dir.rglob("*.json")):
        data = json.loads(json_path.read_text())
        bottle = next(iter(data.values()))
        rebuild = bottle["bottle"].get("rebuild")
        if rebuild is not None:
            rebuilds.add(rebuild)
        for tag_name, payload in sorted(bottle["bottle"]["tags"].items()):
            cellar = payload.get("cellar", "any_skip_relocation")
            cellar_value = ":any_skip_relocation" if cellar == "any_skip_relocation" else f'"{cellar}"'
            entries.append(f'    sha256 cellar: {cellar_value}, {tag_name}: "{payload["sha256"]}"')

    if not entries:
        raise SystemExit("No bottle JSON files found")

    bottle_block = "  bottle do\n"
    bottle_block += f'    root_url "https://github.com/{repo}/releases/download/{tag}"\n'
    if len(rebuilds) > 1:
        raise SystemExit(f"Inconsistent bottle rebuild values: {sorted(rebuilds)}")
    if rebuilds:
        rebuild = next(iter(rebuilds))
        if rebuild:
            bottle_block += f"    rebuild {rebuild}\n"
    bottle_block += "\n".join(entries)
    bottle_block += "\n  end\n"
    return bottle_block


def insert_bottle_block(text: str, bottle_block: str) -> str:
    return re.sub(
        r'((?:  depends_on .*\n)+)',
        lambda match: f'{match.group(1)}\n{bottle_block}\n',
        text,
        count=1,
    )


def main() -> None:
    args = parse_args()
    formula_path = Path(args.formula)
    text = update_source_fields(
        formula_path.read_text(),
        repo=args.repo,
        sdist_url=args.sdist_url,
        sdist_sha256=args.sdist_sha256,
    )

    if args.bottle_json_dir:
        if not args.tag:
            raise SystemExit("--tag is required when --bottle-json-dir is set")
        bottle_block = build_bottle_block(args.repo, args.tag, Path(args.bottle_json_dir))
        text = insert_bottle_block(text, bottle_block)

    formula_path.write_text(text)


if __name__ == "__main__":
    main()
