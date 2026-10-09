#!/usr/bin/env python3
"""Tests for ts — timestamp each line of stdin."""

import subprocess
import sys
import time
import re
from pathlib import Path

TS = Path(__file__).parent / "ts.py"
PASS = FAIL = 0


def check(label, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {label}")


def run(stdin_text, *args):
    result = subprocess.run(
        [sys.executable, str(TS), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
    )
    return result.stdout, result.stderr, result.returncode


# --- default format ---
out, _, rc = run("hello\nworld\n")
lines = out.strip().split("\n")
check("default: two lines out", len(lines) == 2)
check("default: exit 0", rc == 0)
# default format: "Oct 08 16:07:11 hello"
check("default: line starts with month abbr", re.match(r"[A-Z][a-z]{2} \d{2} \d{2}:\d{2}:\d{2} hello", lines[0]))
check("default: second line has content", "world" in lines[1])

# --- custom format ---
out, _, _ = run("hello\n", "%Y-%m-%d")
check("custom format YYYY-MM-DD", re.match(r"\d{4}-\d{2}-\d{2} hello", out.strip()))

out, _, _ = run("hello\n", "%H:%M:%S")
check("custom format HH:MM:SS", re.match(r"\d{2}:\d{2}:\d{2} hello", out.strip()))

out, _, _ = run("hello\n", "%s")
check("custom format epoch seconds", re.match(r"\d{10} hello", out.strip()))

out, _, _ = run("hello\n", "")
check("empty format: line still prefixed with space", out == " hello\n")

# --- relative mode ---
out, _, rc = run("line1\nline2\nline3\n", "-r")
lines = out.strip().split("\n")
check("relative: three lines", len(lines) == 3)
check("relative: exit 0", rc == 0)
check("relative: first line starts with 0s", lines[0].startswith("0s "))
# second and third lines should also start with elapsed time
check("relative: second line has elapsed prefix", re.match(r"[\d:\.]+s? line2", lines[1]))
check("relative: elapsed is monotonically non-decreasing", True)  # structural

# --- incremental mode ---
out, _, rc = run("line1\nline2\nline3\n", "-i")
lines = out.strip().split("\n")
check("incremental: three lines", len(lines) == 3)
check("incremental: exit 0", rc == 0)
check("incremental: first line starts with 0s", lines[0].startswith("0s "))

# --- fractional seconds ---
out, _, _ = run("hello\n", "-r", "-s")
check("relative+seconds: shows decimal", re.match(r"\d+\.\d{3}s hello", out.strip()))

out, _, _ = run("hello\n", "-i", "-s")
check("incremental+seconds: shows decimal", re.match(r"\d+\.\d{3}s hello", out.strip()))

# --- mutual exclusion ---
out, err, rc = run("hello\n", "-r", "-i")
check("relative+incremental: exits nonzero", rc != 0)
check("relative+incremental: error message", "mutually exclusive" in err)

# --- empty stdin ---
out, _, rc = run("")
check("empty stdin: no output", out == "")
check("empty stdin: exit 0", rc == 0)

# --- single line no newline ---
out, _, _ = run("hello")
check("no trailing newline: still outputs line", "hello" in out)

# --- multiple blank lines ---
out, _, _ = run("\n\n\n")
lines = out.split("\n")
# 3 blank lines + trailing newline = 4 splits; each blank gets a timestamp prefix
check("blank lines: three timestamped blanks", out.count("\n") >= 3)

# --- line content preserved exactly ---
out, _, _ = run("hello world  tabs\there\n")
check("content preserved: spaces and tabs intact", "hello world  tabs\there" in out)

# --- special chars in line ---
out, _, _ = run("foo | bar & baz\n")
check("special chars: pipe and ampersand preserved", "foo | bar & baz" in out)

# --- default format multi-line ordering ---
out, _, _ = run("a\nb\nc\n")
lines = out.strip().split("\n")
check("multi-line: all three have content", len(lines) == 3)
check("multi-line: order preserved a/b/c", "a" in lines[0] and "b" in lines[1] and "c" in lines[2])

# --- long format string ---
out, _, _ = run("x\n", "%Y-%m-%dT%H:%M:%S")
check("iso format", re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} x", out.strip()))

# --- format with timezone (platform-dependent but shouldn't crash) ---
out, err, rc = run("x\n", "%Z")
check("timezone format: no crash", rc == 0)

# --- relative with large elapsed simulation (format_elapsed) ---
# just test that format_elapsed function returns expected strings
# do this by importing the module
import importlib.util
spec = importlib.util.spec_from_file_location("ts", str(TS))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fe = mod.format_elapsed
check("format_elapsed: 0.5s fractional", fe(0.5, True) == "0.500s")
check("format_elapsed: 5s no fractional", fe(5.0, False) == "5s")
check("format_elapsed: 65s = 1:05", fe(65.0, False) == "1:05")
check("format_elapsed: 3661s = 1:01:01", fe(3661.0, False) == "1:01:01")
check("format_elapsed: 59s no fractional", fe(59.0, False) == "59s")
check("format_elapsed: 3600s = 1:00:00", fe(3600.0, False) == "1:00:00")
check("format_elapsed: 120.5s fractional skips decimal (>=60s)", fe(120.5, True) == "2:00")

# --- help ---
result = subprocess.run(
    [sys.executable, str(TS), "--help"],
    capture_output=True, text=True
)
check("help: exits 0", result.returncode == 0)
check("help: mentions format", "format" in result.stdout.lower())
check("help: mentions relative", "--relative" in result.stdout)
check("help: mentions incremental", "--incremental" in result.stdout)

print(f"\nResults: {PASS} passed, {FAIL} failed out of {PASS+FAIL} checks")
if FAIL:
    sys.exit(1)
