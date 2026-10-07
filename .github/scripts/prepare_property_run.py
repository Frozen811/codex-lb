"""Record a replayable seed before running the extended property selection."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", default="")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.seed and (not args.seed.isascii() or not args.seed.isdecimal() or int(args.seed) >= 2**64):
        parser.error("seed must be an unsigned decimal integer below 2**64")
    seed = int(args.seed) if args.seed else secrets.randbits(64)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "seed": seed,
                "commit": os.environ.get("GITHUB_SHA"),
                "run_id": os.environ.get("GITHUB_RUN_ID"),
                "profile": "thorough",
                "minimum_examples": 500,
                "python": sys.version.split()[0],
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if output_path := os.environ.get("GITHUB_OUTPUT"):
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(f"seed={seed}\n")
    print(f"Extended property replay seed: {seed}")


if __name__ == "__main__":
    main()
