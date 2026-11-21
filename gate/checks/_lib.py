"""Helpers shared by the checks of this half."""
import os
import subprocess


def files(root, exclude=()):
    """Paths (relative) a commit could carry: tracked and untracked-not-ignored inside a repository, else all."""
    if os.path.isdir(os.path.join(root, ".git")):
        out = subprocess.run(["git", "-C", root, "ls-files", "-co", "--exclude-standard"],
                             capture_output=True, text=True, check=True).stdout.split("\n")
        paths = [p for p in out if p]
    else:
        paths = []
        for d, ds, fs in os.walk(root):
            ds[:] = [x for x in ds if x not in (".git", "__pycache__")]
            for f in fs:
                paths.append(os.path.relpath(os.path.join(d, f), root))
    return sorted(p for p in paths if not any(p == e or p.startswith(e.rstrip("/") + "/") for e in exclude)
                  and os.path.isfile(os.path.join(root, p)))


def text(root, rel):
    try:
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return ""
