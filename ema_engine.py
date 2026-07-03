"""
ema_engine.py

Computes exponential moving averages (5/10/20/50/100/200) for a price
series on daily and weekly timeframes, and classifies current price
as above/below each EMA.
"""

from __future__ import annotations
import pandas as pd

EMA_PERIODS = [5, 10, 20, 50, 100, 200]


def compute_emas(prices: pd.Series, periods: list[int] = EMA_PERIODS) -> pd.DataFrame:
    """Returns a DataFrame indexed same as `prices`, one column per EMA period."""
    df = pd.DataFrame(index=prices.index)
    for p in periods:
        df[f"EMA{p}"] = prices.ewm(span=p, adjust=False).mean()
    df["Close"] = prices
    return df


def resample_weekly(prices: pd.Series) -> pd.Series:
    """Resample a daily price series to weekly closes (last close of each week)."""
    return prices.resample("W").last().dropna()


def ema_snapshot(prices: pd.Series, periods: list[int] = EMA_PERIODS, weekly: bool = False) -> dict:
    """
    Returns the latest EMA values plus 'above'/'below' status vs current
    close, for either the daily or weekly timeframe.
    """
    series = resample_weekly(prices) if weekly else prices
    if len(series) < 2:
        return {}
    emas = compute_emas(series, periods)
    last = emas.iloc[-1]
    result = {"Close": round(last["Close"], 2)}
    for p in periods:
        val = last[f"EMA{p}"]
        result[f"EMA{p}"] = round(val, 2)
        result[f"EMA{p}_status"] = "Above" if last["Close"] >= val else "Below"
    return result


def build_ema_table(price_map: dict[str, pd.Series], periods: list[int] = EMA_PERIODS, weekly: bool = False) -> pd.DataFrame:
    """Build a summary table: one row per index/stock, columns = Close + each EMA with above/below."""
    rows = []
    for name, prices in price_map.items():
        snap = ema_snapshot(prices, periods, weekly=weekly)
        if not snap:
            continue
        row = {"Name": name, "Close": snap["Close"]}
        for p in periods:
            row[f"EMA{p}"] = f'{snap[f"EMA{p}"]} ({snap[f"EMA{p}_status"]})'
        rows.append(row)
    cols = ["Name", "Close"] + [f"EMA{p}" for p in periods]
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows)[cols]
