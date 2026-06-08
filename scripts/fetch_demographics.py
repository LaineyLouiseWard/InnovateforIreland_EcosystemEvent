#!/usr/bin/env python3
"""Fetch Census 2022 demographics for the carer Vulnerability Index (Plan 1).

Two Demand-theme variables, both at small-area level from the CSO PxStat API
(keyless, open, no login):

  SAP2022T1T1SA    population by single year / age band  -> % aged 65+
  SAP2022T12T1SA   persons with a disability             -> total disability rate

Source : https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<CODE>/JSON-stat/2.0/en
Accessed: 2026-06-08

The 65+ figure has no pre-built aggregate, so the five upper age bands are summed.
The disability table is a count of persons with a disability; dividing by the
table's total population gives a rate (the SAPS "great extent" breakdown does not
exist at SA level — see _archive/VARIABLE_VERIFICATION_REPORT.md).

Output: data/sa_demographics.csv  (one row per small area, joins to the carer CSV
        on sa_2022_code — same CSO Small Areas dimension, identical label strings)
"""
import csv
from pathlib import Path

from fetch_carer_data import fetch, geo_slice, rate, write_csv, SA, SEX, AGE

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"

AGE_65PLUS = ["Age 65-69", "Age 70-74", "Age 75-79", "Age 80-84", "Age 85 and over"]


def build():
    pop = geo_slice(fetch("SAP2022T1T1SA"), SA, {SEX: "Both Sexes", AGE: "Total"})
    p65 = {}
    for band in AGE_65PLUS:
        for g, (_, v) in geo_slice(fetch("SAP2022T1T1SA"), SA,
                                   {SEX: "Both Sexes", AGE: band}).items():
            p65[g] = p65.get(g, 0) + (v or 0)
    disability = geo_slice(fetch("SAP2022T12T1SA"), SA, {SEX: "Both Sexes"})

    rows = []
    for g, (name, p) in pop.items():
        if name.strip().lower() == "ireland":   # state aggregate, not a small area
            continue
        pop65 = p65.get(g)
        _, dis = disability.get(g, (None, None))
        rows.append([name, p, pop65, rate(pop65, p), dis, rate(dis, p)])
    rows.sort(key=lambda r: r[0])
    write_csv(OUT / "sa_demographics.csv",
              ["sa_2022_code", "population", "pop_65plus", "pct_65plus_pct",
               "disability_persons", "disability_rate_pct"], rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("Small-area demographics (Demand theme):")
    build()
