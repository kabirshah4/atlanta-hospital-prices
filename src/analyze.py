"""Analysis: how much do prices vary, and what explains it?

Main price measure ("typical insured price"): for a hospital and procedure, the median of the
negotiated rates of the five largest commercial insurers in Georgia (Anthem BCBS,
UnitedHealthcare, Aetna, Cigna, Kaiser), across their commercial plans.

Writes tables to results/ and the numbers to results/numbers.json.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from clean import MAJOR

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
RES.mkdir(exist_ok=True)


def miles(lat1, lon1, lat2, lon2):
    p = np.pi / 180
    a = (np.sin((lat2 - lat1) * p / 2) ** 2
         + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2)
    return 3958.8 * 2 * np.arcsin(np.sqrt(a))


def r2(y, X):
    X = np.column_stack([np.ones(len(y)), X]) if X is not None else np.ones((len(y), 1))
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return 1 - resid.var() / y.var()


def main():
    p = pd.read_parquet(ROOT / "data" / "prices.parquet")
    hosp = pd.read_csv(ROOT / "data" / "hospitals.csv")
    cg = pd.read_parquet(ROOT / "data" / "cash_gross.parquet")
    procs = p[["code", "procedure", "category"]].drop_duplicates()

    comm = p[(p.plan_type == "Commercial") & p.brand.isin(MAJOR)]
    # one number per hospital x insurer brand (median over that brand's plans)
    cell = comm.groupby(["hospital", "system", "code", "brand"]).price.median().reset_index()
    typical = (comm.groupby(["hospital", "code"]).price.agg(typical="median", n_plans="count").reset_index())
    ma = (p[p.plan_type == "Medicare Advantage"].groupby(["hospital", "code"]).price.median()
            .reset_index(name="medicare_adv"))
    hp = (typical.merge(ma, how="left", on=["hospital", "code"])
                 .merge(cg, how="left", on=["hospital", "code"])
                 .merge(procs, on="code").merge(hosp[["hospital", "system", "stars"]], on="hospital"))
    hp.to_csv(RES / "hospital_procedure_prices.csv", index=False)

    # 1. Spread across hospitals, per procedure
    rows = []
    for code, g in hp.groupby("code"):
        g = g.dropna(subset=["typical"])
        if len(g) < 5:
            continue
        lo, hi = g.loc[g.typical.idxmin()], g.loc[g.typical.idxmax()]
        rows.append(dict(code=code, procedure=lo.procedure, n_hospitals=len(g),
                         cheapest=lo.hospital, cheapest_price=lo.typical,
                         priciest=hi.hospital, priciest_price=hi.typical,
                         ratio=hi.typical / lo.typical, gap=hi.typical - lo.typical,
                         median=g.typical.median()))
    spread = pd.DataFrame(rows).sort_values("ratio", ascending=False)
    spread.to_csv(RES / "spread_by_procedure.csv", index=False)

    # 2. Same insurer, nearby hospitals: the "shock" pairs (within 15 miles)
    loc = hosp.set_index("hospital")[["lat", "lon"]]
    pairs = []
    for (code, brand), g in cell.groupby(["code", "brand"]):
        g = g.reset_index(drop=True)
        for i in range(len(g)):
            for j in range(len(g)):
                a, b = g.loc[i], g.loc[j]
                if a.system == b.system or a.price <= b.price:
                    continue
                d = miles(*loc.loc[a.hospital], *loc.loc[b.hospital])
                if d <= 15:
                    pairs.append(dict(code=code, brand=brand, cheap=b.hospital, cheap_price=b.price,
                                      pricey=a.hospital, pricey_price=a.price, miles=round(d, 1),
                                      ratio=a.price / b.price, gap=a.price - b.price))
    pairs = pd.DataFrame(pairs).merge(procs, on="code").sort_values("gap", ascending=False)
    pairs.to_csv(RES / "same_insurer_nearby_gaps.csv", index=False)

    # 3. What explains price differences: hospital system or insurer?
    #    Share of the variation in log price (per procedure) explained by each.
    dec = []
    for code, g in cell.groupby("code"):
        if g.system.nunique() < 3 or g.brand.nunique() < 3:
            continue
        y = np.log(g.price.values)
        S = pd.get_dummies(g.system, drop_first=True).values.astype(float)
        B = pd.get_dummies(g.brand, drop_first=True).values.astype(float)
        dec.append(dict(code=code, n=len(g), system=r2(y, S), insurer=r2(y, B),
                        both=r2(y, np.column_stack([S, B]))))
    dec = pd.DataFrame(dec).merge(procs, on="code")
    dec.to_csv(RES / "variance_explained.csv", index=False)

    # 4. Commercial vs Medicare Advantage at the same hospital
    both = hp.dropna(subset=["typical", "medicare_adv"])
    both = both.assign(multiple=both.typical / both.medicare_adv)

    # 5. Cash vs insurance
    cash = hp.dropna(subset=["typical", "cash"])
    cash = cash.assign(cash_cheaper=cash.cash < cash.typical)
    disc = hp.dropna(subset=["cash", "gross"]).assign(cash_share=lambda x: x.cash / x.gross)
    cash_by_system = disc.groupby("system").cash_share.median()

    # 6. Price vs quality (CMS star rating), hospital price index
    hp["rel"] = np.log(hp.typical / hp.groupby("code").typical.transform("median"))
    idx = hp.groupby(["hospital", "system", "stars"]).rel.mean().reset_index()
    idx["price_index"] = np.exp(idx.rel)  # 1.20 = 20% above the typical Atlanta hospital
    idx.drop(columns="rel").to_csv(RES / "hospital_price_index.csv", index=False)
    rho = idx[["price_index", "stars"]].corr(method="spearman").iloc[0, 1]
    sys_idx = idx.groupby("system").price_index.mean()

    top = pairs.iloc[0]
    numbers = dict(
        n_hospitals=int(hp.hospital.nunique()), n_procedures=int(hp.code.nunique()),
        n_prices=int(len(p)),
        median_ratio=float(spread.ratio.median()),
        max_ratio_procedure=spread.iloc[0].procedure, max_ratio=float(spread.iloc[0].ratio),
        shock=dict(procedure=top.procedure, brand=top.brand, cheap=top.cheap, cheap_price=float(top.cheap_price),
                   pricey=top.pricey, pricey_price=float(top.pricey_price), miles=float(top.miles)),
        variance_explained=dict(system=float(dec.system.median()), insurer=float(dec.insurer.median()),
                                both=float(dec.both.median())),
        commercial_vs_ma_multiple=float(both.multiple.median()),
        cash_cheaper_share=float(cash.cash_cheaper.mean()), n_cash_compared=int(len(cash)),
        cash_as_share_of_list=cash_by_system.round(2).to_dict(),
        price_index_by_system=sys_idx.round(2).to_dict(),
        stars_price_spearman=float(rho),
    )
    (RES / "numbers.json").write_text(json.dumps(numbers, indent=2))
    print(json.dumps(numbers, indent=2))
    print(spread[["procedure", "cheapest", "cheapest_price", "priciest", "priciest_price", "ratio"]].round(0).to_string())
    print(pairs.head(10)[["procedure", "brand", "cheap", "cheap_price", "pricey", "pricey_price", "miles"]].to_string())
    print(dec[["procedure", "system", "insurer", "both"]].round(2).to_string())


if __name__ == "__main__":
    main()
