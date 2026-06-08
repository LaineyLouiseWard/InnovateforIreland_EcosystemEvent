# Brief for the town-naming chat

Hand this whole file to a new Claude Code chat in this repo
(`/home/lainey/Documents/Github/InnovateforIreland_EcosystemEvent`).

## The one job
Our small areas are census codes like `157110001` — meaningless to a human. The capstone
"target your supply here" list needs each one labelled with the **real place it's near**
(e.g. *"near Belmullet, Co. Mayo"*). Produce a lookup table that maps every small-area code
to a human town/locality name. **You decide the best method** — the notes below are options,
not orders.

## Output (the deliverable)
`data/sa_town_names.csv` with at least:
```
sa_2022_code,town_name,county,method,distance_km
157110001,Belmullet,Mayo,nearest_settlement,3.2
```
- `town_name` — the nearest named settlement (label it so a user reads it as *approximate*,
  e.g. the downstream UI will show "near {town_name}"). Don't invent a street address.
- `method` / `distance_km` — how you got it and how far the settlement is, so confidence is auditable.
- **Priority:** the ~200 small areas listed in `data/target_drilldown.json` (the capstone
  targets) MUST be named. Naming all 18,919 is a bonus (it benefits the whole map) — do the
  200 first and confirm before attempting the full set.

A downstream build (`scripts/build_target_drilldown.py`) already reads this file if present
and joins on `sa_2022_code`, falling back to the raw code when a name is missing — so just
producing the CSV wires it in automatically. Re-run that script after to verify.

## Inputs in the repo
- SA centroids: `site/sa/<region>.geojson` features have property `c` (the SA code) and a
  polygon; `scripts/build_service_desert.py` has `feature_centroid()` you can reuse for lon/lat.
- The target list to prioritise: `data/target_drilldown.json` (200 SAs, already have lat/lon).

## Methods to consider (pick what's best — keyless, offline-cacheable, ROI only)
1. **CSO Settlements 2022** (Tailte Éireann / data.gov.ie, open) — official town/village polygons
   or points. Nearest-settlement to each SA centroid. Most authoritative for Irish places.
2. **OSM `place=town/village/suburb/townland`** point extract — keyless, dense in rural areas.
   Nearest-point to each centroid.
3. **OSM Nominatim reverse geocode** of the centroid — keyless but rate-limited (1 req/s) and
   patchy in rural areas (can return a county). Fine as a one-off batch over the 200 targets,
   cached; **not** for the full 18,919 live.

A spatial nearest-settlement join (option 1 or 2) is almost certainly better than reverse
geocoding for this — but confirm with a quick test on a few known areas (e.g. an SA in Belmullet,
one in Dublin city) before running the batch.

## Constraints (from repo CLAUDE.md)
- **Keyless, open data only** — no API keys, no logins.
- **No hard-coded absolute paths** — repo-relative.
- Raw downloads go in the gitignored `data/raw/`; commit the script + the output CSV, not the downloads.
- Add any new dependency to `environment.yml`.
- **Honesty:** the name is the *nearest settlement*, not where the SA is exactly — keep the
  `distance_km` so the UI can footnote far-off matches. Don't imply a precise address.

## Do NOT touch
The scoring pipeline (`scripts/build_*.py` for vulnerability / service desert / market gap)
and the `data/*` scored CSVs / GeoJSONs. You only **add** `scripts/build_town_names.py` and
`data/sa_town_names.csv`. Verify by re-running `python3 scripts/build_target_drilldown.py` and
checking the "with real names" count goes up.
