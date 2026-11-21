# Security policy

KaspaVerse is a non-custodial wallet: it holds the keys to real funds on Kaspa, a public ledger nothing can roll back.
A key leak is total and silent, and a covenant bug is fund loss, not a hotfix. Security is the product.

If you are deciding whether something is worth reporting: **if it could move, freeze, or reveal funds or keys that
should not move, freeze, or be revealed, report it.** Development builds may hold small real balances, so a finding
can matter before the first release.

## Reporting a vulnerability

Please do not open a public issue or pull request for a security problem. Use GitHub's private vulnerability reporting:
the repository's **Security** tab, then **Report a vulnerability**. A contact address on `kaspaverse.app` will be added
here once its mail exists.

Include what you found and where (a file and line, a commit or a build), how to reproduce it, and the impact you
believe it has. A failing test or a minimal reproduction is ideal. We acknowledge reports within a few days, keep you
updated, and credit you in the advisory unless you ask us not to. Please allow time for a fix to ship before any
public disclosure. There is no bug bounty at this stage.

## What is in scope

- a secret leaving the Rust core, reaching managed memory, or being logged or stored in the clear;
- key or seed extraction, a bypass of the platform vault or its lockout;
- a signed transaction that differs from what the review screen showed, or a broadcast the user did not approve;
- a covenant state with no exit a player can take alone;
- a dependency, build or release provenance weakness;
- a source the app reaches that is not named to the user, or that learns more than the app says.

Out of scope: a compromised operating system, physical attacks on an unlocked device, and attacks on third-party
services the user chose.
