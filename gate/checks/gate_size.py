"""gate.size: no gate file is over 300 lines, and no check file is more than 25% comment lines."""
import os
import sys

root = sys.argv[1]
gate = os.path.join(root, "gate")
bad = []
for d, ds, fs in os.walk(gate):
    ds[:] = [x for x in ds if x not in ("controls", "__pycache__", "out")]
    for f in fs:
        if not f.endswith((".py", ".toml")):
            continue
        p = os.path.join(d, f)
        lines = open(p, encoding="utf-8").read().split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        rel = os.path.relpath(p, root)
        if len(lines) > 300:
            bad.append("%s: %d lines (at most 300)" % (rel, len(lines)))
        if os.path.basename(d) == "checks" and lines:
            share = sum(1 for x in lines if x.strip().startswith("#")) / len(lines)
            if share > 0.25:
                bad.append("%s: %d%% comment lines (at most 25%%)" % (rel, round(share * 100)))
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("gate files within size")
