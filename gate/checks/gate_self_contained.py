"""gate.self-contained: no gate file reads above this repository, the home folder or the environment."""
import os
import re
import sys

root = sys.argv[1]
parts = [r"[\"']\.\./", "os" + r"\.pardir", r"\$" + "HOME", r"[\"']~/", "expand" + "user", "os" + r"\.environ",
         "get" + "env"]
rx = re.compile("|".join(parts))
bad = []
gate = os.path.join(root, "gate")
for d, ds, fs in os.walk(gate):
    ds[:] = [x for x in ds if x not in ("controls", "__pycache__", "out")]
    for f in fs:
        if f.endswith((".py", ".toml")):
            p = os.path.join(d, f)
            for i, line in enumerate(open(p, encoding="utf-8"), 1):
                if rx.search(line):
                    bad.append("%s:%d" % (os.path.relpath(p, root), i))
if bad:
    print("reaches outside the repository: " + ", ".join(bad))
    sys.exit(1)
print("the gate reads only this repository")
