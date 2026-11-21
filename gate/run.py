#!/usr/bin/env python3
"""The gate's runner. One runner serves both halves; each half has its own manifest.

  python3 gate/run.py                                   the public half, run from this repository's root
  python3 code/gate/run.py --root . --manifest gate-private/checks.toml    the private half, from the ops root
  options: --no-controls (skip the planted cases), --verbose (one line per check)

A check is one file, run as `python3 -I <file> <root>`: exit 0 PASS, 1 FAIL, 3 subject absent. Subject absent is
FAIL unless the manifest's `applies_if` path is absent (then N/A, never PASS). The roster is checked both ways. Every
check has control cases under controls/<id>/<case>/case.toml: `expect` (pass, fail or na), then [[write]] (path, and
`text`, or `lines` with `comment_lines`) and [[remove]] (path). The runner copies the root, applies the case and runs
the check on the copy; a case with the wrong verdict means the check has gone blind, and the gate is RED.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

if sys.version_info < (3, 11):
    print("GATE: RED (the gate needs Python 3.11 or later; this is %d.%d)" % sys.version_info[:2])
    sys.exit(1)
import tomllib  # noqa: E402

SKIP = shutil.ignore_patterns(".git", "__pycache__", "out", ".DS_Store")


def run_check(root, chk, gate_dir):
    path = os.path.join(gate_dir, "checks", chk["file"])
    try:
        p = subprocess.run([sys.executable, "-I", path, root], capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "FAIL", "timed out"
    why = (p.stdout + p.stderr).strip()
    if p.returncode == 0:
        return "PASS", why
    if p.returncode == 3:
        gate = chk.get("applies_if")
        if gate and not os.path.exists(os.path.join(root, gate)):
            return "N/A", gate + " absent, so the check does not apply"
        return "FAIL", "subject absent where the check applies: " + why
    return "FAIL", why


def roster(man, gate_dir):
    listed = {c["file"] for c in man["check"]}
    cdir = os.path.join(gate_dir, "checks")
    on_disk = {n for n in os.listdir(cdir) if n.endswith(".py") and not n.startswith("_")}
    bad = ["check file not in the manifest: " + f for f in sorted(on_disk - listed)]
    bad += ["manifest names a missing file: " + f for f in sorted(listed - on_disk)]
    ids = [c["id"] for c in man["check"]]
    bad += ["duplicate check id: " + i for i in sorted({i for i in ids if ids.count(i) > 1})]
    return bad


def apply_case(dst, case):
    for r in case.get("remove", []):
        p = os.path.join(dst, r["path"])
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    for w in case.get("write", []):
        p = os.path.join(dst, w["path"])
        os.makedirs(os.path.dirname(p) or dst, exist_ok=True)
        if "text" in w:
            body = w["text"]
        else:
            n, c = w["lines"], w.get("comment_lines", 0)
            body = "".join("# planted comment\n" if i < c else "x%d = %d\n" % (i, i) for i in range(n))
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        if w.get("executable"):
            os.chmod(p, 0o755)


def controls(root, man, gate_dir):
    bad, n = [], 0
    for chk in man["check"]:
        cdir = os.path.join(gate_dir, "controls", chk["id"])
        cases = sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []
        cases = [c for c in cases if os.path.isfile(os.path.join(cdir, c, "case.toml"))]
        if not cases:
            bad.append("%s: no control cases" % chk["id"])
            continue
        for name in cases:
            with open(os.path.join(cdir, name, "case.toml"), "rb") as f:
                case = tomllib.load(f)
            with tempfile.TemporaryDirectory() as tmp:
                dst = os.path.join(tmp, "root")
                shutil.copytree(root, dst, ignore=SKIP, symlinks=True)
                apply_case(dst, case)
                dst_gate = os.path.join(dst, os.path.relpath(gate_dir, root))
                verdict, why = run_check(dst, chk, dst_gate)
            n += 1
            want = case["expect"].upper()
            if verdict != want:
                bad.append("%s/%s: expected %s, got %s (%s)" % (chk["id"], name, want, verdict, why[:120]))
    return bad, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--manifest", default="gate/checks.toml")
    ap.add_argument("--no-controls", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    mpath = os.path.join(root, a.manifest)
    gate_dir = os.path.dirname(mpath)
    with open(mpath, "rb") as f:
        man = tomllib.load(f)
    fails = roster(man, gate_dir)
    for f in fails:
        print("FAIL  roster: " + f)
    counts = {"PASS": 0, "FAIL": 0, "N/A": 0}
    for chk in man["check"]:
        verdict, why = run_check(root, chk, gate_dir)
        counts[verdict] += 1
        if verdict == "FAIL":
            fails.append(chk["id"])
            lines = why.splitlines() or ["(no output)"]
            print("FAIL  %s: %s" % (chk["id"], lines[0][:160]))
            for extra in lines[1:20]:
                print("      " + extra[:160])
        elif a.verbose:
            print("%-4s  %s" % (verdict, chk["id"]))
    ctl = "skipped"
    if not a.no_controls:
        bad, n = controls(root, man, gate_dir)
        for b in bad:
            print("FAIL  control " + b)
        fails += bad
        ctl = "%d of %d behaved" % (n - len([b for b in bad if "no control cases" not in b]), n)
    verdict = "RED" if fails else "GREEN"
    print("GATE %s: %s  checks %d pass, %d n/a, %d fail  controls %s" % (
        man["half"], verdict, counts["PASS"], counts["N/A"], counts["FAIL"], ctl))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
