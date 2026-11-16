# Atlanta Hospital Price Checker

**The same procedure can cost twice as much at a hospital a few miles away, and your insurer matters as much as your hospital.**

Hospitals have been required to publish their prices since 2021, but the files are huge (up to 440 MB each) and unreadable for patients. This project turns the price files of 18 metro Atlanta hospitals into:

1. **A price checker:** type a procedure in plain English ("knee MRI", "having a baby"), choose your insurer or cash, and see every hospital's price on a map, cheapest first, with its Medicare quality rating.
2. **An analysis** of how much prices vary and why.

Built for GenHacks 2026 (Healthcare & Environmental track).

## Key findings

| Finding | Number |
|---|---|
| Same insurer (Cigna), same hip/knee replacement, hospitals 8.3 miles apart | **$37,652** (Emory Johns Creek) vs **$75,616** (Wellstar North Fulton) |
| Typical gap between the cheapest and priciest hospital, per procedure | **2.0×** (up to 6.5× for an echocardiogram) |
| Share of price differences explained by the **insurer** / by the **hospital system** | **34%** / **31%** (both together: 74%) |
| Commercial insurers vs Medicare Advantage, same hospital and procedure | **2.5×** |
| Link between price and Medicare quality stars | **none detectable** (rank correlation 0.22, 18 hospitals) |
| Posted "discounted cash price" vs list price | 70% off at Piedmont, 61% off at Wellstar, **no discount** at Emory and Grady |

Prices are mostly set system-wide: every Emory hospital charges a given insurer the same amount for a brain MRI. So the choice that matters most is the **hospital system**, combined with **your insurer's contract with it**.

## Data

| Source | What |
|---|---|
| Hospital price files (`/cms-hpt.txt` on each hospital's site) | 18 hospitals: 6 Emory, 6 Piedmont, 5 Wellstar, Grady. 3.2 GB of raw files. |
| CMS Care Compare, Hospital General Information | Overall star rating (1–5) |
| U.S. Census Geocoder | Hospital map coordinates |

Northside Hospital is not included: its price files block automated downloads.

## Method

- **Procedures:** 30 common shoppable services by CPT code (imaging, labs, scopes, outpatient surgery, ER visits, therapy) and MS-DRG (childbirth, C-section, joint replacement).
- **Like-for-like prices:** keep the hospital's facility charge; drop doctor's fees and modified codes (e.g. the radiologist's reading only); prefer the hospital's direct fee for the procedure code over internal line items that carry the code only as a secondary code.
- **Typical insured price:** the median of the commercial negotiated rates of the five largest insurers (Anthem BCBS, UnitedHealthcare, Aetna, Cigna, Kaiser).
- **Hospital vs insurer:** for each procedure, the share of the variation in log price explained by hospital-system dummies, insurer dummies, and both (R²). The table reports the median across procedures.
- **Quality:** Spearman correlation between each hospital's price index (geometric mean of its price relative to the median hospital, across procedures) and its star rating.

The headline example was checked by hand against the original hospital files.

## Limits

- These are **posted** rates. What a patient pays depends on deductible, coinsurance and plan.
- Facility fees only; doctor and anesthesia fees are billed separately.
- Some hospitals publish only a formula (e.g. a percent of charges) for some insurers; those rates are converted to dollars by the hospital, not by us.
- 18 hospitals in 4 systems: patterns between systems are clearer than between individual hospitals.

## Run it

```bash
uv sync                          # or: pip install -r requirements.txt duckdb
uv run python src/download.py    # ~3.2 GB of hospital price files into data/raw/
uv run python src/extract.py     # rows for our 30 procedures
uv run python src/clean.py       # comparable prices
uv run python src/analyze.py     # results/
uv run streamlit run app/app.py
```

The cleaned data and results are committed, so the app runs without the download step.

## Built with

Python, DuckDB, pandas, Streamlit, Plotly. AI: Claude Code (Anthropic) helped write the data pipeline and app.
