"""Atlanta Hospital Price Checker: Streamlit app."""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import theme
from theme import BLUE, DOT_GREEN, DOT_RED, PRICE_SCALE, SYSTEM_COLORS, cards

ROOT = Path(__file__).resolve().parents[1]
MAJOR = ["Anthem BCBS", "UnitedHealthcare", "Aetna", "Cigna", "Kaiser"]

st.set_page_config(page_title="Atlanta Hospital Price Checker", page_icon="⚕️", layout="wide")
st.markdown(theme.CSS, unsafe_allow_html=True)


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


st.markdown(f"""<div class="hero">
<div class="eyebrow">Atlanta Hospital Price Checker</div>
<h1>Same procedure.<br>Very different price.</h1>
<p>See what {nums['n_procedures']} common procedures cost at {nums['n_hospitals']} Atlanta hospitals with your insurance,
using the prices hospitals are required to publish.</p></div>""", unsafe_allow_html=True)

tab_search, tab_find, tab_about = st.tabs(["Compare prices", "What we found", "How it works"])

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
    ratio = f"The priciest hospital charges {hi.price / lo.price:.1f}× as much" if lo.price > 0 else ""
    st.markdown(cards([("Cheapest", money(lo.price), lo.hospital, "good"),
                       ("Most expensive", money(hi.price), hi.hospital, "bad"),
                       ("You could save", money(hi.price - lo.price), ratio, "accent")]), unsafe_allow_html=True)
    st.caption(f"Showing each hospital's {label} for **{choice}** (the hospital's own fee). "
               "Doctor's fees are billed separately and are not included.")

    mc, tc = st.columns([3, 2])
    fig = px.scatter_map(have, lat="lat", lon="lon", color="price", size=[14] * len(have),
                         color_continuous_scale=PRICE_SCALE, hover_name="hospital",
                         hover_data={"price": ":$,.0f", "lat": False, "lon": False, "stars": True},
                         zoom=8.4, height=460, map_style="carto-positron")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), coloraxis_showscale=False)
    mc.plotly_chart(fig, width="stretch", theme=None)

    table = have.assign(Price=have.price.map(money), Quality=have.stars.map(lambda s: "★" * int(s) + "☆" * (5 - int(s))))
    tc.dataframe(table[["hospital", "Price", "Quality"]].rename(columns={"hospital": "Hospital"}),
                 hide_index=True, width="stretch", height=460,
                 column_config={"Hospital": st.column_config.TextColumn(width=210),
                                "Price": st.column_config.TextColumn(width=72),
                                "Quality": st.column_config.TextColumn("Quality", width=96,
                                                                       help="Medicare overall star rating")})
    st.caption("Green = cheaper, red = pricier." + (" No published price for this option at: " + ", ".join(missing) + "."
               if missing else ""))

    if pay not in MAJOR and not pay.startswith("Paying cash"):
        st.markdown('<div class="section-label">By insurer</div>', unsafe_allow_html=True)
        st.subheader("Your insurer changes the price too")
        grid = by_brand[by_brand.code == code].pivot_table(index="hospital", columns="brand", values="price")
        if not grid.empty:
            gfig = px.imshow(grid, text_auto="$,.0f", aspect="auto", color_continuous_scale=PRICE_SCALE,
                             labels=dict(color="Price"))
            gfig.update_traces(textfont=dict(color="#1A1B20", size=12), xgap=2, ygap=2)
            gfig.update_layout(height=560, margin=dict(l=0, r=10, t=40, b=10), xaxis_title=None, yaxis_title=None,
                               xaxis=dict(side="top", tickfont=dict(color="#1A1B20", size=13)),
                               coloraxis_showscale=False)
            st.plotly_chart(gfig, width="stretch", theme=None)
            st.caption("Each cell is what that insurer has agreed to pay that hospital. Blank = not published.")

    st.markdown('<div class="note">Estimates only, from each hospital\'s published price file. Your share depends on '
                'your deductible and plan. Call the hospital and your insurer to confirm before you book.</div>',
                unsafe_allow_html=True)

# ---------------------------------------------------------------- findings
with tab_find:
    st.markdown("""<div class="callout"><div class="eyebrow">The biggest gap we found</div>
<h2>The same surgery, twice the price, 8 miles apart.</h2>
<p>With <strong>Cigna</strong>, a hip or knee replacement is listed at <strong>$37,652</strong> at Emory Johns Creek
Hospital and <strong>$75,616</strong> at Wellstar North Fulton Hospital, 8.3 miles away: a <strong>$37,964</strong>
difference for the same insurer and the same operation.</p></div>""", unsafe_allow_html=True)
    ve = nums["variance_explained"]
    st.markdown(cards([("Typical gap", f"{nums['median_ratio']:.1f}×", "cheapest vs priciest hospital", ""),
                       ("vs Medicare Advantage", f"{nums['commercial_vs_ma_multiple']:.1f}×", "commercial rate, same hospital", ""),
                       ("Explained by insurer", f"{ve['insurer']:.0%}", "of price differences", "accent"),
                       ("Explained by hospital", f"{ve['system']:.0%}", "system, of price differences", "")]),
                unsafe_allow_html=True)

    st.markdown('<div class="section-label">Spread</div>', unsafe_allow_html=True)
    st.subheader("Prices vary a lot between hospitals")
    sp = spread.sort_values("ratio")
    rfig = go.Figure()
    for r in sp.itertuples():
        rfig.add_trace(go.Scatter(x=[r.cheapest_price, r.priciest_price], y=[r.procedure] * 2, mode="lines",
                                  line=dict(color="#D2D2D7", width=3), showlegend=False, hoverinfo="skip"))
    for col, name, color, who in [("cheapest_price", "Cheapest hospital", DOT_GREEN, "cheapest"),
                                  ("priciest_price", "Most expensive hospital", DOT_RED, "priciest")]:
        rfig.add_trace(go.Scatter(x=sp[col], y=sp.procedure, mode="markers", name=name,
                                  marker=dict(color=color, size=11), customdata=sp[[who, "ratio"]],
                                  hovertemplate="%{customdata[0]}<br>$%{x:,.0f} (%{customdata[1]:.1f}× gap)<extra></extra>"))
    rfig.update_layout(height=780, xaxis_type="log", xaxis_title="Typical insured price (log scale)",
                       xaxis=dict(tickvals=[10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000],
                                  ticktext=["$10", "$30", "$100", "$300", "$1k", "$3k", "$10k", "$30k", "$100k"]),
                       legend=dict(orientation="h", y=1.03, x=0), margin=dict(l=0, r=10, t=30, b=64))
    st.plotly_chart(rfig, width="stretch", theme=None)
    st.caption("For each procedure: the cheapest and most expensive hospital's typical insured price. "
               "The median procedure costs about 2× more at the priciest hospital.")

    st.markdown('<div class="section-label">Hospital vs. insurer</div>', unsafe_allow_html=True)
    st.subheader("Your insurer matters about as much as your hospital")
    vd = var.melt(id_vars=["procedure"], value_vars=["system", "insurer"], var_name="factor", value_name="share")
    vd["factor"] = vd.factor.map({"system": "Hospital system", "insurer": "Insurer"})
    order = var.sort_values("system").procedure.tolist()
    vfig = px.bar(vd, x="share", y="procedure", color="factor", barmode="group", height=760,
                  category_orders={"procedure": order}, color_discrete_map={"Hospital system": "#9B5DE5", "Insurer": BLUE})
    vfig.update_layout(xaxis_tickformat=".0%", xaxis_title="Share of price differences explained", yaxis_title=None,
                       legend_title=None, legend=dict(orientation="h", y=1.03, x=0),
                       margin=dict(l=0, r=10, t=30, b=64))
    st.plotly_chart(vfig, width="stretch", theme=None)
    st.markdown(
        f"Knowing only the hospital system explains about **{nums['variance_explained']['system']:.0%}** of the price "
        f"differences for a typical procedure; knowing only the insurer explains **{nums['variance_explained']['insurer']:.0%}**; "
        f"both together explain **{nums['variance_explained']['both']:.0%}**. For hospital stays (childbirth, joint replacement) "
        "and ER visits the hospital system matters most; for imaging and lab tests, the insurer matters about as much. "
        "Prices are mostly set system-wide: every Emory hospital charges a given insurer the same rate for a brain MRI.")

    st.markdown('<div class="section-label">Quality</div>', unsafe_allow_html=True)
    st.subheader("Higher prices don't mean higher quality")
    ifig = px.scatter(idx, x="stars", y="price_index", color="system", hover_name="hospital", height=420,
                      color_discrete_map=SYSTEM_COLORS)
    ifig.update_traces(marker=dict(size=13))
    ifig.update_layout(xaxis_title="Medicare quality rating (stars)", yaxis_title="Price index (1.0 = typical Atlanta hospital)",
                       xaxis=dict(dtick=1), legend=dict(orientation="h", y=1.08, x=0, title=None),
                       margin=dict(l=10, r=10, t=40, b=64))
    st.plotly_chart(ifig, width="stretch", theme=None)
    st.caption(f"Rank correlation between price and star rating: {nums['stars_price_spearman']:.2f} "
               "(close to zero, and only 18 hospitals, so we can't claim any link either way).")

    st.markdown('<div class="section-label">Cash prices</div>', unsafe_allow_html=True)
    st.subheader("The 'cash price' isn't always a discount")
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
