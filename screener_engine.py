"""
screener_engine.py

Computes how close each stock's current price is to its 52-week high
and to its all-time high (within the fetched history — see caveat
below), and filters for stocks trading within a given percentage band
of either.

CAVEAT on "all-time high": both the mock data and the Angel One live
fetch only pull a bounded lookback window (e.g. 2-5 years), not full
listing-to-date history. So "all-time high" here really means
"highest close within the fetched window" — for most large, mature
stocks with a multi-year lookback this is usually accurate or close
to it, but for older stocks with a genuine ATH set decades ago on a
shorter lookback window, this could understate the real all-time
high. Widening the lookback window (ATH_LOOKBACK_DAYS below) reduces
this risk at the cost of more data to fetch.
"""

from __future__ import annotations
import pandas as pd

ATH_LOOKBACK_DAYS = 1260  # ~5 trading years


def compute_high_proximity(prices: pd.Series, week52_days: int = 252) -> dict:
    """
    prices: a price series (any length; longer = more accurate ATH)
    Returns dict with current price, 52w high, all-time high (within
    series), and % below each.
    """
    prices = prices.dropna()
    if prices.empty:
        return {}
    current = prices.iloc[-1]
    week52_high = prices.tail(week52_days).max()
    all_time_high = prices.max()

    pct_below_52w = (week52_high - current) / week52_high * 100
    pct_below_ath = (all_time_high - current) / all_time_high * 100

    return {
        "current_price": round(current, 2),
        "week52_high": round(week52_high, 2),
        "all_time_high": round(all_time_high, 2),
        "pct_below_52w_high": round(pct_below_52w, 2),
        "pct_below_ath": round(pct_below_ath, 2),
    }


def screen_near_highs(
    price_map: dict[str, pd.Series],
    within_pct: float = 5.0,
    week52_days: int = 252,
) -> pd.DataFrame:
    """
    Returns a DataFrame of stocks currently trading within `within_pct`
    percent of their 52-week high AND/OR all-time high, with columns
    flagging which condition(s) are met.
    """
    rows = []
    for name, prices in price_map.items():
        stats = compute_high_proximity(prices, week52_days=week52_days)
        if not stats:
            continue
        near_52w = stats["pct_below_52w_high"] <= within_pct
        near_ath = stats["pct_below_ath"] <= within_pct
        if near_52w or near_ath:
            rows.append({
                "Stock": name,
                "Price": stats["current_price"],
                "52W High": stats["week52_high"],
                "% Below 52W High": stats["pct_below_52w_high"],
                "All-Time High*": stats["all_time_high"],
                "% Below ATH*": stats["pct_below_ath"],
                "Near 52W High": "✓" if near_52w else "",
                "Near ATH": "✓" if near_ath else "",
            })
    if not rows:
        return pd.DataFrame(columns=[
            "Stock", "Price", "52W High", "% Below 52W High",
            "All-Time High*", "% Below ATH*", "Near 52W High", "Near ATH",
        ])
    return pd.DataFrame(rows).sort_values("% Below 52W High")
