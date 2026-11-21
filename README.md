# KaspaVerse

A wallet and a covenant arcade for [Kaspa](https://kaspa.org), built for how Kaspa works: each output is its own small
machine. One Rust kernel holds the keys on Android, iOS and the web, shows only what the chain can prove, and takes in
what Kaspa ships next through prepared seams. Messaging speaks the Kasia and KaChat wires. The first game, Attack &
Defend, is written in Argent.

> **Not for real funds until release.** This repository is at the start of its build. Nothing here is a release, and
> no build from it should hold money you are not prepared to lose.

## What it stands for

- **No server** between players, matching them, or holding or moving their funds. No house, no default indexer, no
  telemetry. Every source the app can reach is named, and every one but your node is yours to set or leave empty.
- **Proof over claim.** What the app says about money is checked against the chain, and what the code does is checked
  by the gate in `gate/`, which anyone can run from this repository alone.
- **Open source** under the ISC License (`LICENSE`). The name and the mark are separate (`TRADEMARK.md`).

## Working on it

- `CONTRIBUTING.md`: how a change lands, the commit standard, and how to verify signed commits.
- `SECURITY.md`: how to report a vulnerability privately.
- `python3 gate/run.py`: the gate. It needs Python 3.11 or later and nothing else.
