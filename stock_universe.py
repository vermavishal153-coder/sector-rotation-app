"""
stock_universe.py

A curated mapping of ~10 representative large-weight constituent
stocks per NSE sectoral index. This is hand-maintained public
knowledge (not fetched from an index-constituent API, since Angel
One's SmartAPI doesn't expose official index weightings) — treat it
as a reasonable starting universe, not a precise up-to-date weightage
list. Feel free to edit these lists directly, or add stocks manually
via the app's "Add stock" box without touching this file.

Symbols are plain NSE trading symbols without the "-EQ" suffix; both
mock_data.py and angel_one_client.py know how to resolve them.
"""

SECTOR_STOCKS: dict[str, list[str]] = {
    "NIFTY BANK": [
        "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK",
        "INDUSINDBK", "BANKBARODA", "PNB", "AUBANK", "IDFCFIRSTB",
    ],
    "NIFTY IT": [
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM",
        "LTIM", "PERSISTENT", "COFORGE", "MPHASIS", "LTTS",
    ],
    "NIFTY AUTO": [
        "MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT",
        "HEROMOTOCO", "TVSMOTOR", "ASHOKLEY", "BHARATFORG", "BALKRISIND",
    ],
    "NIFTY PHARMA": [
        "SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP",
        "LUPIN", "AUROPHARMA", "TORNTPHARM", "ZYDUSLIFE", "ALKEM",
    ],
    "NIFTY FMCG": [
        "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "TATACONSUM",
        "DABUR", "GODREJCP", "MARICO", "COLPAL", "UBL",
    ],
    "NIFTY METAL": [
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "JINDALSTEL",
        "SAIL", "NMDC", "NATIONALUM", "HINDZINC", "APLAPOLLO",
    ],
    "NIFTY ENERGY": [
        "RELIANCE", "NTPC", "POWERGRID", "ONGC", "COALINDIA",
        "BPCL", "IOC", "TATAPOWER", "ADANIGREEN", "GAIL",
    ],
    "NIFTY REALTY": [
        "DLF", "GODREJPROP", "OBEROIRLTY", "PHOENIXLTD", "PRESTIGE",
        "LODHA", "BRIGADE", "SOBHA", "SUNTECK", "MAHLIFE",
    ],
    "NIFTY PSU BANK": [
        "SBIN", "BANKBARODA", "PNB", "CANBK", "UNIONBANK",
        "INDIANB", "BANKINDIA", "CENTRALBK", "IOB", "UCOBANK",
    ],
    "NIFTY MEDIA": [
        "ZEEL", "SUNTV", "PVRINOX", "NETWORK18", "TV18BRDCST",
        "SAREGAMA", "NAZARA", "HATHWAY", "DISHTV", "TIPSINDLTD",
    ],
}


def get_sector_stocks(sector_name: str) -> list[str]:
    return SECTOR_STOCKS.get(sector_name.strip().upper(), [])
