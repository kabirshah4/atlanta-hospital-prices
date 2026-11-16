"""Visual system, after cluely.com: sky-blue gradient hero with a serif headline (EB Garamond),
Geist for everything else, a glossy blue feature card, soft lavender-gray cards, and Apple
system colors for price meaning (green = cheaper, red = pricier).
"""
import plotly.graph_objects as go
import plotly.io as pio

# --- tokens ---------------------------------------------------------------
BG = "#FFFFFF"
SOFT = "#F1F3F8"        # Cluely's lavender-gray card
SOFT_2 = "#E9ECF4"
TEXT = "#1A1B20"
TEXT_2 = "#4B4F5C"
TEXT_3 = "#8A8F9E"
LINE = "#E3E6EE"
BLUE = "#2F6BEA"        # Cluely button blue
BLUE_SOFT = "#6C95F2"
GREEN = "#1F8A3B"       # text-safe green on light
RED = "#D21F2B"         # text-safe red on light
DOT_GREEN = "#34C759"
DOT_RED = "#FF3B30"
PRICE_SCALE = [[0, "#34C759"], [0.5, "#FFCC00"], [1, "#FF3B30"]]
SYSTEM_COLORS = {"Emory": "#2F6BEA", "Piedmont": "#9B5DE5", "Wellstar": "#2BB3C0", "Grady": "#F59E0B"}
FONT = "Geist, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
SERIF = "'EB Garamond', 'Iowan Old Style', Georgia, serif"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&family=Geist:wght@400;500;600&display=swap');

:root {{ --text: {TEXT}; --text-2: {TEXT_2}; --text-3: {TEXT_3}; --line: {LINE}; --blue: {BLUE}; --soft: {SOFT}; }}
.stApp {{
  -webkit-font-smoothing: antialiased;
  background:
    radial-gradient(900px 260px at 50% 470px, rgba(255,255,255,0.95), transparent 70%),
    linear-gradient(180deg, #2C67E0 0px, #4F87EE 150px, #8DB5F6 300px, #D3E4FB 430px, #F4F7FD 560px, {BG} 760px);
}}
.stApp :is(h1,h2,h3,h4,h5,h6,p,li,a,label,input,textarea,button,div,span,td,th):not([data-testid="stIconMaterial"]) {{
  font-family: {FONT} !important;
}}
header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer, [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stToolbar"] {{ display: none !important; }}
.block-container {{ max-width: 1100px; padding-top: 3.2rem; }}

/* type */
h1, h2, h3 {{ color: var(--text); font-weight: 500; }}
h2 {{ font-size: 2rem; line-height: 1.15; letter-spacing: -0.02em; }}
h3 {{ font-size: 1.75rem; line-height: 1.2; letter-spacing: -0.02em; }}
p, li {{ color: var(--text-2); line-height: 1.55; }}
strong {{ color: var(--text); font-weight: 600; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: var(--text-3) !important; }}
a {{ color: var(--blue) !important; text-decoration: none; }}

/* hero: serif on sky */
.hero {{ text-align: center; max-width: 780px; margin: 0 auto; padding-top: .4rem; }}
.hero .eyebrow {{ color: rgba(255,255,255,.85); font-weight: 500; font-size: .95rem; }}
.stApp .hero h1, .stApp .hero h1 * {{ font-family: {SERIF} !important; }}
.stApp .hero h1 {{ font-size: clamp(2.8rem, 6vw, 4.6rem); line-height: 1.04;
  letter-spacing: -0.015em; font-weight: 500; color: #FFFFFF; margin: .4rem 0 1rem; padding: 0;
  text-shadow: 0 2px 24px rgba(20,50,140,.25); }}
.hero p {{ font-size: 1.12rem; line-height: 1.5; color: rgba(255,255,255,.92); margin: 0 auto; max-width: 560px; }}
.section-label {{ color: var(--blue); font-weight: 500; font-size: .95rem; margin: 3.2rem 0 .1rem; }}

/* tabs: white segmented control with a glossy blue selected pill */
[data-testid="stTabs"] [role="tablist"] {{ gap: 4px; background: rgba(255,255,255,.75); border: 1px solid rgba(255,255,255,.9) !important;
  box-shadow: 0 8px 24px -10px rgba(40,80,180,.35) !important; padding: 4px; border-radius: 14px; width: fit-content;
  margin: 2.2rem auto 2.4rem; height: auto; backdrop-filter: blur(12px); }}
[data-testid="stTab"] {{ height: 36px; padding: 0 18px; border-radius: 10px; cursor: pointer; transition: background 150ms ease; }}
[data-testid="stTab"] p {{ color: var(--text-2) !important; font-weight: 500; font-size: .92rem; margin: 0; }}
[data-testid="stTab"]:hover {{ background: rgba(47,107,234,.07); }}
[data-testid="stTab"][aria-selected="true"] {{
  background: radial-gradient(120% 120% at 70% 85%, rgba(255,255,255,.35), rgba(255,255,255,0) 60%), linear-gradient(180deg, #4D86F3, {BLUE});
  box-shadow: 0 6px 14px -6px rgba(47,107,234,.7), inset 0 1px 0 rgba(255,255,255,.45), inset 0 -2px 4px rgba(20,40,160,.25); }}
[data-testid="stTab"][aria-selected="true"] p {{ color: #FFFFFF !important; }}
[data-testid="stTab"] .react-aria-SelectionIndicator {{ display: none !important; }}
[data-testid="stTab"]:focus-visible {{ outline: 2px solid var(--blue); outline-offset: 2px; }}
@media (max-width: 520px) {{
  [data-testid="stTabs"] [role="tablist"] {{ width: 100%; }}
  [data-testid="stTab"] {{ flex: 1 1 0; padding: 0 6px; justify-content: center; }}
  [data-testid="stTab"] p {{ font-size: .8rem; white-space: nowrap; }}
}}

/* inputs */
[data-baseweb="input"], [data-baseweb="select"] > div {{ background: #FFFFFF !important; border: 1px solid {LINE} !important;
  border-radius: 12px !important; min-height: 46px; box-shadow: 0 1px 2px rgba(20,30,70,.04);
  transition: border-color 150ms ease, box-shadow 150ms ease; }}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {{
  border-color: var(--blue) !important; box-shadow: 0 0 0 4px rgba(47,107,234,.14); }}
[data-testid="stWidgetLabel"] p {{ font-size: .9rem !important; font-weight: 500; color: var(--text) !important; }}

/* cards */
.cards {{ display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: 14px; margin: 1.4rem 0 .6rem; }}
@media (max-width: 760px) {{ .cards {{ grid-template-columns: 1fr; }} }}
.card {{ padding: 22px 24px; border-radius: 20px; background: var(--soft);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.9), inset 0 0 0 1px rgba(20,30,70,.03); }}
.card .k {{ font-size: .92rem; font-weight: 500; color: var(--text-2); }}
.card .v {{ font-size: 2.5rem; line-height: 1.1; font-weight: 500; letter-spacing: -0.03em; color: var(--text);
  margin: 8px 0 4px; font-variant-numeric: tabular-nums; }}
.card .s {{ font-size: .9rem; color: var(--text-3); }}
.card.good .v {{ color: {GREEN}; }} .card.bad .v {{ color: {RED}; }}
.card.accent {{ background: radial-gradient(120% 90% at 80% 100%, rgba(255,255,255,.28), rgba(255,255,255,0) 60%),
  linear-gradient(180deg, {BLUE_SOFT}, #4A7CEB); box-shadow: 0 18px 30px -18px rgba(47,107,234,.7),
  inset 0 1px 0 rgba(255,255,255,.4); }}
.card.accent .k, .card.accent .s {{ color: rgba(255,255,255,.85); }} .card.accent .v {{ color: #FFFFFF; }}

.callout {{ padding: 32px 34px; border-radius: 24px; margin: .4rem 0 1rem; color: #fff;
  background: radial-gradient(120% 100% at 85% 100%, rgba(255,255,255,.25), rgba(255,255,255,0) 60%),
  linear-gradient(180deg, {BLUE_SOFT}, #3F74E8); box-shadow: 0 24px 40px -24px rgba(47,107,234,.7), inset 0 1px 0 rgba(255,255,255,.4); }}
.callout .eyebrow {{ color: rgba(255,255,255,.85); font-weight: 500; font-size: .95rem; }}
.stApp .callout h2, .stApp .callout h2 * {{ font-family: {SERIF} !important; }}
.stApp .callout h2 {{ color: #fff; margin: .3rem 0 .7rem; font-size: clamp(2rem, 4vw, 2.9rem);
  letter-spacing: -0.01em; font-weight: 500; }}
.callout p {{ margin: 0; font-size: 1.05rem; color: rgba(255,255,255,.9); }}
.callout strong {{ color: #fff; }}
.note {{ padding: 16px 20px; border-radius: 16px; background: linear-gradient(180deg, {SOFT}, {SOFT_2}); color: var(--text-2);
  font-size: .9rem; margin-top: 1.4rem; }}

[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {{ border-radius: 20px; overflow: hidden; background: #FFFFFF;
  border: 1px solid {LINE}; box-shadow: 0 1px 2px rgba(20,30,70,.04), 0 12px 32px -20px rgba(20,30,70,.18); }}
[data-testid="stPlotlyChart"] {{ padding: 10px 8px 4px; }}

@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
"""

# --- plotly template ------------------------------------------------------
pio.templates["cluely_light"] = go.layout.Template(layout=dict(
    font=dict(family=FONT, color=TEXT_2, size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=[BLUE, "#9B5DE5", "#2BB3C0", "#F59E0B", DOT_GREEN, DOT_RED],
    xaxis=dict(automargin=True, gridcolor="#EEF0F5", zerolinecolor=LINE, linecolor=LINE,
               tickfont=dict(color=TEXT_3), title=dict(font=dict(color=TEXT_3, size=12))),
    yaxis=dict(automargin=True, gridcolor="#EEF0F5", zerolinecolor=LINE, linecolor=LINE,
               tickfont=dict(color=TEXT_2), title=dict(font=dict(color=TEXT_3, size=12))),
    legend=dict(font=dict(color=TEXT_2), bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=LINE, font=dict(family=FONT, color=TEXT)),
))
pio.templates.default = "cluely_light"


def cards(items, n=None):
    """items: list of (label, value, sub, variant) -> card row HTML."""
    html = "".join(f'<div class="card {v}"><div class="k">{k}</div><div class="v">{val}</div>'
                   f'<div class="s">{s}</div></div>' for k, val, s, v in items)
    return f'<div class="cards" style="--n:{n or len(items)}">{html}</div>'
