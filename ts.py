#!/usr/bin/env python3
"""ts — timestamp each line of stdin."""

import argparse
import sys
import time
from datetime import datetime


def parse_args():
    p = argparse.ArgumentParser(
        prog="ts",
        description="Timestamp each line of stdin.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  long-running-cmd | ts
  long-running-cmd | ts '%Y-%m-%dT%H:%M:%S'
  long-running-cmd | ts -r
  long-running-cmd | ts -i
""",
    )
    p.add_argument(
        "format",
        nargs="?",
        default="%b %d %H:%M:%S",
        help="strftime format string (default: '%%b %%d %%H:%%M:%%S')",
    )
    p.add_argument(
        "-r",
        "--relative",
        action="store_true",
        help="show time elapsed since first line",
    )
    p.add_argument(
        "-i",
        "--incremental",
        action="store_true",
        help="show time elapsed since previous line",
    )
    p.add_argument(
        "-s",
        "--seconds",
        action="store_true",
        help="with -r/-i: show fractional seconds (e.g. 0.123s)",
    )
    return p.parse_args()


def format_elapsed(seconds: float, show_fractional: bool) -> str:
    if show_fractional and seconds < 60:
        return f"{seconds:.3f}s"
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    if m:
        return f"{m:d}:{s:02d}"
    return f"{s:d}s"


def main():
    args = parse_args()

    if args.relative and args.incremental:
        print("ts: --relative and --incremental are mutually exclusive", file=sys.stderr)
        sys.exit(1)

    first_time = None
    prev_time = None

    try:
        for line in sys.stdin:
            now = time.monotonic()
            wall = datetime.now()

            if args.relative or args.incremental:
                if first_time is None:
                    first_time = now
                if prev_time is None:
                    prev_time = now

                if args.relative:
                    elapsed = now - first_time
                else:
                    elapsed = now - prev_time
                    prev_time = now

                prefix = format_elapsed(elapsed, args.seconds)
            else:
                prefix = wall.strftime(args.format)

            sys.stdout.write(f"{prefix} {line}")
            sys.stdout.flush()

    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
