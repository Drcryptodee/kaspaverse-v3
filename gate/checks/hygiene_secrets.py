"""hygiene.secrets: no secret-shaped file and no private key or token material in what a commit could carry."""
import fnmatch
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

root = sys.argv[1]
NAMES = ["*.keystore", "*.jks", "*.p12", "*.pfx", "*.pem", "*key.properties", ".env", ".env.*", "id_rsa",
         "id_ed25519", "id_ecdsa"]
BODY = re.compile("|".join([
    "-----BEGIN [A-Z ]*PRIV" + "ATE KEY-----", "AKIA[0-9A-Z]{16}", "gh[pousr]_[A-Za-z0-9]{36}",
    "github_pat_[A-Za-z0-9_]{40,}", "xox[abprs]-[A-Za-z0-9-]{10,}", "sk-ant-[A-Za-z0-9_-]{20,}"]))
bad = []
for rel in _lib.files(root, exclude=("gate/controls/",)):
    base = os.path.basename(rel)
    if base != ".env.example" and any(fnmatch.fnmatch(base, n) for n in NAMES):
        bad.append("secret-shaped file: " + rel)
    if BODY.search(_lib.text(root, rel)):
        bad.append("private key or token material: " + rel)
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("no secret-shaped files or key material")
