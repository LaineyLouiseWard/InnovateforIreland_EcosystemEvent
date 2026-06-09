# Product

## Register

product

## Users

Primary: care operators and service planners deciding where to open services, allocate staffing, or plan procurement. Core interaction is the HSE market gap and service desert analysis — they need area-level rankings, not narrative.

Secondary: policy makers and researchers verifying methodology, citing figures, or downloading data for reports.

General: public and journalists discovering the geographic scale of unpaid carer need and sharing the map.

## Product Purpose

A public-interest decision-support tool mapping unpaid carer vulnerability across Ireland's 18,919 Census small areas. Built on CSO Census 2022 and Pobal HP Deprivation 2022 data, it scores every area on four need dimensions (care load, deprivation, demand, isolation) and fuses them with home-support service supply data to expose where unmet need is greatest. Three drillable levels: 8 NUTS3 regions for the national picture, 18,919 Census small areas for neighbourhood-level detail, and 20 HSE Integrated Healthcare Areas for the operator market gap.

Success: a care provider opens a service in Kerry rather than Cork North and East because the map told them Kerry had the highest gap. A journalist writes a piece citing the Border region's vulnerability ranking. A policy maker includes the service desert score in a funding allocation brief.

## Brand Personality

Clear, Serious, Trustworthy. The site speaks with the authority of the data — no emotional advocacy, no institutional bureaucracy. Voice is precise and direct. Every word earns its place. The subject matter (isolated, older, low-income carers) is serious; the design reflects that without aestheticising poverty or guilt-tripping the viewer.

## Anti-references

- Government portal (GOV.IE, data.gov.ie style): institutional blue, heavy navigation, impenetrable dense text, no visual hierarchy, no sense of design intention
- Academic paper / journal aesthetic: methodology-first layout, wall-of-text abstract, publication-style tables before any map or visual, zero typographic hierarchy beyond heading levels

## Design Principles

1. Data is the authority — design clears the path to it. Every visual element should reduce cognitive load, not add interest for its own sake. The map is the product; the interface is its frame.
2. Precision over warmth — urgency comes from the numbers. Resist softening the data with emotional or decorative design. The score "80" for Kerry's market gap is more powerful unadorned.
3. Progressive disclosure — region to small area to HSE is the core product interaction. Each level should feel complete, not like a step toward some other destination.
4. Credibility without bureaucracy — trustworthy does not mean institutional. Authority comes from rigorous data provenance, confident typography, and sparse copy — not from heavy navbars or institutional blue.
5. Cartographic integrity — the colour system serves the data. The viridis vulnerability gradient (yellow = low need, dark purple = high need) has scientific meaning and partial colour-blind support built in. Future design decisions must accommodate it; competing with it is not an option.

## Accessibility & Inclusion

WCAG 2.1 AA minimum: 4.5:1 body contrast, keyboard navigable, screen reader compatible.

Colour-blind safe palette: the current viridis palette has known issues at the yellow-green end under protanopia and deuteranopia. This is a flagged constraint for the frontend-design pass — the palette itself is locked (cartographic integrity), so the fix is additive (labels, patterns, or texture on critical elements) rather than a palette swap.

## Shipped UI decisions

The calls that shaped the built interface, kept here as the record (the working backlog they came
from is local-only).

**Colour system.** Viridis (reversed: yellow = low, purple = high) is reserved for the 0–100
Vulnerability family — regional, local and small-area choropleths, the four drivers, Service Desert
and Residential Gap. The HSE **Market Gap** uses its own colour-blind-safe diverging scale (blue =
better supplied, through light at balance, to orange = bigger gap, centred at 0), so it reads as a
different kind of measure. The Need × Supply bivariate uses a colour-blind-safe blue–orange 3×3.

**One scale across zoom levels.** Region and HSE-area fills are classified on the *same national
0–100 small-area scale*, so a colour means the same number at every level rather than re-scaling per
view. Region averages cluster mid-range — that's honest; the action is the spread within a region on
drill-in. Coarse levels carry a spread bar ("avg 48, ranges 12→91 inside") and a "hidden hotspots"
badge to pull users into regions an average would have flattened. The legend always names what the
colour is ("region average" vs "this area's own value").

**Labels for a care-planner audience.** UI labels were plain-worded away from the internal theme
names: Care load → "Carer share", Isolation → "Hard to reach", the targeting lens → "Need ×
support"; Deprivation and Demand kept. The "Border" region is shown as **North-West** (the data key
is unchanged). The measure dropdown leads with the headline (Vulnerability) and where-to-target, and
tucks the four drivers under a collapsible "What builds the score".

**Supply markers.** The three supply layers sit outside the viridis band so they read on any map
colour, with shape encoding type: home care = red circle, Family Carers = magenta diamond, nursing
home = orange square, each with a white stroke. They live in their own "Care services" panel, not
folded into the legend.

**Explaining the method.** Source detail, geocoding caveats and definitions live on a dedicated
methods page (`site/methods.html`) plus in-place ⓘ popovers, rather than crowding the map. The
operator login (`site/login.html`, the fictional company MedVizion) is a demo wrapper around the
public map, not a real gate.
