"""
╔══════════════════════════════════════════════════════════════╗
║        CRYPTO VOLATILITY VISUALIZER  ·  v3.0                ║
║        Professional Dark Dashboard · Maths for AI           ║
╚══════════════════════════════════════════════════════════════╝

NEW FEATURES:
  • Candlestick / OHLC Chart
  • Bollinger Bands with Rolling Mean
  • Daily Returns Distribution (histogram)
  • Drawdown Analysis Chart
  • Bug fix: hovermode duplicate key error resolved
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Crypto Volatility Visualizer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# DESIGN TOKENS — Single source of truth
# ══════════════════════════════════════════════════════════════
C = {
    "bg":         "#050810",
    "bg2":        "#090d18",
    "surface":    "#0d1221",
    "surface2":   "#111827",
    "surface3":   "#141d30",
    "border":     "#1a2540",
    "border2":    "#243050",
    "text":       "#e8edf5",
    "text2":      "#8899b4",
    "text3":      "#4a5a78",
    "cyan":       "#00d4ff",
    "cyan_dim":   "rgba(0,212,255,0.12)",
    "violet":     "#7c6af7",
    "violet_dim": "rgba(124,106,247,0.12)",
    "green":      "#00e5a0",
    "green_dim":  "rgba(0,229,160,0.10)",
    "red":        "#ff4d6a",
    "red_dim":    "rgba(255,77,106,0.10)",
    "amber":      "#ffb800",
    "amber_dim":  "rgba(255,184,0,0.10)",
    "paper":      "rgba(0,0,0,0)",
    "plot":       "rgba(0,0,0,0)",
    "grid":       "rgba(26,37,64,0.9)",
}

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

    html, body, .stApp {{
        background-color: {C['bg']} !important;
        font-family: 'Outfit', sans-serif;
        color: {C['text']};
    }}
    .stApp {{
        background-image:
            radial-gradient(ellipse 90% 60% at 15% 0%,   rgba(0,212,255,0.05)  0%, transparent 55%),
            radial-gradient(ellipse 70% 50% at 85% 100%, rgba(124,106,247,0.06) 0%, transparent 55%),
            radial-gradient(ellipse 50% 80% at 50% 50%,  rgba(0,229,160,0.02)  0%, transparent 60%);
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {C['surface']} 0%, {C['bg2']} 100%) !important;
        border-right: 1px solid {C['border']} !important;
        padding-top: 0 !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{ padding-top: 0 !important; }}
    section[data-testid="stSidebar"] * {{ color: {C['text']} !important; }}
    section[data-testid="stSidebar"] .stSelectbox > div > div {{
        background: {C['surface2']} !important;
        border: 1px solid {C['border2']} !important;
        border-radius: 8px !important;
    }}
    #MainMenu, footer, header {{ visibility: hidden; height: 0; }}
    .block-container {{ padding-top: 0 !important; max-width: 100% !important; }}

    .sidebar-logo {{
        background: linear-gradient(135deg, {C['surface3']}, {C['surface']});
        border-bottom: 1px solid {C['border']};
        padding: 22px 20px 18px;
        margin-bottom: 8px;
    }}
    .sidebar-logo-mark {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.1rem; font-weight: 600;
        color: {C['cyan']} !important; letter-spacing: 0.05em;
    }}
    .sidebar-logo-sub {{
        font-size: 0.68rem; font-weight: 400;
        color: {C['text3']} !important;
        letter-spacing: 0.15em; text-transform: uppercase; margin-top: 2px;
    }}
    .sb-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.58rem; font-weight: 500;
        letter-spacing: 0.22em; text-transform: uppercase;
        color: {C['text3']} !important; padding: 16px 0 6px;
    }}
    .sb-divider {{ border: none; border-top: 1px solid {C['border']}; margin: 10px 0 0; }}

    .hero-wrap {{ padding: 40px 4px 28px; position: relative; }}
    .hero-chip {{
        display: inline-flex; align-items: center; gap: 6px;
        background: {C['cyan_dim']}; border: 1px solid rgba(0,212,255,0.25);
        border-radius: 20px; padding: 4px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem; letter-spacing: 0.15em; text-transform: uppercase;
        color: {C['cyan']}; margin-bottom: 16px;
    }}
    .hero-chip::before {{ content: '●'; font-size: 0.5rem; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
    .hero-title {{
        font-size: clamp(2.2rem, 4.5vw, 3.6rem); font-weight: 800;
        line-height: 1.08; letter-spacing: -0.03em; color: {C['text']}; margin: 0 0 10px;
    }}
    .hero-title .hl-cyan   {{ color: {C['cyan']}; }}
    .hero-title .hl-violet {{ color: {C['violet']}; }}
    .hero-sub {{ font-size: 0.95rem; color: {C['text2']}; max-width: 560px; }}
    .hero-rule {{ border: none; border-top: 1px solid {C['border']}; margin: 28px 0 24px; }}

    .status-pill {{
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 16px; border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; letter-spacing: 0.08em; margin-bottom: 20px;
    }}
    .status-ok  {{ background:{C['green_dim']}; border:1px solid rgba(0,229,160,0.3); color:{C['green']}; }}
    .status-err {{ background:{C['red_dim']};   border:1px solid rgba(255,77,106,0.3); color:{C['red']}; }}

    .sec-head {{ display: flex; align-items: center; gap: 10px; margin: 32px 0 14px; }}
    .sec-head-line {{ flex:1; height:1px; background:linear-gradient(90deg,{C['border2']},transparent); }}
    .sec-head-text {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
        letter-spacing: 0.2em; text-transform: uppercase; color: {C['text3']}; white-space: nowrap;
    }}
    .sec-head-dot {{ width:6px; height:6px; border-radius:50%; background:{C['cyan']}; flex-shrink:0; }}

    .kpi-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:6px; }}
    .kpi {{
        background:{C['surface2']}; border:1px solid {C['border']};
        border-radius:12px; padding:22px 24px 20px; position:relative; overflow:hidden;
    }}
    .kpi-glow {{ position:absolute; top:0; left:0; right:0; height:1px; }}
    .kpi-glow-cyan   {{ background:linear-gradient(90deg,transparent,{C['cyan']},transparent); }}
    .kpi-glow-violet {{ background:linear-gradient(90deg,transparent,{C['violet']},transparent); }}
    .kpi-glow-green  {{ background:linear-gradient(90deg,transparent,{C['green']},transparent); }}
    .kpi-glow-amber  {{ background:linear-gradient(90deg,transparent,{C['amber']},transparent); }}
    .kpi-label {{
        font-family:'JetBrains Mono',monospace; font-size:0.58rem;
        letter-spacing:0.2em; text-transform:uppercase; color:{C['text3']}; margin-bottom:10px;
    }}
    .kpi-value {{ font-size:1.9rem; font-weight:700; letter-spacing:-0.03em; color:{C['text']}; line-height:1; }}
    .kpi-value.pos   {{ color:{C['green']}; }}
    .kpi-value.neg   {{ color:{C['red']}; }}
    .kpi-value.cyan  {{ color:{C['cyan']}; }}
    .kpi-value.amber {{ color:{C['amber']}; }}
    .kpi-sub {{ font-size:0.72rem; color:{C['text3']}; margin-top:4px; }}

    .chart-wrap {{
        background:{C['surface2']}; border:1px solid {C['border']};
        border-radius:14px; padding:6px 6px 2px; margin-bottom:16px; overflow:hidden;
    }}

    div[data-testid="stTabs"] button {{
        font-family:'JetBrains Mono',monospace !important; font-size:0.7rem !important;
        letter-spacing:0.1em !important; text-transform:uppercase !important;
        color:{C['text2']} !important; border:none !important; padding:10px 20px !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color:{C['cyan']} !important; border-bottom:2px solid {C['cyan']} !important;
        background:{C['cyan_dim']} !important; border-radius:6px 6px 0 0 !important;
    }}
    div[data-testid="stTabsContent"] {{
        border:1px solid {C['border']}; border-radius:0 12px 12px 12px;
        padding:4px; background:{C['surface2']};
    }}

    .stExpander {{
        background:{C['surface2']} !important; border:1px solid {C['border']} !important;
        border-radius:10px !important;
    }}
    .stExpander summary {{
        font-family:'JetBrains Mono',monospace !important; font-size:0.72rem !important;
        letter-spacing:0.1em !important; color:{C['text2']} !important;
    }}
    .stDataFrame {{ border-radius:10px; overflow:hidden; }}
    .footer {{
        text-align:center; padding:40px 0 20px;
        font-family:'JetBrains Mono',monospace; font-size:0.6rem;
        letter-spacing:0.2em; text-transform:uppercase; color:{C['text3']};
    }}
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ══════════════════════════════════════════════════════════════
def load_data(uploaded_file) -> pd.DataFrame:
    df = pd.read_csv(uploaded_file)
    col_map = {}
    for col in df.columns:
        cl = col.strip().lower()
        if cl in ("timestamp", "date", "time", "datetime"):   col_map[col] = "Timestamp"
        elif cl == "open":                                     col_map[col] = "Open"
        elif cl == "high":                                     col_map[col] = "High"
        elif cl == "low":                                      col_map[col] = "Low"
        elif cl in ("close", "price"):                        col_map[col] = "Close"
        elif cl == "volume":                                   col_map[col] = "Volume"
    df.rename(columns=col_map, inplace=True)
    for r in ["Timestamp", "Close"]:
        if r not in df.columns:
            raise ValueError(f"Required column '{r}' not found.")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], infer_datetime_format=True, errors="coerce")
    df.dropna(subset=["Timestamp", "Close"], inplace=True)
    df.sort_values("Timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    for c in ["Open", "High", "Low", "Volume"]:
        if c not in df.columns:
            df[c] = df["Close"]
    df.rename(columns={"Close": "Price"}, inplace=True)
    df.dropna(inplace=True)
    return df


def simulate_data(n_days, amplitude, frequency, drift, pattern) -> pd.DataFrame:
    rng        = np.random.default_rng(42)
    timestamps = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(n_days)]
    t          = np.linspace(0, 2 * np.pi * frequency, n_days)
    base_price = 30_000.0

    sine  = amplitude * 200 * np.sin(t)
    noise = rng.normal(0, amplitude * 80, n_days) if pattern != "Sine Wave Simulation" else np.zeros(n_days)
    drift_comp = np.cumsum(np.full(n_days, drift * 10))
    price = np.maximum(base_price + sine + noise + drift_comp, 1.0)

    spread = amplitude * 30 + 50
    open_  = price + rng.normal(0, spread * 0.3, n_days)
    high   = price + np.abs(rng.normal(0, spread, n_days))
    low    = np.maximum(price - np.abs(rng.normal(0, spread, n_days)), 1.0)
    volume = np.abs(rng.normal(5e6, 1e6, n_days))

    return pd.DataFrame({
        "Timestamp": timestamps,
        "Open": open_, "High": high, "Low": low,
        "Price": price, "Volume": volume,
    })


def enrich(df: pd.DataFrame, bb_window: int = 20, bb_std_mult: float = 2.0) -> pd.DataFrame:
    df = df.copy()
    df["Returns"]    = df["Price"].pct_change() * 100
    df["LogReturns"] = np.log(df["Price"] / df["Price"].shift(1))
    df["RolVol"]     = df["LogReturns"].rolling(20).std() * np.sqrt(252) * 100
    df["BB_Mid"]     = df["Price"].rolling(bb_window).mean()
    bb_s             = df["Price"].rolling(bb_window).std()
    df["BB_Upper"]   = df["BB_Mid"] + bb_std_mult * bb_s
    df["BB_Lower"]   = df["BB_Mid"] - bb_std_mult * bb_s
    roll_max         = df["Price"].cummax()
    df["Drawdown"]   = (df["Price"] - roll_max) / roll_max * 100
    df["CumReturn"]  = (df["Price"] / df["Price"].iloc[0] - 1) * 100
    return df


def calc_metrics(df: pd.DataFrame) -> dict:
    p = df["Price"]
    r = (df["Returns"].dropna()) / 100
    return {
        "volatility":   round(float(p.std()), 2),
        "drift":        round(float(r.mean() * 100), 4),
        "max_price":    round(float(p.max()), 2),
        "min_price":    round(float(p.min()), 2),
        "max_drawdown": round(float(df["Drawdown"].min()), 2),
        "cum_return":   round(float(df["CumReturn"].iloc[-1]), 2),
        "sharpe":       round(float(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0, 2),
    }


# ══════════════════════════════════════════════════════════════
# PLOTLY HELPERS  —  BUG-FREE base layout
# hovermode is a named param, NEVER passed again via **kwargs
# ══════════════════════════════════════════════════════════════
def _base(height: int = 400, hovermode: str = "x unified") -> dict:
    return dict(
        paper_bgcolor = C["paper"],
        plot_bgcolor  = C["plot"],
        font          = dict(family="Outfit, sans-serif", color=C["text2"], size=12),
        xaxis         = dict(gridcolor=C["grid"], zeroline=False, showline=False,
                             tickfont=dict(color=C["text3"], size=11)),
        yaxis         = dict(gridcolor=C["grid"], zeroline=False, showline=False,
                             tickfont=dict(color=C["text3"], size=11)),
        margin        = dict(l=62, r=24, t=50, b=44),
        hovermode     = hovermode,
        hoverlabel    = dict(bgcolor=C["surface"], bordercolor=C["border2"],
                             font=dict(color=C["text"], family="JetBrains Mono, monospace", size=12)),
        legend        = dict(bgcolor="rgba(0,0,0,0)", bordercolor=C["border"],
                             font=dict(color=C["text2"], size=11)),
        height        = height,
    )


def _title(text: str) -> dict:
    return dict(text=text, font=dict(size=14, color=C["text"], family="Outfit, sans-serif"),
                x=0.01, xanchor="left")


# ══════════════════════════════════════════════════════════════
# CHART FUNCTIONS  — each calls _base() only once
# ══════════════════════════════════════════════════════════════

def fig_price(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["Price"], mode="lines", name="Price",
        line=dict(color=C["cyan"], width=2), fill="tozeroy",
        fillcolor="rgba(0,212,255,0.05)",
        hovertemplate="<b>%{x|%b %d %Y}</b><br>Price: $%{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["BB_Mid"], mode="lines", name="20D MA",
        line=dict(color=C["amber"], width=1.2, dash="dot"),
        hovertemplate="MA: $%{y:,.2f}<extra></extra>",
    ))
    lay = _base(420)
    lay["title"]          = _title("Price · 20-Day Moving Average")
    lay["yaxis"]["title"] = "USD"
    fig.update_layout(**lay)
    return fig


def fig_candlestick(df):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["Timestamp"],
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Price"],
        name="OHLC",
        increasing=dict(line=dict(color=C["green"], width=1), fillcolor="rgba(0,229,160,0.45)"),
        decreasing=dict(line=dict(color=C["red"],   width=1), fillcolor="rgba(255,77,106,0.45)"),
    ))
    # Note: hovermode="x" passed explicitly — not repeated
    lay = _base(420, hovermode="x")
    lay["title"]          = _title("Candlestick Chart · OHLC")
    lay["yaxis"]["title"] = "USD"
    lay["xaxis"]["rangeslider"] = dict(visible=False)
    fig.update_layout(**lay)
    return fig


def fig_bollinger(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["BB_Upper"], mode="lines", name="Upper Band",
        line=dict(color="rgba(124,106,247,0.45)", width=1),
        hovertemplate="Upper: $%{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["BB_Lower"], mode="lines", name="Lower Band",
        line=dict(color="rgba(124,106,247,0.45)", width=1),
        fill="tonexty", fillcolor="rgba(124,106,247,0.06)",
        hovertemplate="Lower: $%{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["Price"], mode="lines", name="Price",
        line=dict(color=C["cyan"], width=1.8),
        hovertemplate="Price: $%{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["BB_Mid"], mode="lines", name="20D MA",
        line=dict(color=C["amber"], width=1, dash="dot"),
        hovertemplate="MA: $%{y:,.2f}<extra></extra>",
    ))
    lay = _base(420)
    lay["title"]          = _title("Bollinger Bands  (20-period, 2σ)")
    lay["yaxis"]["title"] = "USD"
    fig.update_layout(**lay)
    return fig


def fig_returns_dist(df):
    rets   = df["Returns"].dropna()
    mean_r = rets.mean()
    std_r  = rets.std()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=rets, nbinsx=50, name="Daily Returns",
        marker=dict(
            color=rets.values,
            colorscale=[[0, C["red"]], [0.5, C["violet"]], [1, C["green"]]],
            line=dict(width=0),
        ),
        hovertemplate="Return: %{x:.2f}%<br>Count: %{y}<extra></extra>",
    ))
    x_r  = np.linspace(rets.min(), rets.max(), 200)
    y_n  = (1 / (std_r * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_r - mean_r) / std_r) ** 2)
    scale = len(rets) * (rets.max() - rets.min()) / 50
    fig.add_trace(go.Scatter(
        x=x_r, y=y_n * scale, mode="lines", name="Normal Fit",
        line=dict(color=C["amber"], width=2),
    ))
    fig.add_vline(x=mean_r, line_color=C["cyan"], line_width=1.5, line_dash="dot",
                  annotation_text=f"μ={mean_r:.3f}%",
                  annotation_font=dict(color=C["cyan"], size=11))
    lay = _base(380)
    lay["title"]          = _title("Daily Returns Distribution")
    lay["xaxis"]["title"] = "Return (%)"
    lay["yaxis"]["title"] = "Frequency"
    lay["bargap"]         = 0.05
    fig.update_layout(**lay)
    return fig


def fig_volume(df):
    direction = df["Price"].diff().fillna(0)
    colors    = [C["green"] if d >= 0 else C["red"] for d in direction]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Timestamp"], y=df["Volume"], name="Volume",
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{x|%b %d}</b><br>Vol: %{y:,.0f}<extra></extra>",
    ))
    # Note: hovermode="x" here — NOT duplicated in _base call
    lay = _base(320, hovermode="x")
    lay["title"]          = _title("Trading Volume  (green = up day, red = down day)")
    lay["yaxis"]["title"] = "Volume"
    lay["bargap"]         = 0.1
    fig.update_layout(**lay)
    return fig


def fig_drawdown(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["Drawdown"], mode="lines", name="Drawdown",
        line=dict(color=C["red"], width=1.5), fill="tozeroy",
        fillcolor="rgba(255,77,106,0.08)",
        hovertemplate="<b>%{x|%b %d %Y}</b><br>Drawdown: %{y:.2f}%<extra></extra>",
    ))
    lay = _base(300)
    lay["title"]           = _title("Drawdown from Peak (%)")
    lay["yaxis"]["title"]  = "%"
    lay["yaxis"]["tickformat"] = ".1f"
    fig.update_layout(**lay)
    return fig


def fig_rolling_vol(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["RolVol"], mode="lines", name="Rolling Vol (20D)",
        line=dict(color=C["violet"], width=2), fill="tozeroy",
        fillcolor="rgba(124,106,247,0.07)",
        hovertemplate="<b>%{x|%b %d %Y}</b><br>Ann.Vol: %{y:.1f}%<extra></extra>",
    ))
    lay = _base(300)
    lay["title"]          = _title("Rolling Annualised Volatility  (20-day window)")
    lay["yaxis"]["title"] = "Ann. Vol (%)"
    fig.update_layout(**lay)
    return fig


def fig_volatility_regions(df):
    window    = max(3, len(df) // 20)
    roll_std  = df["Price"].rolling(window=window).std()
    threshold = roll_std.median()
    volatile  = roll_std > threshold

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=np.where(~volatile, df["Price"], np.nan),
        mode="lines", name="Stable",
        line=dict(color=C["green"], width=2),
        hovertemplate="Stable: $%{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=np.where(volatile, df["Price"], np.nan),
        mode="lines", name="Volatile",
        line=dict(color=C["red"], width=2),
        hovertemplate="Volatile: $%{y:,.2f}<extra></extra>",
    ))
    shapes = []
    for i in range(1, len(df)):
        if volatile.iloc[i]:
            shapes.append(dict(
                type="rect", xref="x", yref="paper",
                x0=df["Timestamp"].iloc[i-1], x1=df["Timestamp"].iloc[i],
                y0=0, y1=1,
                fillcolor="rgba(255,77,106,0.07)", line_width=0, layer="below",
            ))
    lay = _base(380)
    lay["title"]          = _title("Volatility Regime Detection  (green = stable, red = volatile)")
    lay["yaxis"]["title"] = "USD"
    lay["shapes"]         = shapes
    fig.update_layout(**lay)
    return fig


def fig_stable_volatile(df_stable, df_volatile):
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Low Amplitude — Stable", "High Amplitude — Volatile"),
        horizontal_spacing=0.07,
    )
    fig.add_trace(go.Scatter(
        x=df_stable["Timestamp"], y=df_stable["Price"],
        mode="lines", name="Stable", line=dict(color=C["green"], width=1.8),
        hovertemplate="$%{y:,.0f}<extra>Stable</extra>",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df_volatile["Timestamp"], y=df_volatile["Price"],
        mode="lines", name="Volatile", line=dict(color=C["red"], width=1.8),
        hovertemplate="$%{y:,.0f}<extra>Volatile</extra>",
    ), row=1, col=2)
    fig.update_layout(
        paper_bgcolor=C["paper"], plot_bgcolor=C["plot"],
        font=dict(family="Outfit, sans-serif", color=C["text2"], size=12),
        title=dict(text="Side-by-Side: Stable vs Volatile Market",
                   font=dict(size=14, color=C["text"], family="Outfit, sans-serif"),
                   x=0.01, xanchor="left"),
        height=360, margin=dict(l=62, r=24, t=64, b=44),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=C["surface"], bordercolor=C["border2"],
                        font=dict(color=C["text"], family="JetBrains Mono, monospace", size=12)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["text2"], size=11)),
        showlegend=True,
    )
    for ann in fig.layout.annotations:
        ann.font.color = C["text2"]
        ann.font.size  = 12
    fig.update_xaxes(gridcolor=C["grid"], zeroline=False, showline=False)
    fig.update_yaxes(gridcolor=C["grid"], zeroline=False, showline=False)
    return fig


# ══════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════
def sec_head(label: str):
    st.markdown(f"""
    <div class="sec-head">
        <div class="sec-head-dot"></div>
        <div class="sec-head-text">{label}</div>
        <div class="sec-head-line"></div>
    </div>""", unsafe_allow_html=True)


def chart_wrap(fig, key: str):
    st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    inject_css()

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-mark">⬡ CryptoViz</div>
            <div class="sidebar-logo-sub">Volatility Analytics · v3.0</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='sb-label'>Data Source</div>", unsafe_allow_html=True)
        pattern = st.selectbox(
            "mode",
            ["Random Volatility Simulation", "Sine Wave Simulation", "Real Data"],
            label_visibility="collapsed",
        )

        uploaded_file = None
        if pattern == "Real Data":
            st.markdown("<div class='sb-label'>Upload CSV</div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Timestamp · Open · High · Low · Close · Volume",
                type=["csv"], label_visibility="visible",
            )

        st.markdown("<div class='sb-label'>Simulation Parameters</div>", unsafe_allow_html=True)
        amplitude = st.slider("Amplitude",  1,    100, 20,  1)
        frequency = st.slider("Frequency",  0.1,  5.0, 1.0, 0.1)
        drift     = st.slider("Drift",     -5.0,  5.0, 0.5, 0.1)
        n_days    = st.slider("Days",       10,   365, 120, 5)

        st.markdown("<div class='sb-label'>Bollinger Band Settings</div>", unsafe_allow_html=True)
        bb_window = st.slider("BB Window",  5,  50, 20, 1)
        bb_std    = st.slider("BB Std Dev", 1.0, 3.0, 2.0, 0.1)

        st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='padding:12px 0 0;font-family:JetBrains Mono,monospace;"
            f"font-size:0.58rem;letter-spacing:0.15em;color:{C['text3']};'>"
            f"Maths for AI · Streamlit + Plotly<br>All data is simulated / demo</div>",
            unsafe_allow_html=True,
        )

    # ── HERO ─────────────────────────────────────────────────
    st.markdown("""
    <div class='hero-wrap'>
        <div class='hero-chip'>live analytics dashboard</div>
        <div class='hero-title'>
            Crypto <span class='hl-cyan'>Volatility</span><br>
            <span class='hl-violet'>Visualizer</span>
        </div>
        <div class='hero-sub'>
            Quantitative market simulation using sinusoidal wave models,
            Bollinger Bands, regime detection &amp; drawdown analysis.
        </div>
    </div>
    <hr class='hero-rule'>
    """, unsafe_allow_html=True)

    # ── LOAD DATA ─────────────────────────────────────────────
    df = None

    if pattern == "Real Data":
        if uploaded_file is None:
            st.markdown(f"""
            <div style='background:{C["surface2"]};border:1px dashed {C["border2"]};
                        border-radius:14px;padding:40px;text-align:center;'>
                <div style='font-size:2.5rem;margin-bottom:14px;'>📂</div>
                <div style='font-size:1rem;font-weight:600;color:{C["text"]};margin-bottom:8px;'>
                    No CSV uploaded</div>
                <div style='font-size:0.82rem;color:{C["text3"]};line-height:1.6;'>
                    Upload from the sidebar.<br>
                    Required headers:
                    <code style='color:{C["cyan"]};'>Timestamp, Open, High, Low, Close, Volume</code>
                </div>
            </div>""", unsafe_allow_html=True)
            return
        try:
            df = load_data(uploaded_file)
            df = df.tail(n_days).reset_index(drop=True)
            st.markdown(
                f"<div class='status-pill status-ok'>✓  Loaded {len(df):,} rows from CSV</div>",
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.markdown(
                f"<div class='status-pill status-err'>✗  Parse error: {e}</div>",
                unsafe_allow_html=True,
            )
            return
    else:
        df = simulate_data(n_days, amplitude, frequency, drift, pattern)
        st.markdown(
            f"<div class='status-pill status-ok'>✓  Generated {len(df):,} days · {pattern}</div>",
            unsafe_allow_html=True,
        )

    if df is None or df.empty:
        st.warning("No data available.")
        return

    # Enrich + compute metrics
    df  = enrich(df, bb_window=bb_window, bb_std_mult=bb_std)
    m   = calc_metrics(df)

    df_stable   = enrich(simulate_data(n_days, 5,  frequency, drift, "Sine Wave Simulation"))
    df_volatile = enrich(simulate_data(n_days, 80, frequency, drift, "Random Volatility Simulation"))

    # ── KPI CARDS ─────────────────────────────────────────────
    sec_head("KEY PERFORMANCE INDICATORS")
    drift_cls  = "pos" if m["drift"]      >= 0 else "neg"
    drift_sign = "+" if m["drift"]        >= 0 else ""
    cr_cls     = "pos" if m["cum_return"] >= 0 else "neg"
    cr_sign    = "+" if m["cum_return"]   >= 0 else ""
    sh_cls     = "pos" if m["sharpe"]     >= 0 else "neg"

    st.markdown(f"""
    <div class='kpi-grid'>
        <div class='kpi'>
            <div class='kpi-glow kpi-glow-cyan'></div>
            <div class='kpi-label'>Volatility Index σ</div>
            <div class='kpi-value cyan'>{m['volatility']:,.2f}</div>
            <div class='kpi-sub'>Price std. deviation</div>
        </div>
        <div class='kpi'>
            <div class='kpi-glow kpi-glow-violet'></div>
            <div class='kpi-label'>Sharpe Ratio</div>
            <div class='kpi-value {sh_cls}'>{m["sharpe"]:+.2f}</div>
            <div class='kpi-sub'>Annualised risk-adjusted</div>
        </div>
        <div class='kpi'>
            <div class='kpi-glow kpi-glow-green'></div>
            <div class='kpi-label'>Cumulative Return</div>
            <div class='kpi-value {cr_cls}'>{cr_sign}{m['cum_return']:.2f}%</div>
            <div class='kpi-sub'>Period total</div>
        </div>
        <div class='kpi'>
            <div class='kpi-glow kpi-glow-amber'></div>
            <div class='kpi-label'>Max Drawdown</div>
            <div class='kpi-value neg'>{m['max_drawdown']:.2f}%</div>
            <div class='kpi-sub'>From rolling peak</div>
        </div>
    </div>
    <div class='kpi-grid' style='margin-top:14px;'>
        <div class='kpi'>
            <div class='kpi-glow kpi-glow-cyan'></div>
            <div class='kpi-label'>Avg Daily Drift</div>
            <div class='kpi-value {drift_cls}'>{drift_sign}{m['drift']:.4f}%</div>
            <div class='kpi-sub'>Mean daily return</div>
        </div>
        <div class='kpi'>
            <div class='kpi-glow kpi-glow-green'></div>
            <div class='kpi-label'>Maximum Price</div>
            <div class='kpi-value'>${m['max_price']:,.2f}</div>
            <div class='kpi-sub'>Period high</div>
        </div>
        <div class='kpi'>
            <div class='kpi-glow kpi-glow-amber'></div>
            <div class='kpi-label'>Minimum Price</div>
            <div class='kpi-value'>${m['min_price']:,.2f}</div>
            <div class='kpi-sub'>Period low</div>
        </div>
        <div class='kpi'>
            <div class='kpi-glow kpi-glow-violet'></div>
            <div class='kpi-label'>Price Range</div>
            <div class='kpi-value'>${m['max_price'] - m['min_price']:,.2f}</div>
            <div class='kpi-sub'>High − Low spread</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABBED CHARTS ─────────────────────────────────────────
    sec_head("CHARTS & ANALYSIS")

    tab_price, tab_candle, tab_bb, tab_vol, tab_advanced = st.tabs([
        "📈  Price + MA",
        "🕯  Candlestick",
        "📉  Bollinger Bands",
        "📊  Volume & Returns",
        "🔬  Advanced",
    ])

    with tab_price:
        chart_wrap(fig_price(df), "price_chart")
        chart_wrap(fig_volatility_regions(df), "vol_regions")

    with tab_candle:
        chart_wrap(fig_candlestick(df), "candle_chart")

    with tab_bb:
        chart_wrap(fig_bollinger(df), "bb_chart")
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            chart_wrap(fig_rolling_vol(df), "rol_vol")
        with col2:
            chart_wrap(fig_drawdown(df), "drawdown")

    with tab_vol:
        chart_wrap(fig_volume(df), "vol_chart")
        chart_wrap(fig_returns_dist(df), "ret_dist")

    with tab_advanced:
        chart_wrap(fig_stable_volatile(df_stable, df_volatile), "sbs_chart")

    # ── RAW DATA ──────────────────────────────────────────────
    with st.expander("📋  Raw Data Table"):
        display_cols = ["Timestamp","Price","Open","High","Low","Volume",
                        "Returns","RolVol","BB_Upper","BB_Mid","BB_Lower","Drawdown","CumReturn"]
        display_cols = [c for c in display_cols if c in df.columns]
        fmt = {
            "Price":"${:,.2f}", "Open":"${:,.2f}", "High":"${:,.2f}", "Low":"${:,.2f}",
            "Volume":"{:,.0f}", "Returns":"{:+.3f}%", "RolVol":"{:.2f}%",
            "BB_Upper":"${:,.2f}", "BB_Mid":"${:,.2f}", "BB_Lower":"${:,.2f}",
            "Drawdown":"{:.2f}%", "CumReturn":"{:+.2f}%",
        }
        st.dataframe(df[display_cols].style.format(fmt), use_container_width=True, height=320)

    # ── MATH ──────────────────────────────────────────────────
    with st.expander("📐  Simulation Mathematics & Formulas"):
        st.markdown(f"""
**Price Model:**
$$P(t) = P_{{\\text{{base}}}} + A \\cdot \\sin(2\\pi f t) + \\varepsilon(t) + \\sum_{{i=0}}^{{t}} \\delta$$

**Bollinger Bands:**
$$\\text{{Upper}} = \\mu_n + k\\sigma_n, \\quad \\text{{Lower}} = \\mu_n - k\\sigma_n$$
where $\\mu_n$ is $n$-period rolling mean, $k = {bb_std}$

**Rolling Annualised Volatility:**
$$\\sigma_{{\\text{{ann}}}} = \\sigma_{{\\text{{daily}}}} \\times \\sqrt{{252}}$$

**Sharpe Ratio:**
$$\\text{{Sharpe}} = \\frac{{\\bar{{r}}}}{{\\sigma_r}} \\times \\sqrt{{252}}$$

| Symbol | Description | Value |
|--------|-------------|-------|
| $A$ | Amplitude | {amplitude} |
| $f$ | Frequency | {frequency} |
| $\\delta$ | Drift per step | {drift} |
| $n$ | BB window | {bb_window} |
| $k$ | BB std multiplier | {bb_std} |
        """)

    # ── FOOTER ────────────────────────────────────────────────
    st.markdown(
        "<div class='footer'>Crypto Volatility Visualizer &nbsp;·&nbsp; Maths for AI &nbsp;·&nbsp; "
        "Streamlit + Plotly &nbsp;·&nbsp; All data is simulated for educational purposes</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()