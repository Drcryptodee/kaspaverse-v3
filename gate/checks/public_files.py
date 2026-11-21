"""public.files: the licence, policies, contributor guide and commit tooling exist; the README carries the notice."""
import os
import sys

root = sys.argv[1]
REQUIRED = ["README.md", "LICENSE", "NOTICE.md", "TRADEMARK.md", "SECURITY.md", "CONTRIBUTING.md", "AGENTS.md",
            ".githooks/commit-msg", "tools/check-commit-msg.py", "tools/allowed_signers"]
bad = ["missing: " + f for f in REQUIRED if not os.path.isfile(os.path.join(root, f))]
readme = os.path.join(root, "README.md")
if os.path.isfile(readme) and "not for real funds until release" not in open(readme, encoding="utf-8").read().lower():
    bad.append("README.md lacks the notice: not for real funds until release")
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("public files present, notice present")
