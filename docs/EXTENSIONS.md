# Plan ideas & extensions

A running list of ideas beyond the core build, to pick from or park. Not commitments.

The **core build order** (national *Now* map → *2042* view → scenario slider → regional
zoom) lives in [BUILD_BRIEF.md](../BUILD_BRIEF.md). This file is everything beyond or
around it. Add new ideas under **Your new ideas** at the bottom (or drop them in and
I'll sort them).

## Map layers & data

- **At-risk composite:** combine carer load with vulnerability (deprivation,
  access/isolation, older / lone carers) instead of carer rate alone. Constraints:
  deprivation is ED-level only and older/lone-carer measures are national-only (see
  `SOURCES.md`). The small-area-mappable amplifier is **access/isolation**: **no-car
  households** and **distance to nearest support service**. One-person-household % is
  available at small-area but is a poor proxy for *carer* isolation (a co-resident carer
  is not a lone household); read it as a lone care-recipient / demand signal instead.
- **Carer strain projection:** project carer *supply* (current carer-by-age rates ×
  projected age structure) and map demand ÷ supply. The headline "at-risk projection."
  Method in [MODELLING.md](../_archive/MODELLING.md).
- **Support-service overlay:** plot Family Carers Ireland centres / the `carer_supports`
  data and show distance-to-nearest-service ("service deserts").
- **HSE-geography view:** a service-aligned cut (Community Health Networks / Specialist
  Teams) from the `DHGA09` carer tables, since the audience is support services.
- **Bivariate map:** carer rate × deprivation, or toggleable separate layers versus one
  combined score.
- **85+ / disability weighting:** weight demand by the oldest ages (far heavier care
  need) rather than a flat 65+.

## Interactivity & UX

- **Year slider:** animate 2022 → 2042 using `PEC26`'s annual data, not just the 2042 endpoint.
- **Policy what-if levers:** beyond the M1/M2/M3 toggle, e.g. "place a new service here,
  who does it reach," or adjust assumed service capacity.
- **Region report:** click-through to a one-page summary or downloadable stats per region/area.

## Audience & framing

- **Service-planning view:** where to place new capacity given projected demand.
- **Commercial angle:** a product for support-service providers (the "sell to" idea from
  the brainstorm).
- **Explainer / story mode:** a guided walk-through for non-specialist communication.

## Method & rigour (stretch)

- **Hotspot significance:** Getis-Ord Gi* / Local Moran's I to test whether high-need
  clusters are statistically real, not just where we drew the line.

## Your new ideas

- 
