"""Visual system: light, quiet, Apple-like; a touch of Cluely's soft sky wash.

Apple light UI: #FBFBFD canvas, #1D1D1F text, #0071E3 blue, system font (SF on Apple devices),
white cards with hairline borders and soft shadows, segmented control for tabs.
"""
import plotly.graph_objects as go
import plotly.io as pio

# --- tokens ---------------------------------------------------------------
BG = "#FBFBFD"
CARD = "#FFFFFF"
TEXT = "#1D1D1F"
TEXT_2 = "#515154"
TEXT_3 = "#86868B"
LINE = "#E5E5EA"
BLUE = "#0071E3"
GREEN = "#248A3D"       # Apple green, darkened for text contrast on white
RED = "#D70015"         # Apple red, darkened for text contrast on white
DOT_GREEN = "#34C759"   # chart marks
DOT_RED = "#FF3B30"
PRICE_SCALE = [[0, "#34C759"], [0.5, "#FFCC00"], [1, "#FF3B30"]]
SYSTEM_COLORS = {"Emory": "#0071E3", "Piedmont": "#AF52DE", "Wellstar": "#30B0C7", "Grady": "#FF9500"}
FONT = ("-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', Inter, 'Helvetica Neue', "
        "Helvetica, Arial, sans-serif")

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{ --text: {TEXT}; --text-2: {TEXT_2}; --text-3: {TEXT_3}; --line: {LINE}; --blue: {BLUE}; }}
.stApp {{
  -webkit-font-smoothing: antialiased;
  background: linear-gradient(180deg, #EEF4FD 0px, #F6F9FE 260px, {BG} 560px);
}}
.stApp :is(h1,h2,h3,h4,h5,h6,p,li,a,label,input,textarea,button,div,span,td,th):not([data-testid="stIconMaterial"]) {{
  font-family: {FONT} !important;
}}
header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer, [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stToolbar"] {{ display: none !important; }}
.block-container {{ max-width: 1120px; padding-top: 3.5rem; }}

/* type */
h1, h2, h3 {{ color: var(--text); font-weight: 600; }}
h2 {{ font-size: 2rem; line-height: 1.12; letter-spacing: -0.02em; }}
h3 {{ font-size: 1.5rem; line-height: 1.2; letter-spacing: -0.015em; }}
p, li {{ color: var(--text-2); line-height: 1.55; }}
strong {{ color: var(--text); font-weight: 600; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: var(--text-3) !important; }}
a {{ color: var(--blue) !important; text-decoration: none; }}

.hero {{ text-align: center; max-width: 760px; margin: 0 auto; }}
.hero .eyebrow {{ color: var(--blue); font-weight: 600; font-size: 1rem; letter-spacing: -0.005em; }}
.hero h1 {{ font-size: clamp(2.4rem, 5.4vw, 4rem); line-height: 1.05; letter-spacing: -0.03em; font-weight: 700;
  color: var(--text); margin: .5rem 0 1rem; padding: 0; }}
.hero p {{ font-size: 1.2rem; line-height: 1.5; color: var(--text-2); margin: 0 auto; max-width: 620px; }}
.section-label {{ color: var(--blue); font-weight: 600; font-size: .95rem; margin: 3rem 0 .1rem; }}

/* tabs: Apple segmented control */
[data-testid="stTabs"] [role="tablist"] {{ gap: 2px; background: #E8E8ED; border: none !important; box-shadow: none !important;
  padding: 3px; border-radius: 10px; width: fit-content; margin: 2.4rem auto 2rem; height: auto; }}
[data-testid="stTab"] {{ height: 34px; padding: 0 20px; border-radius: 8px; cursor: pointer; transition: background 150ms ease; }}
[data-testid="stTab"] p {{ color: var(--text) !important; font-weight: 500; font-size: .9rem; margin: 0; }}
[data-testid="stTab"][aria-selected="true"] {{ background: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 1px 1px rgba(0,0,0,.04); }}
[data-testid="stTab"] .react-aria-SelectionIndicator {{ display: none !important; }}
[data-testid="stTab"]:focus-visible {{ outline: 2px solid var(--blue); outline-offset: 2px; }}
@media (max-width: 520px) {{
  [data-testid="stTabs"] [role="tablist"] {{ width: 100%; }}
  [data-testid="stTab"] {{ flex: 1 1 0; padding: 0 6px; justify-content: center; }}
  [data-testid="stTab"] p {{ font-size: .8rem; white-space: nowrap; }}
}}

/* inputs */
[data-baseweb="input"], [data-baseweb="select"] > div {{ background: #FFFFFF !important; border: 1px solid #D2D2D7 !important;
  border-radius: 12px !important; min-height: 46px; transition: border-color 150ms ease, box-shadow 150ms ease; }}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {{
  border-color: var(--blue) !important; box-shadow: 0 0 0 4px rgba(0,113,227,.15); }}
[data-testid="stWidgetLabel"] p {{ font-size: .9rem !important; font-weight: 500; color: var(--text) !important; }}

/* cards */
.cards {{ display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: 16px; margin: 1.4rem 0 .6rem; }}
@media (max-width: 760px) {{ .cards {{ grid-template-columns: 1fr; }} }}
.card {{ padding: 22px 24px; border-radius: 18px; background: {CARD}; border: 1px solid var(--line);
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 8px 24px -12px rgba(0,0,0,.08); }}
.card .k {{ font-size: .9rem; font-weight: 500; color: var(--text-2); }}
.card .v {{ font-size: 2.4rem; line-height: 1.1; font-weight: 600; letter-spacing: -0.025em; color: var(--text);
  margin: 8px 0 4px; font-variant-numeric: tabular-nums; }}
.card .s {{ font-size: .9rem; color: var(--text-3); }}
.card.good .v {{ color: {GREEN}; }} .card.bad .v {{ color: {RED}; }} .card.accent .v {{ color: var(--blue); }}

.callout {{ padding: 30px 32px; border-radius: 20px; background: {CARD}; border: 1px solid var(--line); margin: .4rem 0 1rem;
  box-shadow: 0 1px 2px rgba(0,0,0,.04), 0 8px 24px -12px rgba(0,0,0,.08); }}
.callout .eyebrow {{ color: {RED}; font-weight: 600; font-size: .95rem; }}
.callout h2 {{ margin: .3rem 0 .7rem; font-size: clamp(1.7rem, 3.4vw, 2.4rem); letter-spacing: -0.025em; }}
.callout p {{ margin: 0; font-size: 1.05rem; }}
.note {{ padding: 14px 18px; border-radius: 12px; background: #F5F5F7; color: var(--text-2); font-size: .9rem; margin-top: 1.2rem; }}

[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {{ border: 1px solid var(--line); border-radius: 16px;
  overflow: hidden; background: {CARD}; }}
[data-testid="stPlotlyChart"] {{ padding: 10px 8px 4px; }}

@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
"""

# --- plotly template ------------------------------------------------------
pio.templates["apple_light"] = go.layout.Template(layout=dict(
    font=dict(family=FONT, color=TEXT_2, size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=[BLUE, "#AF52DE", "#30B0C7", "#FF9500", DOT_GREEN, DOT_RED],
    xaxis=dict(automargin=True, gridcolor="#F0F0F3", zerolinecolor="#E5E5EA", linecolor=LINE,
               tickfont=dict(color=TEXT_3), title=dict(font=dict(color=TEXT_3, size=12))),
    yaxis=dict(automargin=True, gridcolor="#F0F0F3", zerolinecolor="#E5E5EA", linecolor=LINE,
               tickfont=dict(color=TEXT_2), title=dict(font=dict(color=TEXT_3, size=12))),
    legend=dict(font=dict(color=TEXT_2), bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=LINE, font=dict(family=FONT, color=TEXT)),
    coloraxis=dict(colorbar=dict(outlinewidth=0, tickfont=dict(color=TEXT_3), title=dict(font=dict(color=TEXT_3)))),
))
pio.templates.default = "apple_light"


def cards(items, n=None):
    """items: list of (label, value, sub, variant) -> card row HTML."""
    html = "".join(f'<div class="card {v}"><div class="k">{k}</div><div class="v">{val}</div>'
                   f'<div class="s">{s}</div></div>' for k, val, s, v in items)
    return f'<div class="cards" style="--n:{n or len(items)}">{html}</div>'
