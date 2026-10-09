# ts

Prepend a timestamp to each line of stdin.

```
long-running-cmd | ts
long-running-cmd | ts '%Y-%m-%dT%H:%M:%S'
long-running-cmd | ts -r
make build | ts -i -s
```

Replaces the `ts` command from `moreutils` — no package manager needed, pure Python stdlib.

## Install

```
curl -O https://github.com/kithfoss/ts/releases/latest/download/ts.py
chmod +x ts.py
sudo mv ts.py /usr/local/bin/ts
```

Or just `python3 ts.py` directly.

## Usage

```
usage: ts [-h] [-r] [-i] [-s] [format]

positional arguments:
  format             strftime format string (default: '%b %d %H:%M:%S')

options:
  -r, --relative     show time elapsed since first line
  -i, --incremental  show time elapsed since previous line
  -s, --seconds      with -r/-i: show fractional seconds (e.g. 0.123s)
```

## Examples

### Default (wall clock)

```
$ long-cmd | ts
Oct 08 16:07:11 starting build...
Oct 08 16:07:13 compiling...
Oct 08 16:07:15 done.
```

### ISO 8601

```
$ long-cmd | ts '%Y-%m-%dT%H:%M:%S'
2026-10-08T16:07:11 starting build...
2026-10-08T16:07:13 compiling...
```

### Elapsed since start (`-r`)

```
$ make test | ts -r
0s Running tests...
2s test_auth passed
5s test_db passed
5s All done.
```

### Time between lines (`-i`)

```
$ make build | ts -i -s
0.001s starting build
0.834s compiled 42 files
0.012s linked
```

### Elapsed with fractional seconds (`-r -s`)

```
$ slow-script | ts -r -s
0.000s initializing
0.123s step 1
1.456s step 2
```

## Limitations

- Reads line by line — output buffers in the connected process may delay timestamps.
- Elapsed modes use monotonic clock; wall-clock mode uses system time.
- Elapsed times ≥ 60 seconds do not show fractional parts even with `-s`.
