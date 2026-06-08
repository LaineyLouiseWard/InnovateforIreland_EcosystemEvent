# Carer At-Risk Map — Ireland

An interactive map of where unpaid carers in Ireland are most in need today, and
where that need will grow as the population ages. Built for carer-support services,
**national and regional**, to see where to direct help before carers reach crisis.

Our group's project for the Innovate for Ireland **AI Build Day** — a hands-on session
with Claude Code facilitated by Jonathan McCrea (brief in
[`WORKSHOP_EMAIL.md`](WORKSHOP_EMAIL.md)). We scope and build the prototype together in
the room.

## The problem

Almost 300,000 people in Ireland provide unpaid care (Census 2022), many of them poor,
older, or isolated themselves. Support is allocated off national and regional totals
that hide where strain actually concentrates, so help often arrives after a carer is
already in crisis. The data to find where need is greatest exists, but it hasn't been
brought together — and it says nothing about where demand is heading as the population
ages.

## What it does

**Two levels you click — or search — through,** because national and regional services
need different views:

- **National** — all 8 regions at a glance, for national services and the country-wide picture.
- **Regional** — drill into a region for small-area detail, for services working one patch.
- **Search your region** to jump straight there.

Across both levels:

- **Now** — where carers are most in need today (carer rate, Census 2022).
- **2042** — projected demand as the population ages, with a scenario slider (high /
  medium / low migration). A projection under stated assumptions, not a prediction.

## Tech stack

Keyless CSO open data (PxStat) pre-baked to static JSON, drawn with Leaflet, deployed on
GitHub Pages — the same pattern as the sister project
[the-indices-of-ireland](https://github.com/LaineyLouiseWard/the-indices-of-ireland).
Python (pandas / geopandas) for the data prep.

## Getting started

```bash
conda env create -f environment.yml
go InnovateforIreland_EcosystemEvent   # cd in + activate the env
```

## How the project is laid out

The planning docs live in [`docs/`](docs/); the build brief stays at the root. In build order:

| Doc | What it covers |
|---|---|
| [docs/BRAINSTORM.md](docs/BRAINSTORM.md) | the idea and the decisions |
| [docs/DATA.md](docs/DATA.md) | what carer data exists, and what we can plot |
| [docs/MODELLING.md](docs/MODELLING.md) | how we project current need forward to 2042 |
| [docs/DOWNLOAD_MANIFEST.md](docs/DOWNLOAD_MANIFEST.md) | the datasets to fetch (one per subagent) |
| [BUILD_BRIEF.md](BUILD_BRIEF.md) | how to build the site, with prompts for the day |
| [SOURCES.md](SOURCES.md) | what data is pulled, where it lives, the join keys |

[docs/carer-data-summary.txt](docs/carer-data-summary.txt) is a plain-language version for sharing.
Working conventions are in [CLAUDE.md](CLAUDE.md).

Folders: `site/` the web app · `scripts/` data prep · `data/` processed outputs + boundaries ·
`Design/` and `Research/` the team's materials.

## Data

Census 2022 and the CSO Regional Population Projections 2023–2042, all free and keyless
via the CSO PxStat API. Raw pulls are gitignored and re-pulled by scripts; only processed
outputs are committed. We map **area-level rates, not individuals**. Attribution: CSO
(CC BY 4.0).
