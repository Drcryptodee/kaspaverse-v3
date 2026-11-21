# Contributing to KaspaVerse

KaspaVerse is a Kaspa wallet and covenant arcade that will hold real money. Every change lands through a pull request,
passes the gate, and is described in plain, exact words.

## How a change lands

- Work on a branch, never on `main`. `main` takes squash merges from pull requests whose checks are green, and its
  history stays linear. Nothing is ever force-pushed.
- One logical change per commit, and each commit passes the gate on its own: `python3 gate/run.py`.
- Commits are signed, and the commit-message hook runs on every commit. Once per clone:
  `git config core.hooksPath .githooks`. Never skip it with `--no-verify`.
- To verify signatures locally: `git config gpg.ssh.allowedSignersFile "$PWD/tools/allowed_signers"`, then
  `git log --show-signature`.
- A security problem never goes in a public issue or pull request: see `SECURITY.md`.

## Commit messages

This is the project's one standard for commit messages. It follows Conventional Commits 1.0.0 for the shape and git's
own advice for the form: a short summary line, a blank line, then a body only when it is needed. The hook in
`.githooks/commit-msg` refuses a message that breaks a mechanical rule before the commit exists, and the gate checks
every commit on every ref again, so a squash message or a contributor's commit cannot slip through. Review checks the
rest.

### The shape

- **Subject:** `type(scope): summary`, at most 72 characters, plain ASCII. The summary starts with a lowercase verb in
  the imperative ("add", "fix", never "added", "adds" or "adding") and ends with no full stop. It completes the
  sentence *If applied, this commit will ...*
- **Types:** `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`, `revert`.
- **Scopes** (optional, one of): `wallet`, `kernel`, `sync`, `send`, `journal`, `storage`, `custody`, `signer`,
  `bridge`, `messaging`, `covenant`, `game`, `room`, `tokens`, `app`, `ui`, `web`, `android`, `ios`, `gate`, `ci`,
  `build`, `deps`, `release`, `docs`, `readme`, `license`, `security`, `contributing`, `hooks`, `repo`. A new scope is
  added here and in `tools/check-commit-msg.py` in the same change.
- **Body:** only when the subject and the diff cannot show why. At most three lines, wrapped at 72. Anything longer
  belongs in the pull request or the docs.
- **Footers:** only when they carry meaning. `BREAKING CHANGE:` (with `!` after the type or scope) when a saved
  wallet, a file format or a covenant template changes, saying what the user or developer must do. `Fixes #n` or
  `Refs #n` for a public issue. `Co-authored-by` only for a real person.

### The voice

A plain fact about the code. Never who asked, who decided or how the work went: no people's names, devices or work
sessions, no project phases or internal rulings. No filler (*robust*, *seamless*, *comprehensive*, *leverage*), no
metaphors, no em or en dashes, no emoji.

- **No tool attribution.** No co-author line, "Generated with" line or session link for any tool or assistant.
- **No private references.** Messages here never cite an internal record id or a path outside this repository.
- **Security fixes** say what is fixed, never how to exploit it, until a release carries the fix.

### Beyond commits

A pull request's title is its squash commit's subject, and the squash message is written to this standard, never
GitHub's default list of commits. Pull request descriptions, tags and release notes use the same voice; release notes
are built from `feat`, `fix` and `perf`.

### Examples

Good:
- `feat(wallet): show the network fee before signing`
- `fix(sync): resume from the last checked block after a restart`
- `docs(readme): explain how to verify a release`

Avoid:
- `feat(covenant): the duel's exit table is a machine, 31,098 states proven`: an essay, not a change.
- `fix: the founder's phone could not send`: a person, not the code.
- `chore: apply D-179 as ruled`: a private id and process talk.
- `Fixed bugs.`: says nothing, in the wrong tense.

The maintainers' private repository follows this standard too, with one difference: its messages may cite its own
record ids, and it has its own scopes.

## Code comments

Comments are concise and say what and why, straight to the point. No filler, no history of earlier versions of this
app, no person, work session or date, no private record ids (an invariant's number, `INV-n`, is fine), and no em
dashes. The gate catches what a lint can; review catches the rest.
