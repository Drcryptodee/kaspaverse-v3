"""hooks.commit-msg: the hook exists and runs the checker, which refuses planted bad messages and accepts good ones."""
import os
import subprocess
import sys
import tempfile

root = sys.argv[1]
hook = os.path.join(root, ".githooks", "commit-msg")
checker = os.path.join(root, "tools", "check-commit-msg.py")
if not os.path.isfile(hook) or not os.access(hook, os.X_OK):
    print("missing or not executable: .githooks/commit-msg")
    sys.exit(1)
if "tools/check-commit-msg.py" not in open(hook, encoding="utf-8").read():
    print(".githooks/commit-msg does not run tools/check-commit-msg.py")
    sys.exit(1)
BAD = ["Fixed bugs.\n", "feat(wallet): Added the fee preview\n", "chore: wip\n",
       "feat(wallet): show the fee preview.\n", "fix(sync): resume \u2014 after a restart\n"]
GOOD = ["feat(wallet): show the network fee before signing\n", "docs(readme): explain how to verify a release\n"]
wrong = []
with tempfile.TemporaryDirectory() as tmp:
    for i, (msg, want) in enumerate([(m, 1) for m in BAD] + [(m, 0) for m in GOOD]):
        p = os.path.join(tmp, "msg%d" % i)
        with open(p, "w", encoding="utf-8") as f:
            f.write(msg)
        rc = subprocess.run([sys.executable, "-I", checker, "--public", p], capture_output=True).returncode
        if (rc != 0) != (want == 1):
            wrong.append(("accepted " if rc == 0 else "refused ") + repr(msg.strip()))
if wrong:
    print("the checker misjudged: " + "; ".join(wrong))
    sys.exit(1)
print("hook runs the checker; checker refuses %d planted messages and accepts %d" % (len(BAD), len(GOOD)))
