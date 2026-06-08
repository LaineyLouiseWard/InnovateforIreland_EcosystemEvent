#!/usr/bin/env python3
"""Build the Small Area -> IHA crosswalk for Plan 4 (Market Gap).

The CSO SA boundary layer carries no IHA field, so membership is derived by a
spatial join: each SA's representative point (guaranteed inside the polygon) is
located within one of the 20 HSE IHA polygons. Both layers are CSO-Small-Areas-
2022 lineage and generalised 20m, so SAs nest into IHAs and the assignment is
exact.

Inputs : data/raw/sa_2022_boundaries.geojson  (18,919 SAs; fetch_sa_boundaries.py)
         data/boundaries/iha_2025.geojson      (20 IHAs; fetch_iha_boundaries.py)
Output : data/sa_to_iha.csv  (sa_2022_code, IHA_code, IHA_operational_name,
                              HR_code, HR_operational_name)
"""
from pathlib import Path
import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent
SA   = ROOT / "data" / "raw" / "sa_2022_boundaries.geojson"
IHA  = ROOT / "data" / "boundaries" / "iha_2025.geojson"
OUT  = ROOT / "data" / "sa_to_iha.csv"


def canon(code):
    # match fetch_sa_boundaries.py: zero-pad each numeric part to 9 digits
    return "/".join(p.zfill(9) if (p.isdigit() and len(p) >= 8) else p
                    for p in code.split("/"))


def main():
    sa = gpd.read_file(SA)[["SA_PUB2022", "geometry"]].set_crs(4326, allow_override=True)
    sa["SA_PUB2022"] = sa["SA_PUB2022"].map(canon)
    iha = gpd.read_file(IHA).set_crs(4326, allow_override=True)
    print(f"  {len(sa)} SAs, {len(iha)} IHAs loaded")

    # representative point is guaranteed inside the (possibly concave) polygon
    pts = sa.copy()
    pts["geometry"] = sa.geometry.representative_point()

    joined = gpd.sjoin(pts, iha, how="left", predicate="within")
    unmatched = joined["IHA_code"].isna().sum()
    if unmatched:
        # fall back to nearest IHA for any point that missed (generalisation slivers)
        miss = pts[joined["IHA_code"].isna()]
        near = gpd.sjoin_nearest(miss, iha, how="left")
        joined.loc[near.index, ["IHA_code", "IHA_operational_name",
                                "HR_code", "HR_operational_name"]] = \
            near[["IHA_code", "IHA_operational_name", "HR_code", "HR_operational_name"]].values
        print(f"  {unmatched} SAs matched by nearest-IHA fallback")

    out = (joined[["SA_PUB2022", "IHA_code", "IHA_operational_name",
                   "HR_code", "HR_operational_name"]]
           .rename(columns={"SA_PUB2022": "sa_2022_code"})
           .sort_values("sa_2022_code"))
    out.to_csv(OUT, index=False)
    print(f"  wrote {OUT.relative_to(ROOT)}  ({len(out)} rows, {out['IHA_code'].isna().sum()} unassigned)")

    print("\n  SAs per IHA:")
    counts = out.groupby(["IHA_code", "IHA_operational_name"]).size()
    for (code, name), n in counts.items():
        print(f"    {code:>3}  {name:<45} {n:5d}")


if __name__ == "__main__":
    main()
