"""Visual system: near-black canvas, Apple dark-mode system colors, Geist type.

Inspired by Apple's dark UI (system colors, #F5F5F7 text, frosted glass), Cluely (soft
gradient glow, glassy hairline cards) and Studio Freight's Dragonfly (oversized tight
display type, small mono labels).
"""
import plotly.graph_objects as go
import plotly.io as pio

# --- tokens ---------------------------------------------------------------
BG = "#0A0A0C"
SURFACE = "#141418"
TEXT = "#F5F5F7"        # Apple primary label (dark)
TEXT_2 = "#A1A1A6"      # secondary label
TEXT_3 = "#6E6E73"      # tertiary label
HAIRLINE = "rgba(255,255,255,0.08)"
BLUE = "#0A84FF"        # Apple systemBlue (dark)
VIOLET = "#5E5CE6"      # systemIndigo (dark)
GREEN = "#30D158"       # cheap
AMBER = "#FF9F0A"       # middle
RED = "#FF453A"         # expensive
PRICE_SCALE = [[0, GREEN], [0.5, AMBER], [1, RED]]
SYSTEM_COLORS = {"Emory": "#0A84FF", "Piedmont": "#BF5AF2", "Wellstar": "#64D2FF", "Grady": "#FFD60A"}
FONT = "Geist, -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif"
MONO = "'Geist Mono', 'SF Mono', ui-monospace, monospace"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap');

:root {{
  --bg: {BG}; --surface: {SURFACE}; --text: {TEXT}; --text-2: {TEXT_2}; --text-3: {TEXT_3};
  --hair: {HAIRLINE}; --blue: {BLUE}; --green: {GREEN}; --red: {RED};
}}
.stApp {{ -webkit-font-smoothing: antialiased; }}
/* Streamlit sets fonts per element, so override them all; keep icon glyph fonts intact */
.stApp :is(h1,h2,h3,h4,h5,h6,p,li,a,label,input,textarea,button,div,span,td,th):not([data-testid="stIconMaterial"]) {{
  font-family: {FONT} !important;
}}
.stApp {{
  background:
    radial-gradient(1200px 520px at 50% -180px, rgba(10,132,255,0.22), transparent 70%),
    radial-gradient(700px 380px at 85% -120px, rgba(94,92,230,0.20), transparent 70%),
    var(--bg);
}}
header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer, [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stToolbar"] {{ display: none !important; }}
.block-container {{ max-width: 1240px; padding-top: 3.2rem; }}

/* type */
h1, h2, h3 {{ color: var(--text); letter-spacing: -0.025em; font-weight: 600; }}
h2 {{ font-size: 2rem; line-height: 1.1; }}
h3 {{ font-size: 1.35rem; line-height: 1.2; letter-spacing: -0.015em; }}
p, li {{ color: var(--text-2); line-height: 1.6; }}
strong {{ color: var(--text); font-weight: 600; }}
[data-testid="stCaptionContainer"], .stCaption {{ color: var(--text-3) !important; }}
a {{ color: var(--blue) !important; text-decoration: none; }}

.eyebrow {{ font-family: {MONO}; font-size: .72rem; letter-spacing: .14em; text-transform: uppercase;
  color: var(--text-3); display: flex; align-items: center; gap: .6rem; }}
.eyebrow .dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--green);
  box-shadow: 0 0 10px var(--green); }}
.hero h1 {{ font-size: clamp(2.6rem, 6vw, 4.6rem); line-height: 1.02; letter-spacing: -0.045em;
  font-weight: 600; margin: .9rem 0 .8rem; padding: 0;
  background: linear-gradient(180deg, #FFFFFF 30%, #8E8E93 130%); -webkit-background-clip: text;
  background-clip: text; color: transparent; }}
.hero p {{ font-size: 1.12rem; max-width: 640px; color: var(--text-2); margin: 0; }}
.section-label {{ font-family: {MONO}; font-size: .7rem; letter-spacing: .14em; text-transform: uppercase;
  color: var(--blue); margin: 2.6rem 0 .3rem; }}

/* tabs as a segmented control */
[data-testid="stTabs"] [role="tablist"] {{ gap: 4px; background: rgba(255,255,255,0.04);
  border: 1px solid var(--hair) !important; box-shadow: none !important; padding: 4px; border-radius: 999px;
  width: fit-content; margin: 2.2rem 0 1.6rem; height: auto; }}
[data-testid="stTab"] {{ height: 38px; padding: 0 18px; border-radius: 999px; cursor: pointer;
  transition: background 160ms ease; }}
[data-testid="stTab"] p {{ color: var(--text-2) !important; font-weight: 500; font-size: .92rem; margin: 0; }}
[data-testid="stTab"]:hover {{ background: rgba(255,255,255,0.05); }}
[data-testid="stTab"][aria-selected="true"] {{ background: rgba(255,255,255,0.11);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }}
[data-testid="stTab"][aria-selected="true"] p {{ color: var(--text) !important; }}
[data-testid="stTab"] .react-aria-SelectionIndicator {{ display: none !important; }}
@media (max-width: 520px) {{
  [data-testid="stTabs"] [role="tablist"] {{ width: 100%; max-width: 100%; }}
  [data-testid="stTab"] {{ flex: 1 1 0; padding: 0 8px; justify-content: center; }}
  [data-testid="stTab"] p {{ font-size: .8rem; white-space: nowrap; }}
}}
[data-testid="stTab"]:focus-visible {{ outline: 2px solid var(--blue); outline-offset: 2px; }}

/* inputs */
[data-baseweb="input"], [data-baseweb="select"] > div {{ background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--hair) !important; border-radius: 14px !important; min-height: 48px;
  transition: border-color 160ms ease, box-shadow 160ms ease; }}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {{
  border-color: rgba(10,132,255,.7) !important; box-shadow: 0 0 0 4px rgba(10,132,255,.18); }}
label p {{ font-family: {MONO}; font-size: .72rem !important; letter-spacing: .1em; text-transform: uppercase;
  color: var(--text-3) !important; }}

/* glass cards */
.cards {{ display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: 14px; margin: 1.4rem 0 .6rem; }}
@media (max-width: 760px) {{ .cards {{ grid-template-columns: 1fr; }} }}
.card {{ position: relative; padding: 22px 22px 20px; border-radius: 20px; border: 1px solid var(--hair);
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
  backdrop-filter: blur(24px) saturate(160%); -webkit-backdrop-filter: blur(24px) saturate(160%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 20px 40px -24px rgba(0,0,0,.8);
  animation: rise 420ms cubic-bezier(.2,.8,.2,1) both; }}
.card:nth-child(2) {{ animation-delay: 50ms; }} .card:nth-child(3) {{ animation-delay: 100ms; }}
.card:nth-child(4) {{ animation-delay: 150ms; }}
.card .k {{ font-family: {MONO}; font-size: .7rem; letter-spacing: .12em; text-transform: uppercase; color: var(--text-3); }}
.card .v {{ font-size: 2.5rem; line-height: 1.05; font-weight: 600; letter-spacing: -0.035em; color: var(--text);
  margin: 10px 0 6px; font-variant-numeric: tabular-nums; }}
.card .s {{ font-size: .9rem; color: var(--text-2); }}
.card.good .v {{ color: var(--green); }} .card.bad .v {{ color: var(--red); }}
.card.accent {{ border-color: rgba(10,132,255,.35);
  background: linear-gradient(180deg, rgba(10,132,255,0.16), rgba(10,132,255,0.03)); }}

.callout {{ padding: 26px 28px; border-radius: 22px; border: 1px solid var(--hair); margin: .4rem 0 1rem;
  background: radial-gradient(600px 200px at 0% 0%, rgba(255,69,58,0.14), transparent 70%), rgba(255,255,255,0.03); }}
.callout h2 {{ margin: 0 0 .6rem; font-size: clamp(1.8rem, 3.6vw, 2.6rem); letter-spacing: -0.035em; }}
.callout p {{ margin: 0; font-size: 1.05rem; }}
.note {{ padding: 14px 18px; border-radius: 14px; border: 1px solid var(--hair); background: rgba(255,255,255,0.03);
  color: var(--text-2); font-size: .9rem; margin-top: 1.2rem; }}

/* data frames + charts sit on glass */
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {{ border: 1px solid var(--hair); border-radius: 18px;
  overflow: hidden; background: rgba(255,255,255,0.02); }}
[data-testid="stPlotlyChart"] {{ padding: 8px 6px 2px; }}

/* mono labels win over the global font rule (declared later, equal-or-higher specificity) */
.stApp :is(.eyebrow, .eyebrow *, .section-label, .card .k, [data-testid="stWidgetLabel"] p) {{
  font-family: {MONO} !important; }}

@keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
@media (prefers-reduced-motion: reduce) {{ .card {{ animation: none; }} * {{ transition: none !important; }} }}
@media (prefers-reduced-transparency: reduce) {{ .card {{ backdrop-filter: none; background: var(--surface); }} }}
</style>
"""

# --- plotly template ------------------------------------------------------
pio.templates["apple_dark"] = go.layout.Template(layout=dict(
    font=dict(family=FONT, color=TEXT_2, size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=[BLUE, "#BF5AF2", "#64D2FF", "#FFD60A", GREEN, RED],
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.10)", linecolor=HAIRLINE,
               tickfont=dict(color=TEXT_3), title=dict(font=dict(color=TEXT_3, size=12))),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.10)", linecolor=HAIRLINE,
               tickfont=dict(color=TEXT_2), title=dict(font=dict(color=TEXT_3, size=12))),
    legend=dict(font=dict(color=TEXT_2), bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#1C1C21", bordercolor="rgba(255,255,255,0.12)", font=dict(family=FONT, color=TEXT)),
    coloraxis=dict(colorbar=dict(outlinewidth=0, tickfont=dict(color=TEXT_3), title=dict(font=dict(color=TEXT_3)))),
))
pio.templates.default = "apple_dark"


def cards(items, n=None):
    """items: list of (label, value, sub, variant) -> glass card row HTML."""
    html = "".join(f'<div class="card {v}"><div class="k">{k}</div><div class="v">{val}</div>'
                   f'<div class="s">{s}</div></div>' for k, val, s, v in items)
    return f'<div class="cards" style="--n:{n or len(items)}">{html}</div>'
