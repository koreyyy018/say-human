"""Sync public corpora/prompts into importlib.resources package copies."""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIR = [
    *( (ROOT / "data" / name, ROOT / "src/sayhuman/assets" / name)
       for name in ("concepts.json", "concepts.zh-CN.json", "gold-standard.json", "corporate-phrases.json") ),
    *( (ROOT / "prompts" / name, ROOT / "src/sayhuman/assets" / name)
       for name in ("jargon-aligner.md", "corporate-jargon-optimizer.md", "gold-standard-fewshots.md") ),
]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail rather than update drifted copies")
    args = parser.parse_args(argv)
    errors = []
    for source, target in PAIR:
        if not source.exists():
            errors.append(f"Missing source {source}")
            continue
        if not target.exists() or source.read_bytes() != target.read_bytes():
            if args.check:
                errors.append(f"Out-of-sync asset: {target.relative_to(ROOT)}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
                print(f"Synced {target.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors))
        return 1
    print("Asset sync verified" if args.check else "Asset synchronization complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
