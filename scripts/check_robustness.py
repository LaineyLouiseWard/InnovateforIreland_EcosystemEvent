"""Robustness check for the Vulnerability composite.

Reads the baked per-SA theme scores from site/sa/*.geojson (no raw pulls needed) and reports:
 1. pairwise Spearman correlations between the four themes — flags double-counting if themes
    are highly correlated (equal weights then overweight their shared component);
 2. Spearman rank agreement between the composite and the SVI-style flag count (themes in the
    worst national quartile, score >= 75) — how far the compensatory average and the
    non-compensatory count tell the same story;
 3. the flag-count breakdown of the composite's top decile — whether severe composite scores
    are broad-based or driven by a single extreme theme.

Run from the repo root: python scripts/check_robustness.py
"""

import json
from pathlib import Path

import pandas as pd

THEMES = ["cl", "st", "dm", "is"]
NAMES = {"cl": "Carer share", "st": "Deprivation", "dm": "Demand", "is": "Hard to reach"}

sa_dir = Path(__file__).resolve().parent.parent / "site" / "sa"
rows = []
for f in sorted(sa_dir.glob("*.geojson")):
    for feat in json.loads(f.read_text())["features"]:
        p = feat["properties"]
        rows.append({k: p.get(k) for k in THEMES + ["v"]})
df = pd.DataFrame(rows).dropna()
df["flags"] = (df[THEMES] >= 75).sum(axis=1)
print(f"{len(df):,} small areas\n")

print("Pairwise Spearman correlation between themes:")
print(df[THEMES].corr(method="spearman").rename(index=NAMES, columns=NAMES).round(2).to_string(), "\n")

rho = df["v"].corr(df["flags"], method="spearman")
print(f"Composite vs flag count, Spearman rho: {rho:.2f}\n")

top = df[df["v"] >= df["v"].quantile(0.9)]
print("Flag counts within the composite's top decile:")
share = (top["flags"].value_counts(normalize=True).sort_index() * 100).round(1)
for k, v in share.items():
    print(f"  {k} of 4 themes in worst quartile: {v}%")
print(f"\nShare of all areas flagged on 3+ themes: {100 * (df['flags'] >= 3).mean():.1f}%")
