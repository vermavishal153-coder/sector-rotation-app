"""
rrg_engine.py

Core math for building a Relative Rotation Graph (RRG)-style sector
rotation model.

Methodology (open, documented approximation of the JdK RS-Ratio /
RS-Momentum indicators popularised by Julius de Kempenaer — the exact
proprietary formula isn't public, this is the widely used open-source
approximation and is more than good enough for spotting rotation):

1. Relative Strength (RS):
       RS = (Sector Price / Benchmark Price) * 100

2. RS-Ratio: a rolling z-score of RS, re-centered on 100.
       RS-Ratio = 100 + zscore(RS, window)
   > 100  => sector outperforming benchmark on a relative basis
   < 100  => sector underperforming benchmark

3. RS-Momentum: a rolling z-score of the rate-of-change of RS-Ratio,
   re-centered on 100.
       RS-Momentum = 100 + zscore(RS-Ratio.diff(), window)
   > 100  => outperformance is accelerating
   < 100  => outperformance is decelerating

4. Quadrant (the classic 4-box RRG map):
       Leading    : RS-Ratio > 100  AND RS-Momentum > 100   (best -> risk of rolling over)
       Weakening  : RS-Ratio > 100  AND RS-Momentum < 100   (was strong, momentum fading)
       Lagging    : RS-Ratio < 100  AND RS-Momentum < 100   (worst -> often a bottoming zone)
       Improving  : RS-Ratio < 100  AND RS-Momentum > 100   (was weak, momentum turning up)

Sectors typically rotate clockwise through these quadrants over weeks/months:
Improving -> Leading -> Weakening -> Lagging -> Improving ...
"""

from __future__ import annotations
import pandas as pd
import numpy as np


QUADRANT_COLORS = {
    "Leading": "#2ecc71",     # green
    "Weakening": "#f1c40f",   # yellow
    "Lagging": "#e74c3c",     # red
    "Improving": "#3498db",   # blue
}

QUADRANT_ORDER = ["Improving", "Leading", "Weakening", "Lagging"]


def _zscore(series: pd.Series, window: int) -> pd.Series:
    mean = series.rolling(window).mean()
    std = series.rolling(window).std(ddof=0)
    return (series - mean) / std


def compute_rs_ratio_momentum(
    sector_prices: pd.Series,
    benchmark_prices: pd.Series,
    rs_window: int = 14,
    mom_window: int = 14,
) -> pd.DataFrame:
    """
    Given two aligned price series (same DatetimeIndex), return a
    DataFrame with columns: rs, rs_ratio, rs_momentum, quadrant
    """
    df = pd.DataFrame({"sector": sector_prices, "benchmark": benchmark_prices}).dropna()
    if df.empty:
        return pd.DataFrame(columns=["rs", "rs_ratio", "rs_momentum", "quadrant"])

    rs = (df["sector"] / df["benchmark"]) * 100
    rs_ratio = 100 + _zscore(rs, rs_window)
    rs_momentum = 100 + _zscore(rs_ratio.diff(), mom_window)

    out = pd.DataFrame({
        "rs": rs,
        "rs_ratio": rs_ratio,
        "rs_momentum": rs_momentum,
    })
    out["quadrant"] = out.apply(
        lambda r: classify_quadrant(r["rs_ratio"], r["rs_momentum"]), axis=1
    )
    return out


def classify_quadrant(rs_ratio: float, rs_momentum: float) -> str:
    if pd.isna(rs_ratio) or pd.isna(rs_momentum):
        return "Unknown"
    if rs_ratio >= 100 and rs_momentum >= 100:
        return "Leading"
    if rs_ratio >= 100 and rs_momentum < 100:
        return "Weakening"
    if rs_ratio < 100 and rs_momentum < 100:
        return "Lagging"
    return "Improving"


def build_rrg_dataset(
    sector_price_map: dict[str, pd.Series],
    benchmark_prices: pd.Series,
    rs_window: int = 14,
    mom_window: int = 14,
    tail_length: int = 8,
) -> dict[str, pd.DataFrame]:
    """
    sector_price_map: {sector_name: price_series}
    Returns: {sector_name: dataframe with rs_ratio/rs_momentum/quadrant,
              trimmed to the last `tail_length` points for plotting a trail}
    """
    result = {}
    for name, prices in sector_price_map.items():
        full = compute_rs_ratio_momentum(prices, benchmark_prices, rs_window, mom_window)
        result[name] = full.dropna().tail(tail_length)
    return result
