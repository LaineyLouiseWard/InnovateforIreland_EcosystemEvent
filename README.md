# Carer Vulnerability Map of Ireland

An interactive map of where unpaid carers in Ireland are most vulnerable, and where that
need is least matched by support on the ground. Built for carer-support services and the
people who plan them, at national, regional, and operator level, to see where to direct
help and where to put the next service before carers reach crisis.

Our group's project for the Innovate for Ireland **AI Build Day**, a hands-on session with
Claude Code facilitated by Jonathan McCrea (brief in [`WORKSHOP_EMAIL.md`](WORKSHOP_EMAIL.md)).
We scope and build the prototype together in the room.

## The problem

Almost 300,000 people in Ireland provide unpaid care (Census 2022), many of them poor,
older, or isolated themselves. Support is allocated off national and regional totals that
hide where strain actually concentrates, so help often arrives after a carer is already in
crisis. And nobody has joined *where the need is* to *where the services already are*. The
data to answer both exists; it just hadn't been brought together.

## What it does

Four layers, each clickable from the whole country down to a single small area:

- **Vulnerability:** a composite of carer load, deprivation, age/disability demand, and
  isolation, percentile-ranked across all 18,919 small areas. Where carers are most at risk.
- **Supply:** where support actually exists (home-care agencies, family-carer centres,
  nursing homes), geocoded and overlaid.
- **Service desert:** vulnerability weighted by how far the nearest support is, so a
  high-need area with nothing nearby rises to the top.
- **Market gap:** need rank minus provider-density rank for each of the 20 HSE areas, showing
  where demand most outstrips supply. This feeds the operator drill-down: pick an area, get
  its worst small areas to target first.

Every score is a relative rank, not an absolute count, and every layer carries its caveats
([`docs/LIMITATIONS.md`](docs/LIMITATIONS.md)). We map **area-level rates, not individuals**.

## Tech stack

Keyless open data (CSO PxStat, Pobal, HIQA/HSE registers) pre-baked to static JSON, drawn
with Leaflet, deployed on GitHub Pages. Python (pandas / geopandas) for the data prep and
scoring.

## Getting started

```bash
conda env create -f environment.yml
go InnovateforIreland_EcosystemEvent   # cd in + activate the env
```

The site is static. Open `site/index.html`, or serve `site/` over HTTP so the fetches work.
The scoring pipeline lives in `scripts/` (demographics → deprivation → vulnerability →
supply → service desert → market gap → target drill-down).

## How the project is laid out

| Where | What |
|---|---|
| [`docs/`](docs/) | The methodology, limitations, and project context. See [`docs/README.md`](docs/README.md) for the index. |
| [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) | How every score is built, and the established method each rests on. |
| [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) | What the map can and cannot tell you. |
| [`SOURCES.md`](SOURCES.md) | Every dataset pulled, where it lives, the join keys. |
| [`CLAUDE.md`](CLAUDE.md) | Working conventions for anyone (or any Claude session) building here. |

Folders: `site/` the web app, `scripts/` data prep and scoring, `data/` processed outputs
plus boundaries, `Design/` and `Research/` the team's materials, `_archive/` spent planning
docs.

## Data

CSO Census 2022 (PxStat), Pobal HP Deprivation Index 2022, and the HIQA / HSE provider
registers, all free and keyless. Raw pulls are gitignored and re-pulled by scripts; only
processed outputs are committed. We map **area-level rates, not individuals**. Attribution:
CSO (CC BY 4.0), Pobal, and the respective registers (see [`SOURCES.md`](SOURCES.md)).
