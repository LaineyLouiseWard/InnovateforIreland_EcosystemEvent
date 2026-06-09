# Extensions — parked ideas

Ideas beyond what shipped, to pick from or park. Not commitments. The built product (Vulnerability
Index, Service Desert, Market Gap, bivariate, capstone drill-down) is described in
[`../methods/METHODOLOGY.md`](../methods/METHODOLOGY.md).

## Sharper data

- **85+ / disability weighting:** weight demand by the oldest ages (far heavier care need) rather
  than a flat 65+ share.
- **Drive-time distances:** replace straight-line distance with a routing engine, so access reflects
  real journeys (matters most in the rural west, with winding roads and water crossings).
- **Eircode-precise geocoding:** a paid Eircode-to-coordinate lookup would pin every supply point to
  its building, sharpening the weak home-care layer (see [`../methods/LIMITATIONS.md`](../methods/LIMITATIONS.md)).
- **Provider capacity (2SFCA):** if per-provider capacity data ever becomes available, the two-step
  floating catchment method becomes possible (deliberately avoided now for lack of that data).

## Time and scenarios

- **Future-demand layer:** age each area's population forward with the CSO regional projections
  (`PEC26`, NUTS3, 2022–2042) to map where demand grows, with a migration scenario (M1/M2/M3). This
  was the project's original direction; it was set aside in favour of the present-day need-vs-supply
  map, but remains a natural second view.

## Reach and audience

- **All-island version:** add Northern Ireland, which uses separate geography (NISRA) and a different
  deprivation index (NIMDM). A distinct piece of work, not a toggle.
- **Explainer / story mode:** a guided walk-through of the map for a non-specialist audience.

## Method and rigour (stretch)

- **Hotspot significance:** Getis-Ord Gi* or Local Moran's I to test whether high-need clusters are
  statistically real, not just where the colour breaks fall.

## Your new ideas

-
