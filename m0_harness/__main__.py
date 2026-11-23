import argparse
import json
from pathlib import Path
import sys

from .corpus import json_default, run_corpus


def main():
    parser = argparse.ArgumentParser(description="Compare M0 fixture outcomes with the checked-in inventory")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    # Reports must never overwrite the fixture inventory or any fixture source.
    try:
        config = json.loads(args.manifest.read_text(encoding="utf-8"))
        protected = [args.manifest.resolve().parent]
        protected.extend((args.manifest.resolve().parent / b["root"]).resolve()
                         for b in config["bundles"] + config.get("registration_attempts", []))
        if args.output and any(args.output.resolve().is_relative_to(root) for root in protected):
            parser.error("report output must be outside the fixture directory and bundle roots")
        report = run_corpus(args.manifest)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Cannot run corpus: {exc}\n")
    rendered = json.dumps(report, indent=2, default=json_default, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    failures = report["expectation_failures"]
    summary_stream = sys.stdout if args.output else sys.stderr
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=summary_stream)
    else:
        print(f"Matched fixture expectations for {len(report['bundles'])} bundles; sources unchanged.", file=summary_stream)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
