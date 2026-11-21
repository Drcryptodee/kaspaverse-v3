#!/usr/bin/env python3
"""Check commit messages against the commit standard in CONTRIBUTING.md ("Commit messages").

  check-commit-msg.py [--private] FILE        one message, as the commit-msg hook passes it (git comments ignored)
  check-commit-msg.py [--private] --all-refs  the stored message of every commit on every ref

Exit 0 when every message passes, 1 otherwise, with one line per broken rule. --private is for the maintainers'
private repository: its messages may cite its own record ids and paths, and it has its own scopes.
Only the mechanical rules live here; the rest of the standard is checked in review.
"""
import re
import subprocess
import sys

TYPES = ("feat", "fix", "perf", "refactor", "test", "docs", "build", "ci", "chore", "revert")
SCOPES_PUBLIC = (
    "wallet", "kernel", "sync", "send", "journal", "storage", "custody", "signer", "bridge", "messaging",
    "covenant", "game", "room", "tokens", "app", "ui", "web", "android", "ios", "gate", "ci", "build", "deps",
    "release", "docs", "readme", "license", "security", "contributing", "hooks", "repo",
)
SCOPES_PRIVATE = (
    "router", "readme", "charter", "constitution", "decisions", "answers", "lessons", "ideas", "registers",
    "phases", "sessions", "sittings", "research", "state", "threat", "operations", "agents", "skills",
    "settings", "gate", "tools", "hooks", "repo",
)
SUBJECT = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[a-z0-9-]+)\))?(?P<bang>!)?: (?P<summary>.+)$")
FOOTER = re.compile(r"^(BREAKING CHANGE: \S.*|Fixes #[0-9]+|Refs #[0-9]+|Co-authored-by: [^<>]+ <[^<>\s]+@[^<>\s]+>)$")
TRAILER_LIKE = re.compile(r"^[A-Za-z][A-Za-z-]*(?: [A-Z]+)?(?:: | #)")
ATTRIBUTION = re.compile(
    r"claude|anthropic|generated (?:with|by)|openai|chatgpt|copilot|\bgpt-?[0-9]|\bai[- ]generated", re.I)
PERSON_PROCESS = re.compile(
    r"\b(?:founders?|sittings?|rulings?|ruled|as requested|as asked|per (?:the )?request|the user asked)\b"
    r"|\bP[0-9](?:\.[0-9]+)?\b|\bG[0-6]\b", re.I)
FILLER = re.compile(r"\b(?:robust|seamless(?:ly)?|comprehensive|leverag(?:e|es|ed|ing)|utili[sz]e[sd]?|wip)\b", re.I)
EMPTY_FIRST = {"the", "a", "an", "this", "that", "these", "those", "it", "its", "we", "i", "my", "our", "new",
               "now", "more", "some", "all", "various", "misc", "minor", "small", "stuff", "initial", "final"}
ED_OK = {"embed", "feed", "seed", "need", "speed", "shed", "bleed", "breed", "proceed", "succeed", "exceed",
         "shred", "heed", "weed"}
ING_OK = {"bring", "string", "ring", "sing", "swing", "ping", "sting", "spring", "cling", "fling", "sling"}
S_OK = {"alias", "bias"}
PRIVATE_IDS = re.compile(r"\b20[0-9]{6}-(?:mac|ubu)(?:-[a-z0-9]+)+\b|\bv2:|\bD-[0-9]{1,4}\b")
PRIVATE_PATHS = re.compile(
    r"docs/(?:decisions|founder|registers|sittings|research)\b|gate-private|kaspaverse-v3-ops|"
    r"kaspaverse-next-intake|\bCHARTER\.md|\bCONSTITUTION\.md|\bSTATE\.md", re.I)


def strip_git_comments(text):
    out = []
    for line in text.split("\n"):
        if line.startswith("# ------------------------ >8 ------------------------"):
            break
        if line.startswith("#"):
            continue
        out.append(line.rstrip())
    while out and not out[-1]:
        out.pop()
    while out and not out[0]:
        out.pop(0)
    return out


def check(lines, private):
    """Return the broken rules of one message, given as lines with comments already removed."""
    errs = []
    if not lines:
        return ["the message is empty"]
    subject = lines[0]
    m = SUBJECT.match(subject)
    if not m:
        return ["the subject must read 'type(scope): summary' (CONTRIBUTING.md, Commit messages)"]
    if m.group("type") not in TYPES:
        errs.append("unknown type '%s'; use one of: %s" % (m.group("type"), ", ".join(TYPES)))
    scopes = SCOPES_PRIVATE if private else SCOPES_PUBLIC
    if m.group("scope") and m.group("scope") not in scopes:
        errs.append("unknown scope '%s'; use one of: %s" % (m.group("scope"), ", ".join(scopes)))
    if len(subject) > 72:
        errs.append("the subject is %d characters; at most 72" % len(subject))
    summary = m.group("summary")
    words = summary.split()
    first = words[0].lower().strip(",;:")
    if not summary[0].islower():
        errs.append("the summary starts with a lowercase verb in the imperative ('add', 'fix')")
    if len(words) < 2:
        errs.append("the summary says too little; name what changes")
    if first in EMPTY_FIRST:
        errs.append("the summary starts with '%s'; start with the verb ('add', 'fix', 'show')" % first)
    elif (first.endswith("ed") and first not in ED_OK) or (first.endswith("ing") and first not in ING_OK) or \
            (first.endswith("s") and not first.endswith(("ss", "us", "is")) and first not in S_OK):
        errs.append("'%s' is not the imperative; write 'add', not 'added', 'adds' or 'adding'" % first)
    if summary.endswith("."):
        errs.append("the subject ends with a full stop")
    if len(lines) > 1 and lines[1] != "":
        errs.append("a blank line must follow the subject")
    rest = lines[2:]
    paras, cur = [], []
    for line in rest:
        if line == "":
            if cur:
                paras.append(cur)
                cur = []
        else:
            cur.append(line)
    if cur:
        paras.append(cur)
    footers = []
    if paras and all(FOOTER.match(x) for x in paras[-1]):
        footers = paras.pop()
    elif paras:
        for x in paras[-1]:
            if TRAILER_LIKE.match(x) and not FOOTER.match(x):
                errs.append("unknown footer '%s'; footers are BREAKING CHANGE, Fixes #n, Refs #n, Co-authored-by"
                            % x.split(":")[0].split(" #")[0])
    body = [x for p in paras for x in p]
    if len(body) > 3:
        errs.append("the body is %d lines; at most 3 (longer reasons belong in the pull request)" % len(body))
    for x in body:
        if len(x) > 72:
            errs.append("a body line is %d characters; wrap at 72" % len(x))
    has_breaking = any(x.startswith("BREAKING CHANGE: ") for x in footers)
    if m.group("bang") and not has_breaking:
        errs.append("'!' in the subject needs a 'BREAKING CHANGE:' footer that says what to do")
    if has_breaking and not m.group("bang"):
        errs.append("a 'BREAKING CHANGE:' footer needs '!' in the subject")
    for x in lines:
        if not x.startswith("Co-authored-by: ") and any(ord(c) > 127 for c in x):
            errs.append("plain ASCII only: no em or en dashes, curly quotes or emoji ('%s')" % x[:40])
            break
    text = "\n".join(lines)
    checks = [(ATTRIBUTION, "no tool attribution, co-author line or session link"),
              (PERSON_PROCESS, "describe the code, not who asked or how the work went"),
              (FILLER, "no filler words")]
    if not private:
        checks += [(PRIVATE_IDS, "no private record id in a public message"),
                   (PRIVATE_PATHS, "no private record path in a public message")]
    for rx, why in checks:
        hit = rx.search(text)
        if hit:
            errs.append("%s ('%s')" % (why, hit.group(0)))
    return errs


def main(argv):
    private = "--private" in argv
    args = [a for a in argv if a not in ("--private", "--public")]
    if args == ["--all-refs"]:
        revs = subprocess.run(["git", "rev-list", "--all"], capture_output=True, text=True, check=True).stdout.split()
        bad = 0
        for rev in revs:
            msg = subprocess.run(["git", "log", "-1", "--format=%B", rev], capture_output=True, text=True,
                                 check=True).stdout
            lines = [x.rstrip() for x in msg.rstrip("\n").split("\n")]
            errs = check(lines, private)
            if errs:
                bad += 1
                print("%s %s" % (rev[:12], lines[0][:60]))
                for e in errs:
                    print("  - " + e)
        print("commit messages: %d checked, %d broken" % (len(revs), bad))
        return 1 if bad else 0
    if len(args) != 1:
        print(__doc__.strip())
        return 2
    with open(args[0], encoding="utf-8", errors="replace") as f:
        errs = check(strip_git_comments(f.read()), private)
    if errs:
        print("commit refused: the message breaks the commit standard (CONTRIBUTING.md, Commit messages)")
        for e in errs:
            print("  - " + e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
