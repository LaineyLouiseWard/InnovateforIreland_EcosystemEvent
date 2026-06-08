# Working conventions — AI Build Day repo

Read [`README.md`](README.md) and [`WORKSHOP_EMAIL.md`](WORKSHOP_EMAIL.md) for the problem and brief. This file is committed — the shared source of truth for anyone (and any Claude Code session) building here.

It's a fast, half-day, several-people-at-once build, so the hygiene below matters. CLAUDE.md sets *how we work*, not *what we build* — the idea is worked out on the day, so don't lock in data or design choices it doesn't already state.

## Environment

```bash
conda env create -f environment.yml
go InnovateforIreland_EcosystemEvent   # cd in + activate the env
```

Python 3.12 + geopandas/pandas/matplotlib. Add new deps to `environment.yml` (not ad-hoc `pip install`) so everyone stays in sync.

## Working as a group

- **Branch off `main`** — one short-lived branch per person/pair, merged via a quick review.
- **Pull before you push** (`git pull --rebase`); never force-push a shared branch.
- **Small, frequent commits**, clear present-tense messages. No AI/co-author trailers.
- **Never commit secrets or data** — no API keys, no `raw/`, no `.env`. Check `git status` before staging.

## Data

**Keyless open data** → join to a boundary → draw with Leaflet. If a source needs a login or API key, it's the wrong source.

- Each fetch script names its source URL and access date (a comment or `SOURCES.md`), so anyone can re-pull.
- `raw/` and `data/raw/` are gitignored — commit the code that fetches and processes, not the downloads.

## Code

- No hard-coded absolute paths — repo-relative only, so it runs on every machine.
- It's a prototype to demo in the room: make it work and make it clear; skip speculative abstraction.

## Sensitivity

Real, vulnerable people (unpaid carers). Map **area-level rates, not individuals** — small-area census data can't identify anyone. If anything gets **forecast or simulated** (future demand, what-ifs), label it as a scenario under stated assumptions, never as fact.
