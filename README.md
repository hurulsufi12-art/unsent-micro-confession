# Unsent: The Micro-Confession Sprint

[![Unsent: The Micro-Confession Sprint](https://make.fun/badge/u-boothlord-unsent-the-micro-confession-sprint-8c6596ba.svg)](https://make.fun/bounty/u-boothlord-unsent-the-micro-confession-sprint-8c6596ba)
[![Rank](https://make.fun/badge/u-boothlord-unsent-the-micro-confession-sprint-8c6596ba/hurulsufi12-art/unsent-micro-confession/rank.svg)](https://make.fun/bounty/u-boothlord-unsent-the-micro-confession-sprint-8c6596ba)
[![Reward](https://make.fun/badge/u-boothlord-unsent-the-micro-confession-sprint-8c6596ba/hurulsufi12-art/unsent-micro-confession/reward.svg)](https://make.fun/bounty/u-boothlord-unsent-the-micro-confession-sprint-8c6596ba)

Entry for the [Unsent: The Micro-Confession Sprint](https://make.fun/bounty/u-boothlord-unsent-the-micro-confession-sprint-8c6596ba) bounty on make.fun.

The program writes one two-part micro-confession — a `To:` line naming who it was meant for, and the unsent message itself, one line written exactly as it was typed — to `/output/entry.txt`.

## Run

```sh
python3 main.py
```

Stdlib only, no network, no input files, deterministic: every run writes the same bytes.

## Tests

```sh
python3 -m unittest discover -s tests -v
```
