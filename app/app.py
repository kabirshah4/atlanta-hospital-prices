"""Atlanta Hospital Price Checker: Streamlit app."""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
MAJOR = ["Anthem BCBS", "UnitedHealthcare", "Aetna", "Cigna", "Kaiser"]
SYSTEM_COLORS = {"Emory": "#1f6feb", "Piedmont": "#8250df", "Wellstar": "#1a7f37", "Grady": "#bf8700"}

st.set_page_config(page_title="Atlanta Hospital Price Checker", page_icon="🏥", layout="wide")


@st.cache_data
def load():
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from procedures import PROCEDURES
    procs = pd.DataFrame(PROCEDURES, columns=["code", "code_system", "procedure", "category", "keywords"])
    procs = procs[procs.code != "93000"]
    prices = pd.read_parquet(ROOT / "data" / "prices.parquet")
    hosp = pd.read_csv(ROOT / "data" / "hospitals.csv")
    hp = pd.read_csv(ROOT / "results" / "hospital_procedure_prices.csv", dtype={"code": str})
    nums = json.loads((ROOT / "results" / "numbers.json").read_text())
    var = pd.read_csv(ROOT / "results" / "variance_explained.csv", dtype={"code": str})
    idx = pd.read_csv(ROOT / "results" / "hospital_price_index.csv")
    spread = pd.read_csv(ROOT / "results" / "spread_by_procedure.csv", dtype={"code": str})
    comm = prices[(prices.plan_type == "Commercial") & prices.brand.isin(MAJOR)]
    by_brand = comm.groupby(["hospital", "code", "brand"]).price.median().reset_index()
    return procs, hosp, hp, by_brand, nums, var, idx, spread


procs, hosp, hp, by_brand, nums, var, idx, spread = load()


def money(x):
    return "—" if pd.isna(x) else f"${x:,.0f}"


def search(q):
    words = [w for w in q.lower().replace("-", " ").split() if len(w) > 1]
    if not words:
        return procs
    text = (procs.procedure + " " + procs.keywords).str.lower()
    score = sum(text.str.contains(w, regex=False).astype(int) for w in words)
    return procs[score > 0].assign(score=score[score > 0]).sort_values("score", ascending=False)


st.title("🏥 Atlanta Hospital Price Checker")
st.caption(f"Real prices from {nums['n_hospitals']} metro Atlanta hospitals' own price files, "
           f"for {nums['n_procedures']} common procedures. Same procedure, very different prices.")

tab_search, tab_find, tab_about = st.tabs(["🔎 Compare prices", "📊 What we found", "ℹ️ How it works"])

# ---------------------------------------------------------------- search
with tab_search:
    c1, c2 = st.columns([3, 2])
    q = c1.text_input("What do you need?", placeholder="e.g. knee MRI, having a baby, colonoscopy, blood test")
    matches = search(q)
    if matches.empty:
        st.warning("No match. Try simpler words like 'MRI', 'CT', 'baby', 'blood test' or 'ER'.")
        st.stop()
    choice = c1.selectbox("Procedure", matches.procedure.tolist())
    pay = c2.selectbox("How will you pay?", ["My insurer isn't listed / not sure"] + MAJOR + ["Paying cash (no insurance)"])
    code = procs.loc[procs.procedure == choice, "code"].iloc[0]

    view = hosp[["hospital", "system", "stars", "lat", "lon", "address"]].copy()
    if pay in MAJOR:
        pr = by_brand[(by_brand.code == code) & (by_brand.brand == pay)][["hospital", "price"]]
        label = f"{pay} negotiated price"
    elif pay.startswith("Paying cash"):
        pr = hp[hp.code == code][["hospital", "cash"]].rename(columns={"cash": "price"})
        label = "cash price"
    else:
        pr = hp[hp.code == code][["hospital", "typical"]].rename(columns={"typical": "price"})
        label = "typical insured price (median of the 5 largest insurers)"
    view = view.merge(pr, on="hospital", how="left")
    have = view.dropna(subset=["price"]).sort_values("price")
    missing = view[view.price.isna()].hospital.tolist()

    if have.empty:
        st.info("These hospitals don't publish a price for this procedure and payment option.")
        st.stop()

    lo, hi = have.iloc[0], have.iloc[-1]
    m1, m2, m3 = st.columns(3)
    m1.metric("Cheapest", money(lo.price))
    m1.caption(lo.hospital)
    m2.metric("Most expensive", money(hi.price))
    m2.caption(hi.hospital)
    m3.metric("You could save", money(hi.price - lo.price))
    m3.caption(f"The priciest hospital charges {hi.price / lo.price:.1f}× as much" if lo.price > 0 else "")
    st.caption(f"Showing each hospital's {label} for **{choice}** (the hospital's own fee). "
               "Doctor's fees are billed separately and are not included.")

    mc, tc = st.columns([3, 2])
    fig = px.scatter_map(have, lat="lat", lon="lon", color="price", size=[14] * len(have),
                         color_continuous_scale=["#1a7f37", "#d4a72c", "#cf222e"], hover_name="hospital",
                         hover_data={"price": ":$,.0f", "lat": False, "lon": False, "stars": True},
                         zoom=8.4, height=460, map_style="carto-positron")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), coloraxis_colorbar=dict(title="Price", tickprefix="$"))
    mc.plotly_chart(fig, width="stretch")

    table = have.assign(Price=have.price.map(money), Quality=have.stars.map(lambda s: "★" * int(s) + "☆" * (5 - int(s))))
    tc.dataframe(table[["hospital", "Price", "Quality", "system"]].rename(columns={"hospital": "Hospital", "system": "System"}),
                 hide_index=True, width="stretch", height=460)
    if missing:
        st.caption("No published price for this option at: " + ", ".join(missing) + ".")

    if pay not in MAJOR and not pay.startswith("Paying cash"):
        st.subheader("Your insurer changes the price too")
        grid = by_brand[by_brand.code == code].pivot_table(index="hospital", columns="brand", values="price")
        if not grid.empty:
            gfig = px.imshow(grid, text_auto="$,.0f", aspect="auto", color_continuous_scale="RdYlGn_r",
                             labels=dict(color="Price"))
            gfig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(gfig, width="stretch")
            st.caption("Each cell is what that insurer has agreed to pay that hospital. Blank = not published.")

    st.info("Estimates only, from each hospital's published price file. Your share depends on your deductible and "
            "plan. Call the hospital and your insurer to confirm before you book.")

# ---------------------------------------------------------------- findings
with tab_find:
    st.header("The same surgery, twice the price, 8 miles apart")
    st.markdown(
        "With **Cigna** insurance, a hip or knee replacement is listed at **$37,652** at Emory Johns Creek Hospital "
        "and **$75,616** at Wellstar North Fulton Hospital, 8.3 miles away. That is a **$37,964** difference for "
        "the same insurer and the same operation.")

    a, b, c, d = st.columns(4)
    a.metric("Typical gap, cheapest vs priciest hospital", f"{nums['median_ratio']:.1f}×")
    b.metric("Commercial vs Medicare Advantage, same hospital", f"{nums['commercial_vs_ma_multiple']:.1f}×")
    c.metric("Price differences explained by insurer", f"{nums['variance_explained']['insurer']:.0%}")
    d.metric("…and by hospital system", f"{nums['variance_explained']['system']:.0%}")

    st.subheader("1. Prices vary a lot between hospitals")
    sp = spread.sort_values("ratio")
    rfig = go.Figure()
    for r in sp.itertuples():
        rfig.add_trace(go.Scatter(x=[r.cheapest_price, r.priciest_price], y=[r.procedure] * 2, mode="lines",
                                  line=dict(color="#c9ccd1", width=3), showlegend=False, hoverinfo="skip"))
    for col, name, color, who in [("cheapest_price", "Cheapest hospital", "#1a7f37", "cheapest"),
                                  ("priciest_price", "Most expensive hospital", "#cf222e", "priciest")]:
        rfig.add_trace(go.Scatter(x=sp[col], y=sp.procedure, mode="markers", name=name,
                                  marker=dict(color=color, size=11), customdata=sp[[who, "ratio"]],
                                  hovertemplate="%{customdata[0]}<br>$%{x:,.0f} (%{customdata[1]:.1f}× gap)<extra></extra>"))
    rfig.update_layout(height=760, xaxis_type="log", xaxis_title="Typical insured price (log scale)",
                       xaxis_tickprefix="$", legend=dict(orientation="h", y=1.04, x=0),
                       margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(rfig, width="stretch")
    st.caption("For each procedure: the cheapest and most expensive hospital's typical insured price. "
               "The median procedure costs about 2× more at the priciest hospital.")

    st.subheader("2. Your insurer matters about as much as your hospital")
    vd = var.melt(id_vars=["procedure"], value_vars=["system", "insurer"], var_name="factor", value_name="share")
    vd["factor"] = vd.factor.map({"system": "Hospital system", "insurer": "Insurer"})
    order = var.sort_values("system").procedure.tolist()
    vfig = px.bar(vd, x="share", y="procedure", color="factor", barmode="group", height=760,
                  category_orders={"procedure": order}, color_discrete_map={"Hospital system": "#8250df", "Insurer": "#1f6feb"})
    vfig.update_layout(xaxis_tickformat=".0%", xaxis_title="Share of price differences explained", yaxis_title=None,
                       legend_title=None, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(vfig, width="stretch")
    st.markdown(
        f"Knowing only the hospital system explains about **{nums['variance_explained']['system']:.0%}** of the price "
        f"differences for a typical procedure; knowing only the insurer explains **{nums['variance_explained']['insurer']:.0%}**; "
        f"both together explain **{nums['variance_explained']['both']:.0%}**. For hospital stays (childbirth, joint replacement) "
        "and ER visits the hospital system matters most; for imaging and lab tests, the insurer matters about as much. "
        "Prices are mostly set system-wide: every Emory hospital charges a given insurer the same rate for a brain MRI.")

    st.subheader("3. Higher prices don't mean higher quality")
    ifig = px.scatter(idx, x="stars", y="price_index", color="system", hover_name="hospital", height=420,
                      color_discrete_map=SYSTEM_COLORS)
    ifig.update_traces(marker=dict(size=13))
    ifig.update_layout(xaxis_title="Medicare quality rating (stars)", yaxis_title="Price index (1.0 = typical Atlanta hospital)",
                       xaxis=dict(dtick=1), margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(ifig, width="stretch")
    st.caption(f"Rank correlation between price and star rating: {nums['stars_price_spearman']:.2f} "
               "(close to zero, and only 18 hospitals, so we can't claim any link either way).")

    st.subheader("4. The 'cash price' isn't always a discount")
    cs = nums["cash_as_share_of_list"]
    st.markdown(
        f"Hospitals must post a discounted cash price. At Piedmont it is about **{1 - cs['Piedmont']:.0%} off** the list price "
        f"and at Wellstar **{1 - cs['Wellstar']:.0%} off**, but at Emory and Grady the posted cash price **equals the full list "
        f"price**. Paying cash beat the typical insured price in {nums['cash_cheaper_share']:.0%} of the "
        f"{nums['n_cash_compared']} cases where both were published.")

# ---------------------------------------------------------------- about
with tab_about:
    st.markdown(f"""
### Where the numbers come from
Since 2021, U.S. hospitals must publish a machine-readable file with their prices, including what each insurer has agreed
to pay ([45 CFR 180](https://www.cms.gov/priceTransparency)). Each hospital lists its file at `/cms-hpt.txt` on its website.
These files are huge (up to 440 MB each, 3.2 GB in total here) and nearly impossible for a patient to read.

**Hospitals:** {nums['n_hospitals']} adult hospitals in metro Atlanta from Emory, Piedmont, Wellstar and Grady.
Northside Hospital blocks automated downloads, so it is not included yet.
**Procedures:** {nums['n_procedures']} common "shoppable" services (imaging, lab tests, scopes, outpatient surgery, ER visits,
childbirth, joint replacement), identified by CPT code or, for hospital stays, by MS-DRG.
**Quality:** Medicare's overall hospital star rating (CMS Care Compare).

### How prices were made comparable
1. Keep only the hospital's own (facility) charge: drop doctor's fees and modified codes (e.g. the radiologist's reading only).
2. Prefer the hospital's direct fee for the procedure code; some hospitals also list internal line items priced as a percent
   of list price, which are used only when no direct fee is published.
3. **Typical insured price** = median of the commercial rates of the 5 largest insurers (Anthem BCBS, UnitedHealthcare,
   Aetna, Cigna, Kaiser).
4. Insurers are grouped by brand, and plans into commercial, Medicare Advantage and Medicaid.

### Limits
- These are **posted** prices. What you pay depends on your deductible, coinsurance and exact plan.
- Some hospitals don't publish every price, or publish only a formula for some.
- Facility fees only; doctor and anesthesia fees are extra.
- Only 18 hospitals in 4 systems, so system-level patterns are clearer than hospital-level ones.

### Built with
Python, DuckDB, pandas, Streamlit, Plotly; U.S. Census geocoder; CMS Care Compare.
AI tools: Claude Code (Anthropic) helped write the data pipeline and app; the headline example was checked by hand against the
original hospital files. Code: [GitHub](https://github.com/kabirshah4/atlanta-hospital-prices).
""")
