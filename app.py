"""
Sector Rotation & Market Intelligence Dashboard
------------------------------------------------
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from rrg_engine import build_rrg_dataset, QUADRANT_COLORS
from chart_utils import build_rrg_figure, build_summary_table
from screener_engine import screen_near_highs, ATH_LOOKBACK_DAYS
from ema_engine import build_ema_table
from theme import apply_theme
from data_sources.mock_data import (
    generate_mock_prices, generate_mock_benchmark_500, generate_mock_benchmark_sensex,
    generate_mock_stock_prices, DEFAULT_SECTORS, BENCHMARK_500_NAME, BENCHMARK_SENSEX_NAME,
)
from data_sources.stock_universe import get_sector_stocks
from data_sources.fo_universe import FO_STOCKS
from data_sources.links_directory import (
    NEWS_RSS_FEEDS, PODCASTS, BUFFETT_REPORTS, TRADER_INTERVIEWS,
    BOOKS_INTERNATIONAL_TRADERS, BOOKS_INDIAN_TRADERS, BOOKS_FINANCIAL_ASTROLOGY_INDIA,
    BROKERS, QUICK_LINKS,
)

st.set_page_config(page_title="Sector Rotation — India", layout="wide", page_icon="🔄")

# ---------------- Sidebar: theme + navigation ----------------
st.sidebar.title("🔄 Sector Pulse")

theme_choice = st.sidebar.radio("Theme", ["Dark", "Light"], horizontal=True)
st.markdown(apply_theme(theme_choice), unsafe_allow_html=True)

section = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Dashboard",
        "📊 Sector RRG",
        "⚖️ Dual Benchmark",
        "🎯 Stock Screener (F&O)",
        "🚀 52W / ATH Watch",
        "📈 EMA Dashboard",
        "📰 News & Podcasts",
        "📚 Resources",
        "🏦 Broker Login",
    ],
)

with st.sidebar.expander("📖 Buffett letters (quick access)"):
    for r in BUFFETT_REPORTS[:2]:
        st.markdown(f"- [{r['name']}]({r['url']})")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Settings")

data_mode = st.sidebar.radio(
    "Data source", ["Mock data (test)", "Angel One (live)"], index=0,
    help="Start with mock data. Switch to Angel One once your API credentials are set up.",
)
lookback_days = st.sidebar.slider("Lookback window (trading days)", 60, 365, 180, step=10)
rs_window = st.sidebar.slider("RS-Ratio smoothing window", 5, 30, 14)
mom_window = st.sidebar.slider("RS-Momentum smoothing window", 5, 30, 14)
tail_length = st.sidebar.slider("Trail length (points shown per sector)", 3, 20, 8)
selected_sectors = st.sidebar.multiselect("Sectors", DEFAULT_SECTORS, default=DEFAULT_SECTORS)

# ---------------- Cached data loaders ----------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_mock(sectors, days):
    return generate_mock_prices(sectors=sectors, days=days)

@st.cache_data(ttl=3600, show_spinner=False)
def load_mock_500(nifty50_series):
    return generate_mock_benchmark_500(nifty50_series)

@st.cache_data(ttl=3600, show_spinner=False)
def load_mock_sensex(nifty50_series):
    return generate_mock_benchmark_sensex(nifty50_series)

@st.cache_data(ttl=3600, show_spinner=False)
def load_mock_stocks(stocks, days):
    return generate_mock_stock_prices(stocks=stocks, days=days)

@st.cache_resource(show_spinner=False)
def get_angel_client():
    from data_sources.angel_one_client import AngelOneClient
    client = AngelOneClient()
    client.login()
    return client

@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_angel_data(_client, sectors: tuple, days: int):
    return _client.fetch_all(sectors=list(sectors), days=days)

@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_angel_benchmark(_client, name: str, days: int, exchange: str = "NSE"):
    return _client.fetch_benchmark(name, days=days, exchange=exchange)

@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_angel_stocks(_client, stocks: tuple, days: int):
    return _client.fetch_stocks(list(stocks), days=days)

# once-a-day caches for the heavier full-universe scans
@st.cache_data(ttl=86400, show_spinner=False)
def load_mock_fo_universe(days):
    return generate_mock_stock_prices(stocks=FO_STOCKS, days=days)

@st.cache_data(ttl=86400, show_spinner=False)
def load_angel_fo_universe(_client, days):
    return _client.fetch_stocks(FO_STOCKS, days=days)


with st.spinner("Loading price data..."):
    angel_client = None
    if data_mode == "Mock data (test)":
        benchmark, sector_prices = load_mock(tuple(selected_sectors), lookback_days)
        benchmark_500 = load_mock_500(benchmark)
        benchmark_sensex = load_mock_sensex(benchmark)
    else:
        try:
            angel_client = get_angel_client()
            benchmark, sector_prices = _fetch_angel_data(_client=angel_client, sectors=tuple(selected_sectors), days=lookback_days)
            benchmark_500 = _fetch_angel_benchmark(_client=angel_client, name=BENCHMARK_500_NAME, days=lookback_days)
            benchmark_sensex = _fetch_angel_benchmark(_client=angel_client, name=BENCHMARK_SENSEX_NAME, days=lookback_days, exchange="BSE")
        except Exception as e:
            st.error(
                f"Could not fetch Angel One data ({e}). Check your ANGEL_* environment variables. Falling back to mock data."
            )
            benchmark, sector_prices = load_mock(tuple(selected_sectors), lookback_days)
            benchmark_500 = load_mock_500(benchmark)
            benchmark_sensex = load_mock_sensex(benchmark)

rrg_data = build_rrg_dataset(sector_prices, benchmark, rs_window=rs_window, mom_window=mom_window, tail_length=tail_length)

st.title("🔄 Indian Sector Rotation & Market Intelligence")
st.caption(f"Benchmark: **NIFTY 50** · Data source: **{data_mode}** · Lookback: **{lookback_days}** trading days")

# ==================================================================
# DASHBOARD
# ==================================================================
if section == "🏠 Dashboard":
    hot_sectors = [n for n, df in rrg_data.items() if not df.empty and df.iloc[-1]["quadrant"] in ("Improving", "Leading")]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leading sectors", sum(1 for n, df in rrg_data.items() if not df.empty and df.iloc[-1]["quadrant"] == "Leading"))
    c2.metric("Improving sectors", sum(1 for n, df in rrg_data.items() if not df.empty and df.iloc[-1]["quadrant"] == "Improving"))
    c3.metric("Nifty 50 close", round(benchmark.iloc[-1], 2))
    c4.metric("Sensex close", round(benchmark_sensex.iloc[-1], 2))

    st.markdown("#### Sectors currently Improving / Leading")
    st.write(", ".join(hot_sectors) if hot_sectors else "None right now.")

    st.markdown("#### Quick links")
    cols = st.columns(len(QUICK_LINKS))
    for col, link in zip(cols, QUICK_LINKS):
        col.link_button(link["name"], link["url"])

    st.info("Use the sidebar to jump to the Stock Screener, 52W/ATH Watch, EMA Dashboard, News, Buffett Reports, Trader Interviews, or Broker Login.")

# ==================================================================
# SECTOR RRG
# ==================================================================
elif section == "📊 Sector RRG":
    st.plotly_chart(build_rrg_figure(rrg_data, height=650), use_container_width=True)
    st.subheader("Current Sector Positioning")
    summary_df = build_summary_table(rrg_data, label_col="Sector")

    def quadrant_style(val):
        color = QUADRANT_COLORS.get(val, "#ccc")
        return f"background-color: {color}33; font-weight: 600"

    st.dataframe(summary_df.style.map(quadrant_style, subset=["Quadrant"]), use_container_width=True, hide_index=True)
    with st.expander("How to read this"):
        st.markdown("""
- **Leading** (green): outperforming Nifty 50 and still accelerating.
- **Weakening** (yellow): still outperforming, but momentum fading.
- **Lagging** (red): underperforming, momentum still negative.
- **Improving** (blue): underperforming but momentum turning up.

Sectors rotate **clockwise**: Improving → Leading → Weakening → Lagging → Improving.
""")

# ==================================================================
# DUAL BENCHMARK
# ==================================================================
elif section == "⚖️ Dual Benchmark":
    st.caption("Compare selected sectors against both Nifty 50 and Nifty 500.")
    compare_sectors = st.multiselect("Sectors to compare", DEFAULT_SECTORS, default=selected_sectors[:5] or DEFAULT_SECTORS[:5])
    sub_rrg, sub_line = st.tabs(["Side-by-side RRG", "Relative performance line chart"])
    compare_prices = {s: sector_prices[s] for s in compare_sectors if s in sector_prices}

    with sub_rrg:
        rrg_vs_50 = build_rrg_dataset(compare_prices, benchmark, rs_window=rs_window, mom_window=mom_window, tail_length=tail_length)
        rrg_vs_500 = build_rrg_dataset(compare_prices, benchmark_500, rs_window=rs_window, mom_window=mom_window, tail_length=tail_length)
        col1, col2 = st.columns(2)
        col1.markdown("**vs NIFTY 50**")
        col1.plotly_chart(build_rrg_figure(rrg_vs_50, height=550), use_container_width=True, key="rrg50")
        col2.markdown("**vs NIFTY 500**")
        col2.plotly_chart(build_rrg_figure(rrg_vs_500, height=550), use_container_width=True, key="rrg500")

    with sub_line:
        if not compare_prices:
            st.info("Select at least one sector above.")
        else:
            norm_df = pd.DataFrame()
            for name, series in compare_prices.items():
                norm_df[name] = (series / series.iloc[0]) * 100
            norm_df["NIFTY 50"] = (benchmark / benchmark.iloc[0]) * 100
            norm_df[BENCHMARK_500_NAME] = (benchmark_500 / benchmark_500.iloc[0]) * 100
            fig_line = go.Figure()
            for col in norm_df.columns:
                is_bench = col in ("NIFTY 50", BENCHMARK_500_NAME)
                fig_line.add_trace(go.Scatter(x=norm_df.index, y=norm_df[col], mode="lines", name=col,
                                               line=dict(width=3.5 if is_bench else 2, dash="dash" if is_bench else "solid")))
            fig_line.update_layout(height=550, yaxis_title="Normalized performance (start = 100)",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
            st.plotly_chart(fig_line, use_container_width=True)

# ==================================================================
# STOCK SCREENER (F&O universe, quadrant classification)
# ==================================================================
elif section == "🎯 Stock Screener (F&O)":
    st.caption(
        f"Quadrant classification (vs Nifty 50) across {len(FO_STOCKS)} F&O-eligible stocks. "
        "Refreshed once daily — not recomputed on every interaction."
    )
    with st.spinner("Scanning F&O universe (once-daily cache)..."):
        if data_mode == "Mock data (test)":
            fo_prices = load_mock_fo_universe(lookback_days)
        else:
            try:
                fo_prices = load_angel_fo_universe(_client=angel_client, days=lookback_days)
            except Exception as e:
                st.error(f"Live F&O scan failed ({e}). Showing mock data.")
                fo_prices = load_mock_fo_universe(lookback_days)

    fo_rrg = build_rrg_dataset(fo_prices, benchmark, rs_window=rs_window, mom_window=mom_window, tail_length=tail_length)
    fo_summary = build_summary_table(fo_rrg, label_col="Stock")

    quad_filter = st.multiselect("Filter by quadrant", ["Leading", "Improving", "Weakening", "Lagging"], default=["Leading", "Improving"])
    filtered = fo_summary[fo_summary["Quadrant"].isin(quad_filter)] if quad_filter else fo_summary

    def quadrant_style(val):
        color = QUADRANT_COLORS.get(val, "#ccc")
        return f"background-color: {color}33; font-weight: 600"

    st.dataframe(filtered.style.map(quadrant_style, subset=["Quadrant"]), use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(filtered)} of {len(fo_summary)} F&O stocks.")

# ==================================================================
# 52W / ATH WATCH
# ==================================================================
elif section == "🚀 52W / ATH Watch":
    st.caption(
        f"F&O stocks trading within a chosen % of their 52-week high and/or all-time high "
        f"(within a ~{ATH_LOOKBACK_DAYS}-day fetched window — see note below). Refreshed once daily."
    )
    within_pct = st.slider("Within % of high", 1.0, 15.0, 5.0, step=0.5)

    with st.spinner("Scanning for 52W/ATH proximity (once-daily cache)..."):
        if data_mode == "Mock data (test)":
            long_prices = load_mock_fo_universe(ATH_LOOKBACK_DAYS)
        else:
            try:
                long_prices = load_angel_fo_universe(_client=angel_client, days=ATH_LOOKBACK_DAYS)
            except Exception as e:
                st.error(f"Live scan failed ({e}). Showing mock data.")
                long_prices = load_mock_fo_universe(ATH_LOOKBACK_DAYS)

    near_highs_df = screen_near_highs(long_prices, within_pct=within_pct)
    st.dataframe(near_highs_df, use_container_width=True, hide_index=True)
    st.caption(f"{len(near_highs_df)} stocks within {within_pct}% of 52W high or all-time high (within fetched window).")
    st.info(
        "* 'All-time high' reflects the highest close within the fetched lookback window, not necessarily "
        "the stock's true listing-to-date high. Widen the lookback for older stocks if this matters to you."
    )

# ==================================================================
# EMA DASHBOARD
# ==================================================================
elif section == "📈 EMA Dashboard":
    st.caption("5/10/20/50/100/200 period EMAs for Nifty 50, Sensex, Nifty 500, and each sector index.")
    timeframe = st.radio("Timeframe", ["Daily", "Weekly"], horizontal=True)
    weekly = timeframe == "Weekly"

    index_map = {"NIFTY 50": benchmark, "SENSEX": benchmark_sensex, BENCHMARK_500_NAME: benchmark_500, **sector_prices}
    ema_table = build_ema_table(index_map, weekly=weekly)
    st.dataframe(ema_table, use_container_width=True, hide_index=True)
    st.caption("Each cell shows the EMA value and whether the latest close is Above or Below it.")

# ==================================================================
# NEWS & PODCASTS
# ==================================================================
elif section == "📰 News & Podcasts":
    st.subheader("Live market news")
    try:
        import feedparser
        for feed in NEWS_RSS_FEEDS:
            with st.expander(feed["name"]):
                parsed = feedparser.parse(feed["url"])
                if not parsed.entries:
                    st.write("No items fetched — feed may be temporarily unavailable.")
                for entry in parsed.entries[:6]:
                    st.markdown(f"- [{entry.title}]({entry.link})")
    except ImportError:
        st.warning("Install `feedparser` (in requirements.txt) to enable live news headlines: `uv pip install feedparser`")

    st.markdown("---")
    st.subheader("🎧 Podcasts — markets & sector insights")
    for p in PODCASTS:
        st.markdown(f"**[{p['name']}]({p['url']})** — {p['note']}")

# ==================================================================
# RESOURCES (Interviews, Buffett Letters, Books)
# ==================================================================
elif section == "📚 Resources":
    tab_interviews, tab_buffett, tab_books = st.tabs(["🎙️ Trader Interviews", "📖 Buffett Letters", "📚 Books"])

    with tab_interviews:
        st.subheader("Interviews with well-known Indian traders & investors")
        for t in TRADER_INTERVIEWS:
            st.markdown(f"- [{t['name']}]({t['url']})")

    with tab_buffett:
        st.subheader("Warren Buffett — Berkshire Hathaway primary sources")
        st.caption("Official links only — read the source material directly.")
        for r in BUFFETT_REPORTS:
            st.markdown(f"- [{r['name']}]({r['url']})")

    with tab_books:
        st.subheader("Recommended reading — no purchase links, just the list")
        st.caption("Titles only — search for them wherever you buy books. No PDFs linked here (copyright).")

        st.markdown("**International traders & investors**")
        for b in BOOKS_INTERNATIONAL_TRADERS:
            st.markdown(f"- {b}")

        st.markdown("**Indian traders & investors**")
        for b in BOOKS_INDIAN_TRADERS:
            st.markdown(f"- {b}")

        st.markdown("**Financial astrology — Indian authors**")
        for b in BOOKS_FINANCIAL_ASTROLOGY_INDIA:
            st.markdown(f"- {b}")

# ==================================================================
# BROKER LOGIN
# ==================================================================
elif section == "🏦 Broker Login":
    st.subheader("Broker login")
    st.caption("Select your broker and log in directly on their site. This app never handles your broker login credentials for trading.")
    broker_names = [b["name"] for b in BROKERS]
    chosen = st.selectbox("Choose a broker", broker_names)
    broker = next(b for b in BROKERS if b["name"] == chosen)
    st.link_button(f"Log in to {broker['name']}", broker["url"])

st.markdown("---")
if data_mode == "Mock data (test)":
    st.info(
        "You're viewing **synthetic mock data**. Set ANGEL_API_KEY, ANGEL_CLIENT_CODE, ANGEL_PASSWORD and "
        "ANGEL_TOTP_SECRET as environment variables, then switch to 'Angel One (live)' in the sidebar."
    )
