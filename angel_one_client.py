"""
angel_one_client.py

Wraps Angel One's SmartAPI (smartapi-python) to fetch daily historical
closes for the Nifty 50 benchmark and NSE sectoral indices, in a shape
that's a drop-in replacement for mock_data.generate_mock_prices().

READ-ONLY BY DESIGN — SAFE FOR YOUR ACCOUNT:
This client only ever calls generateSession() (login) and
getCandleData() (historical price candles). It never calls
placeOrder, modifyOrder, cancelOrder, or any endpoint that touches
funds, positions, or holdings. There is no code path anywhere in
this app that can place a trade or move money. The only thing at
risk if your credentials leaked is someone else logging into your
actual Angel One account directly — not through this app.

SETUP (one-time):
1. pip install smartapi-python pyotp
2. Create an Angel One trading account + enable API access at
   https://smartapi.angelbroking.com/  -> generates an API key.
3. Enable TOTP-based 2FA on your Angel One account and note the TOTP
   secret (shown as a QR code / base32 string when you set up 2FA).
4. Fill in credentials.py (see credentials.example.py in this folder)
   or set the environment variables listed below. NEVER commit real
   credentials to source control.

Environment variables used:
    ANGEL_API_KEY
    ANGEL_CLIENT_CODE     (your Angel One client / login id)
    ANGEL_PASSWORD        (your Angel One trading PIN/password)
    ANGEL_TOTP_SECRET     (base32 TOTP secret, NOT a one-time code)

Notes on index symbol tokens:
Angel One identifies every tradable/quotable instrument by a numeric
"symboltoken", not by name. Index tokens can change, so rather than
hardcoding them we download Angel One's public instrument master
("scrip master") once per day (cached locally) and look tokens up by
name. This is the approach Angel One itself recommends.

Rate limiting:
Angel One's historical-data endpoint is rate limited (roughly 3
requests/second). Fetching 10+ sectors plus stocks in one go can trip
this, so every historical-data call is spaced out with a short sleep.
"""

from __future__ import annotations
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

try:
    from SmartApi import SmartConnect
    import pyotp
except ImportError:  # pragma: no cover
    SmartConnect = None
    pyotp = None

SCRIP_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
CACHE_PATH = Path(__file__).parent / ".scrip_master_cache.json"
CACHE_TTL_HOURS = 24
REQUEST_DELAY_SECONDS = 0.35  # stay under Angel One's ~3 req/sec historical-data limit

BENCHMARK_NAME = "NIFTY 50"
BENCHMARK_500_NAME = "NIFTY 500"
BENCHMARK_SENSEX_NAME = "SENSEX"

# Angel One's naming for these indices inside the scrip master varies
# slightly (e.g. "Nifty Bank", "NIFTY BANK"), so lookup is case-insensitive
# and matched on exchange == NSE with symbol/name containing the search term.
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


class AngelOneClient:
    def __init__(self, api_key=None, client_code=None, password=None, totp_secret=None):
        if SmartConnect is None:
            raise ImportError(
                "smartapi-python / pyotp not installed. Run: "
                "pip install smartapi-python pyotp"
            )
        self.api_key = api_key or os.environ.get("ANGEL_API_KEY")
        self.client_code = client_code or os.environ.get("ANGEL_CLIENT_CODE")
        self.password = password or os.environ.get("ANGEL_PASSWORD")
        self.totp_secret = totp_secret or os.environ.get("ANGEL_TOTP_SECRET")

        missing = [n for n, v in [
            ("ANGEL_API_KEY", self.api_key),
            ("ANGEL_CLIENT_CODE", self.client_code),
            ("ANGEL_PASSWORD", self.password),
            ("ANGEL_TOTP_SECRET", self.totp_secret),
        ] if not v]
        if missing:
            raise ValueError(f"Missing Angel One credentials: {', '.join(missing)}")

        self.conn = SmartConnect(api_key=self.api_key)
        self._session = None
        self._scrip_master = None

    def login(self):
        totp = pyotp.TOTP(self.totp_secret).now()
        session = self.conn.generateSession(self.client_code, self.password, totp)
        if not session or not session.get("status"):
            raise RuntimeError(f"Angel One login failed: {session}")
        self._session = session
        return session

    # ---------- scrip master / token lookup ----------

    def _load_scrip_master(self) -> list[dict]:
        if self._scrip_master is not None:
            return self._scrip_master

        if CACHE_PATH.exists():
            age_hours = (time.time() - CACHE_PATH.stat().st_mtime) / 3600
            if age_hours < CACHE_TTL_HOURS:
                self._scrip_master = json.loads(CACHE_PATH.read_text())
                return self._scrip_master

        resp = requests.get(SCRIP_MASTER_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        CACHE_PATH.write_text(json.dumps(data))
        self._scrip_master = data
        return data

    def find_token(self, name: str, exchange: str = "NSE") -> str:
        """
        Look up the symboltoken for an index or an equity stock by
        (fuzzy) name. Works for both:
          - index names, e.g. "NIFTY BANK", "NIFTY 500"
          - stock symbols, e.g. "RELIANCE" (auto-tries "RELIANCE-EQ")
        """
        master = self._load_scrip_master()
        name_norm = name.strip().upper()

        # 1) exact symbol match (covers indices and "SYMBOL-EQ" stocks)
        for candidate_symbol in (name_norm, f"{name_norm}-EQ"):
            for row in master:
                if row.get("exch_seg") == exchange and row.get("symbol", "").upper() == candidate_symbol:
                    return row["token"]

        # 2) fuzzy match on name field (good for index names)
        candidates = [
            row for row in master
            if row.get("exch_seg") == exchange
            and name_norm in row.get("name", "").upper().replace("-", " ")
        ]
        # 3) fuzzy match on symbol field, preferring plain equities (-EQ)
        if not candidates:
            candidates = [
                row for row in master
                if row.get("exch_seg") == exchange
                and name_norm in row.get("symbol", "").upper().replace("-", " ")
            ]
        if not candidates:
            raise LookupError(f"Could not find instrument token for '{name}' on {exchange}")

        eq_candidates = [r for r in candidates if r.get("symbol", "").upper().endswith("-EQ")]
        return (eq_candidates or candidates)[0]["token"]

    # ---------- historical data ----------

    def get_daily_history(self, name: str, days: int = 180, exchange: str = "NSE") -> pd.Series:
        """Fetch daily close prices for an index/instrument over the last `days` days."""
        if self._session is None:
            self.login()

        token = self.find_token(name, exchange)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=int(days * 1.6))  # buffer for weekends/holidays

        params = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": "ONE_DAY",
            "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M"),
        }
        time.sleep(REQUEST_DELAY_SECONDS)  # respect Angel One's rate limit
        resp = self.conn.getCandleData(params)
        if not resp or not resp.get("status"):
            raise RuntimeError(f"Angel One historical data fetch failed for {name}: {resp}")

        candles = resp["data"]  # [[timestamp, open, high, low, close, volume], ...]
        idx = [pd.Timestamp(c[0]).normalize() for c in candles]
        closes = [c[4] for c in candles]
        series = pd.Series(closes, index=pd.DatetimeIndex(idx), name=name)
        return series.tail(days)

    def fetch_all(
        self,
        sectors: list[str] | None = None,
        benchmark: str = BENCHMARK_NAME,
        days: int = 180,
    ) -> tuple[pd.Series, dict[str, pd.Series]]:
        """Drop-in replacement for mock_data.generate_mock_prices()."""
        sectors = sectors or DEFAULT_SECTORS
        benchmark_series = self.get_daily_history(benchmark, days=days)
        sector_series = {}
        for name in sectors:
            try:
                sector_series[name] = self.get_daily_history(name, days=days)
            except Exception as e:
                print(f"[warn] skipping {name}: {e}")
        return benchmark_series, sector_series

    def fetch_stocks(self, stocks: list[str], days: int = 180) -> dict[str, pd.Series]:
        """Fetch daily history for a list of individual stock symbols (e.g. 'RELIANCE')."""
        result = {}
        for symbol in stocks:
            try:
                result[symbol] = self.get_daily_history(symbol, days=days, exchange="NSE")
            except Exception as e:
                print(f"[warn] skipping stock {symbol}: {e}")
        return result

    def fetch_benchmark(self, name: str, days: int = 180, exchange: str = "NSE") -> pd.Series:
        """Fetch a single benchmark index series, e.g. NIFTY 50, NIFTY 500, or SENSEX (exchange='BSE')."""
        return self.get_daily_history(name, days=days, exchange=exchange)
