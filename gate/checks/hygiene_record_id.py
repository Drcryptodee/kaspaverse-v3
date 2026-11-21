"""hygiene.record-id: no private record id (YYYYMMDD-<machine>-<slug>) in a public file."""
import os
import re
import sys
import tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

root = sys.argv[1]
with open(os.path.join(root, "gate", "checks.toml"), "rb") as f:
    machines = tomllib.load(f)["machines"]
rx = re.compile(r"\b20\d{6}-(?:" + "|".join(map(re.escape, machines)) + r")(?:-[a-z0-9]+)+\b")
bad = []
for rel in _lib.files(root, exclude=("gate/controls/", "gate/checks.toml")):
    for i, line in enumerate(_lib.text(root, rel).split("\n"), 1):
        if rx.search(line):
            bad.append("%s:%d" % (rel, i))
if bad:
    print("private record id in a public file: " + ", ".join(bad))
    sys.exit(1)
print("no private record ids")
