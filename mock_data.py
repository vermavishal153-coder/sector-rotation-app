"""
mock_data.py

Generates synthetic-but-plausible daily close price series for the
Nifty 50 benchmark and a set of NSE sectoral indices, so the RRG app
can be fully built and tested before Angel One API credentials are
wired in. Swap this module for angel_one_client.py once you're ready
to go live (the app.py toggle handles this).
"""

from __future__ import annotations
import numpy as np
import pandas as pd

DEFAULT_SECTORS = [
    "NIFTY BANK",
    "NIFTY IT",
    "NIFTY AUTO",
    "NIFTY PHARMA",
    "NIFTY FMCG",
    "NIFTY METAL",
    "NIFTY ENERGY",
    "NIFTY REALTY",
    "NIFTY PSU BANK",
    "NIFTY MEDIA",
]

BENCHMARK_NAME = "NIFTY 50"
BENCHMARK_500_NAME = "NIFTY 500"
BENCHMARK_SENSEX_NAME = "SENSEX"


def _random_walk(days: int, start_price: float, drift: float, vol: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    rets = rng.normal(loc=drift, scale=vol, size=days)
    # add a slow-moving cyclical component so sectors visibly rotate
    cycle = np.sin(np.linspace(0, rng.uniform(2, 5) * np.pi, days)) * vol * 3
    rets = rets + cycle / days
    price = start_price * np.cumprod(1 + rets)
    return price


def generate_mock_prices(
    sectors: list[str] | None = None,
    days: int = 180,
    end_date: str | None = None,
    seed: int = 42,
) -> tuple[pd.Series, dict[str, pd.Series]]:
    """
    Returns (benchmark_series, {sector_name: series}), both indexed by
    business-day DatetimeIndex, mimicking daily EOD closes.
    """
    sectors = sectors or DEFAULT_SECTORS
    end = pd.Timestamp(end_date) if end_date else pd.Timestamp.today().normalize()
    dates = pd.bdate_range(end=end, periods=days)

    bench_prices = _random_walk(days, start_price=22000, drift=0.0004, vol=0.008, seed=seed)
    benchmark = pd.Series(bench_prices, index=dates, name=BENCHMARK_NAME)

    sector_series = {}
    for i, name in enumerate(sectors):
        # each sector gets its own drift/vol/seed so they visibly occupy
        # different quadrants and rotate over time
        drift = 0.0004 + (np.sin(i) * 0.0006)
        vol = 0.009 + (i % 4) * 0.002
        prices = _random_walk(days, start_price=15000 + i * 1000, drift=drift, vol=vol, seed=seed + i + 1)
        sector_series[name] = pd.Series(prices, index=dates, name=name)

    return benchmark, sector_series


def generate_mock_benchmark_500(
    nifty50_series: pd.Series,
    seed: int = 99,
) -> pd.Series:
    """
    Nifty 500 is a much broader basket than Nifty 50 but highly
    correlated with it (Nifty 50 is its largest-weight subset). Model
    it as Nifty 50 scaled + a slow independent random-walk "spread"
    factor, so the two benchmarks move together but aren't identical
    — which is what makes comparing sectors against both meaningful.
    """
    days = len(nifty50_series)
    rng = np.random.default_rng(seed)
    spread_rets = rng.normal(loc=0.00005, scale=0.0025, size=days)
    spread_factor = np.cumprod(1 + spread_rets)
    price = (nifty50_series.values / nifty50_series.values[0]) * spread_factor * 23500
    return pd.Series(price, index=nifty50_series.index, name=BENCHMARK_500_NAME)


def generate_mock_benchmark_sensex(
    nifty50_series: pd.Series,
    seed: int = 77,
) -> pd.Series:
    """Sensex (BSE) tracks Nifty 50 (NSE) very closely in practice; model similarly."""
    days = len(nifty50_series)
    rng = np.random.default_rng(seed)
    spread_rets = rng.normal(loc=0.00003, scale=0.0015, size=days)
    spread_factor = np.cumprod(1 + spread_rets)
    price = (nifty50_series.values / nifty50_series.values[0]) * spread_factor * 72000
    return pd.Series(price, index=nifty50_series.index, name=BENCHMARK_SENSEX_NAME)


def generate_mock_stock_prices(
    stocks: list[str],
    days: int = 180,
    end_date: str | None = None,
    seed: int = 500,
) -> dict[str, pd.Series]:
    """Same synthetic engine as sectors, but for individual stock symbols."""
    end = pd.Timestamp(end_date) if end_date else pd.Timestamp.today().normalize()
    dates = pd.bdate_range(end=end, periods=days)

    result = {}
    for i, symbol in enumerate(stocks):
        drift = 0.0003 + (np.sin(i * 1.7) * 0.0008)
        vol = 0.011 + (i % 5) * 0.0015
        prices = _random_walk(
            days, start_price=800 + (i * 137) % 2500, drift=drift, vol=vol, seed=seed + i + 1
        )
        result[symbol] = pd.Series(prices, index=dates, name=symbol)
    return result
