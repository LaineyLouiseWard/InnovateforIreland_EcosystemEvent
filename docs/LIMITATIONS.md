# Limitations

A plain-language list of what this map can and cannot tell you. Written to be read aloud to a
non-specialist audience, and to keep us honest. Nothing here is a flaw to hide: these are the
known edges of a keyless, open-data prototype, and most have a clear upgrade path.

Rule of thumb: everything here is an area-level signal to investigate, never a verdict about a
place or a person.

---

## Supply side (where the help is)

**1. An office is not where the care happens.**
A home-care agency's address is its office; the carers it employs drive out to people's homes
across a wide area. So "this area is 40 km from the nearest home-care office" means the nearest
provider is based 40 km away, not that nobody reaches it: a carer may well drive there. The
office distance is a proxy for access, not a hard "no service here" boundary.
*How we handle it:* stated on-screen wherever a distance is shown.

**2. The dots aren't all equally precise.**
Addresses were geocoded with a free tool that reads the text of an address, not Eircodes (the
official Eircode lookup is paid). Home-care offices are the weak layer: only about 27 of 201
resolved to an exact street, most landed at the town centre (off by up to a few km), and some at
the county. *How we handle it:* every point carries a precision flag (`address`/`town`/
`county`), and county-level ones are flagged as softer. The error matters least in rural
deserts, where real distances are tens of km and a few km of slack doesn't change the picture.
*Upgrade path:* a paid Eircode-to-coordinate lookup would pin every point to its building.

**3. Distances are "as the crow flies."**
We measure straight-line distance from an area to the nearest service, not road travel time.
Real journeys are longer, more so in the rural west, with winding roads, peninsulas and water
crossings. So true access is somewhat worse than the map shows in remote areas.
*Upgrade path:* a routing engine would give drive-times instead.

**4. We can't see how big or busy each provider is.**
We know where providers are, not their capacity or how many clients they already serve. So we
can't tell a stretched 2-carer agency from a 200-carer one. *How we handle it:* we use
distance-to-nearest (an honest measure for the data we have) and deliberately did not use the
"gold standard" capacity-based method (2SFCA), which would require guessing those numbers.

**5. Nursing homes are deliberately excluded from the "desert" score.**
A nursing home is a place someone moves into; it replaces home caring rather than supporting the
informal carer, so it doesn't count toward "is carer support nearby?" This is a choice, and not
everyone would make it. *How we handle it:* nursing homes stay visible on the map as context,
and their distance is still stored if you ever want the broader view.

---

## Demand side (where the need is)

**6. Deprivation is borrowed from the bigger area.**
The Pobal deprivation score isn't openly released at small-area level, so each small area
inherits its parent Electoral Division's score (about 5 small areas per ED). The big differences
*between* areas survive; fine variation *within* an ED is lost. Flagged as "assigned from
parent ED."

**7. Disability is the total rate, not severity.**
The census only gives total disability at small-area level, not the "to a great extent"
breakdown. We use the total rate as a reasonable stand-in: less specific, not wrong.

**8. One care variable couldn't be mapped.**
The "43+ hours of unpaid care per week" figure (the most intense carers) doesn't exist at
small-area level in the census, so it's left out rather than faked. Care load uses the overall
carer rate instead.

---

## How to read the maps (interpretation)

**9. Colours are *relative to Ireland*, not absolute.**
"High need" means in the worst third of Irish areas, not above any official threshold. On the
need-vs-supply bivariate, about 1 in 9 areas always falls in the "dark corner" by construction:
it shows *where* the worst-on-both areas are, not *how many* areas are objectively "bad."

**10. The scores are 0–100 ranks, not percentages.**
A vulnerability of 78 means "more vulnerable than 78% of areas," not "78% of people." Never read
them as percentages.

**11. Zoomed-out colours are averages, and averages hide spread.**
A region or HSE-area colour is the average of all the small areas inside it. Averages bunch up in
the middle, so a calm-looking region can still hide pockets of severe need. *How we handle it:*
each zoom level gets its own colour scale, and muted areas hiding hotspots get flagged. But the
rule stands: drill in to see the truth.

**12. The capstone "build here" list is a shortlist, not an instruction.**
The operator "target these towns" output is a starting point to validate on the ground. Because
it inherits limitations 1 to 3, a flagged "desert" could occasionally be an artefact of an
office that's geocoded coarsely but actually serves the area. Treat it as where to look first,
never where to definitely build.

---

## Scope & freshness

**13. Republic of Ireland only.**
Northern Ireland has separate census geography (NISRA) and a different deprivation index (NIMDM).
An all-island version is a distinct piece of work, not a quick toggle.

**14. It's a snapshot.**
Built on Census 2022 and provider registers as of mid-2026. Registers change as providers open
and close; the census runs about every 5 years. Re-running the fetch scripts refreshes it.

**15. Town names (once added) are the *nearest* settlement.**
The "near Belmullet" labels point to the closest named town to an area's centre, a human gloss on
a small-area code, not a precise address. Each carries the distance to that town so far-off
matches are visible.
