# ts — Build Notes

**Seeded:** 2026-10-08 (Week 50)
**Status:** Built, tested, 41/41

## The Problem

`ts` from moreutils is the canonical answer to "timestamp my output." But moreutils isn't installed by default anywhere, and it's a surprising package to install just for one utility. The Python stdlib has everything needed.

## Design Choices

**Three modes:**
- Default (wall clock): matches `ts` from moreutils exactly — `%b %d %H:%M:%S`
- `-r` (relative): elapsed since first line — good for "how long has this been running?"
- `-i` (incremental): elapsed since previous line — good for "where is the slow step?"

**Fractional seconds flag (`-s`):** Added alongside `-r`/`-i`. When elapsed < 60s, shows milliseconds. Above 60s, shows `h:mm:ss` or `m:ss` — fractional parts don't matter at that scale.

**Format string as positional arg:** Matches moreutils `ts` behavior — `ts '%Y-%m-%dT%H:%M:%S'` just works.

**No buffering workaround:** Output buffers in the upstream process can delay timestamps. This is a fundamental shell pipeline limitation, not a bug. Documented in README.

## What Works

- Default wall clock with custom strftime format
- `-r` relative elapsed
- `-i` incremental elapsed
- `-s` fractional seconds with elapsed modes
- Mutual exclusion: `-r` and `-i` together exit with error
- BrokenPipeError and KeyboardInterrupt handled cleanly
- Empty stdin: no output, exit 0
- Lines without trailing newlines

## What Doesn't (by design)

- No timezone-aware output for `-r`/`-i` (elapsed is timedelta, not a timestamp)
- No `--utc` flag — strftime handles this via `%Z` if needed
- No debouncing or rate limiting

## Tests

41 checks covering: default format, custom formats, -r, -i, -s, mutual exclusion, empty stdin, format_elapsed math, help output.
