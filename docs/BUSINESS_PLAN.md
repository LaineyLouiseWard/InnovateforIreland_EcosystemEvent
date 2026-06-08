# CareMap Ireland — Business Plan (One-Page)

---

## Problem

Ireland has no integrated demand-and-supply intelligence tool for the care sector. Site selection decisions for nursing homes and home care agencies are made on gut feel, Fair Deal rate schedules, and reactive CBRE valuations. The UK equivalent — Carterwood Analytics — covers Great Britain only. That gap is the opportunity.

---

## Product

An interactive web map showing where unpaid carer need is greatest in Ireland versus where care services exist — surfacing geographic gaps at small-area resolution.

**Working name:** CareMap Ireland

**What it shows:**
- **Demand layer:** Small-area vulnerability index built from carer rate, deprivation (Pobal HP Index), disability prevalence, and age 65+ share — across all 18,919 CSO small areas
- **Supply layer:** 545 nursing homes (HIQA register), 22 Family Carers Ireland centres, 200+ HSE-approved home care agencies
- **Derived indices:** Vulnerability Score, Service Desert Score, Market Gap Score

---

## Market

| Segment | Scale |
|---|---|
| Nursing home sector revenue | ~€800m |
| Nursing home beds needed by 2040 | 19,500–25,000 (ESRI) |
| Home care market (Ireland) | USD 2.9bn → 5.4bn by 2030 |
| Over-65 population by 2051 | 1.6m (doubling from today) |

Home care is about to be formally regulated for the first time (December 2025 Bill), creating immediate demand for compliance and market-entry intelligence.

---

## Customers

**Tier 1 — Paying:** Nursing home operators, private equity investors, property developers. Use case: site selection, IHA application decisions, market entry assessment.

**Tier 2 — Free/grant-funded:** HSE, Family Carers Ireland, local authority planners. Use case: resource allocation, policy evidence. This layer builds credibility and public legitimacy.

---

## Revenue

- **SaaS subscriptions** for operators and investors (primary revenue)
- **Free public planner view** — no paywall for HSE/FCI/planning bodies
- **Grant income potential** from HSE or FCI to fund the public layer

---

## Tech

- **Frontend:** Leaflet.js interactive map
- **Data pipeline:** Python (CSO PxStat API, HIQA register, HSE IHA PDFs, Pobal index)
- **Data:** Entirely open, keyless public sources — CSO Census 2022, HIQA, HSE, Pobal. No proprietary data required.
- **Hosting:** Vercel

---

## Status

Prototype live at **https://innovateforireland-ecosystemevent.vercel.app**

Demand, supply, and index layers functional. Subscription and access tiers not yet implemented.
