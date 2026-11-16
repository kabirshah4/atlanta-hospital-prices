"""Pull the rows for our procedures out of each hospital's price file.

Hospitals publish one of two CMS formats:
  * tall: one row per (item, payer, plan)            -- Emory, Wellstar, Piedmont
  * wide: one row per item, one column per payer/plan -- Grady
Both become one tidy table: data/extracted.parquet
"""
from pathlib import Path

import duckdb
import pandas as pd

from procedures import CODES

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "extracted.parquet"

con = duckdb.connect()
code_list = ",".join(f"'{c}'" for c in CODES)
# DRG codes are sometimes zero-padded ("0807"), CPT codes never are.
NORM = "ltrim({c}, '0')"


def read(path):
    return f"read_csv('{path}', skip=2, header=true, all_varchar=true, ignore_errors=true, max_line_size=10000000)"


def code_match_sql(cols):
    """For each row, find the first code|n that is one of our CPT / DRG codes."""
    cases = []
    for n in range(1, 5):
        if f"code|{n}" not in cols:
            continue
        c, t = f'"code|{n}"', f'upper("code|{n}|type")'
        cases.append(
            f"when {t} in ('CPT','HCPCS') and {c} in ({code_list}) then {c}||'|CPT' "
            f"when {t} = 'MS-DRG' and {NORM.format(c=c)} in ({code_list}) then {NORM.format(c=c)}||'|MS-DRG'"
        )
    return "case " + " ".join(cases) + " end"


def col(cols, name, alias):
    return f'"{name}" as {alias}' if name in cols else f"null as {alias}"


def extract_tall(path, hospital):
    src = read(path)
    cols = con.sql(f"select * from {src} limit 0").columns
    match = code_match_sql(cols)
    q = f"""
    select '{hospital.replace("'", "''")}' as hospital, split_part(m,'|',1) as code, split_part(m,'|',2) as code_system,
           description, {col(cols,'setting','setting')}, {col(cols,'billing_class','billing_class')},
           {col(cols,'modifiers','modifiers')}, payer_name as payer, plan_name as plan,
           try_cast("standard_charge|negotiated_dollar" as double) as negotiated,
           try_cast("standard_charge|gross" as double) as gross,
           try_cast("standard_charge|discounted_cash" as double) as cash,
           {col(cols,'standard_charge|methodology','methodology')}
    from (select *, {match} as m from {src}) where m is not null
    """
    return con.sql(q).df()


def extract_wide(path, hospital):
    src = read(path)
    cols = con.sql(f"select * from {src} limit 0").columns
    match = code_match_sql(cols)
    payer_cols = [c for c in cols if c.startswith("standard_charge|") and c.endswith("|negotiated_dollar")]
    base = con.sql(f"select *, {match} as m from {src}").filter("m is not null").df()
    keep = ["description", "setting", "billing_class", "modifiers", "standard_charge|gross",
            "standard_charge|discounted_cash", "m"]
    long = base[keep + payer_cols].melt(id_vars=keep, var_name="col", value_name="negotiated")
    long = long[long.negotiated.notna() & (long.negotiated != "")]
    parts = long.col.str.split("|", expand=True)
    out = pd.DataFrame({
        "hospital": hospital,
        "code": long.m.str.split("|").str[0],
        "code_system": long.m.str.split("|").str[1],
        "description": long.description,
        "setting": long.setting,
        "billing_class": long.billing_class,
        "modifiers": long.modifiers,
        "payer": parts[1],
        "plan": parts[2],
        "negotiated": pd.to_numeric(long.negotiated, errors="coerce"),
        "gross": pd.to_numeric(long["standard_charge|gross"], errors="coerce"),
        "cash": pd.to_numeric(long["standard_charge|discounted_cash"], errors="coerce"),
        "methodology": None,
    })
    return out


def main():
    frames = []
    for path in sorted(RAW.glob("*.csv")):
        hospital = path.stem.replace("_", " ").replace("Saint Josephs", "Saint Joseph's")
        header = path.open(errors="ignore").readlines(200000)[2]
        wide = "|negotiated_dollar" in header and "payer_name" not in header
        df = extract_wide(path, hospital) if wide else extract_tall(path, hospital)
        print(f"{hospital:40s} {'wide' if wide else 'tall'} {len(df):7d} rows")
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out.to_parquet(OUT, index=False)
    print(f"saved {len(out)} rows -> {OUT}")


if __name__ == "__main__":
    main()
