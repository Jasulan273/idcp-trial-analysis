import argparse
import json
import sys
from pathlib import Path
from .analysis import read_pairs, summarize, svg_chart

def main():
    parser = argparse.ArgumentParser(description="Compare matched coordination tasks before and with IDCP.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    try:
        pairs = read_pairs(args.input)
        summary = summarize(pairs, args.input)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (args.output / "comparison.svg").write_text(svg_chart(pairs), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
