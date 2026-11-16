"""Turn the extracted rows into one comparable price per (hospital, procedure, insurer plan).

Rules (each chosen so we compare like with like):
  * Keep the hospital's own charge: drop 'professional' (doctor's fee) rows and rows with
    modifiers (26 = doctor's reading only, TC = equipment only, 50 = both sides, ...).
  * Outpatient procedures (CPT): keep outpatient / 'both' settings.
    Inpatient stays (MS-DRG): keep inpatient / 'both'.
  * Keep only dollar amounts above $1 (placeholders like $0 / $0.01 are dropped).
  * Group insurers into brands and plans into Commercial / Medicare Advantage / Medicaid.
Outputs: data/prices.parquet (one row per hospital x procedure x insurer plan)
"""
import re
from pathlib import Path

import pandas as pd

from procedures import PROCEDURES

ROOT = Path(__file__).resolve().parents[1]

BRANDS = [
    ("Anthem BCBS", r"bcbs|blue cross|anthem|bluecross"),
    ("UnitedHealthcare", r"uhc|united|surest|optum"),
    ("Aetna", r"aetna"),
    ("Cigna", r"cigna"),
    ("Kaiser", r"kaiser"),
    ("Humana", r"humana"),
    ("Ambetter", r"ambetter"),
    ("Oscar", r"oscar"),
    ("CareSource", r"caresource"),
    ("Amerigroup", r"amerigroup|wellpoint"),
    ("Peach State", r"peach state"),
    ("WellCare", r"wellcare"),
    ("Alliant", r"alliant"),
]
MAJOR = {"Anthem BCBS", "UnitedHealthcare", "Aetna", "Cigna", "Kaiser"}


def brand(payer):
    p = str(payer).lower()
    for name, pat in BRANDS:
        if re.search(pat, p):
            return name
    return "Other"


def plan_type(payer, plan, brand_name):
    t = f"{payer} {plan}".lower()
    if re.search(r"tricare|champva|va ccn|vaccn|va community|workers comp|naphcare|pathways/marketplace", t):
        return "Other"
    if str(payer).strip().lower() == "medicare":
        return "Medicare"
    if re.search(r"medicare|advantage|\bmapd?\b|dsnp|d-snp|clover|devoted|clear spring|wellcare|sonder|pruitt", t):
        return "Medicare Advantage"
    if re.search(r"ambetter|exchange|marketplace|\bifp\b|connect", t):
        return "Commercial"
        return "Medicare Advantage"
    if re.search(r"medicaid|peach state|amerigroup|pathways|\bcms\b|\bpeachcare", t) or (
        brand_name == "CareSource" and "marketplace" not in t and "exchange" not in t):
        return "Medicaid"
    if re.search(r"tricare|champva|va ccn|vaccn|workers comp|naphcare", t):
        return "Other"
    return "Commercial"


def system_of(h):
    return h.split()[0] if not h.startswith("Grady") else "Grady"


def main():
    d = pd.read_parquet(ROOT / "data" / "extracted.parquet")
    n0 = len(d)
    d = d[d.billing_class.fillna("facility").str.lower() != "professional"]
    d = d[d.modifiers.isna() | (d.modifiers.astype(str).str.strip() == "")]
    is_drg = d.code_system == "MS-DRG"
    s = d.setting.str.lower()
    d = d[(is_drg & s.isin(["inpatient", "both"])) | (~is_drg & s.isin(["outpatient", "both"]))]
    d = d[d.code != "93000"]  # only one hospital lists it
    # Prefer the hospital's direct fee for the procedure code; use line items that only carry the
    # code as a secondary code when the hospital publishes no direct fee for it.
    has_direct = d.groupby(["hospital", "code"]).direct.transform("any")
    print(f"rows kept after like-for-like filters: {len(d)} of {n0}")

    d["brand"] = d.payer.map(brand)
    d["plan_type"] = [plan_type(p, q, b) for p, q, b in zip(d.payer, d.plan, d.brand)]
    d["system"] = d.hospital.map(system_of)

    neg = d[(d.direct | ~has_direct) & (d.negotiated > 1)]
    prices = (neg.groupby(["hospital", "system", "code", "brand", "plan_type", "payer", "plan"], dropna=False)
                 .negotiated.median().reset_index(name="price"))

    # Cash and list ("gross") prices, where the hospital ties them to the CPT/DRG code
    cash = (d[d.cash > 1].groupby(["hospital", "code"]).cash.median().reset_index())
    gross = (d[d.gross > 1].groupby(["hospital", "code"]).gross.median().reset_index())

    meta = pd.DataFrame(PROCEDURES, columns=["code", "code_system", "procedure", "category", "keywords"])
    prices = prices.merge(meta[["code", "procedure", "category"]], on="code")
    prices.to_parquet(ROOT / "data" / "prices.parquet", index=False)
    cash.merge(gross, how="outer", on=["hospital", "code"]).to_parquet(ROOT / "data" / "cash_gross.parquet", index=False)

    print(prices.plan_type.value_counts().to_string())
    print(prices.groupby("plan_type").brand.value_counts().to_string())
    print(f"saved {len(prices)} hospital x procedure x plan prices")


if __name__ == "__main__":
    main()
