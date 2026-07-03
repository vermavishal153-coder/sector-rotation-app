"""
fo_universe.py

A curated list of NSE F&O (futures & options) eligible stocks, used
as the scanning universe for the Stock Screener and 52-Week/All-Time
High watch tabs.

NSE revises the official F&O eligible-stock list periodically (based
on rolling volume/market-cap criteria), and Angel One's SmartAPI
doesn't expose that list directly — so like stock_universe.py, this
is hand-curated public knowledge covering the large, liquid, commonly
F&O-traded names. It intentionally overlaps heavily with
stock_universe.py's sector lists. Edit this list directly if NSE adds
or removes something you care about.
"""

FO_STOCKS: list[str] = sorted(set([
    # Banking / financials
    "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK",
    "BANKBARODA", "PNB", "AUBANK", "IDFCFIRSTB", "FEDERALBNK", "BANDHANBNK",
    "SBICARD", "HDFCLIFE", "SBILIFE", "ICICIGI", "ICICIPRULI", "CHOLAFIN",
    "BAJFINANCE", "BAJAJFINSV", "PFC", "RECLTD", "MUTHOOTFIN", "LICHSGFIN",
    # IT
    "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTIM", "PERSISTENT",
    "COFORGE", "MPHASIS", "LTTS", "OFSS",
    # Auto
    "MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO",
    "TVSMOTOR", "ASHOKLEY", "BHARATFORG", "BALKRISIND", "MOTHERSON", "BOSCHLTD",
    # Pharma / healthcare
    "SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP", "LUPIN",
    "AUROPHARMA", "TORNTPHARM", "ZYDUSLIFE", "ALKEM", "BIOCON", "MAXHEALTH",
    # FMCG
    "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "TATACONSUM", "DABUR",
    "GODREJCP", "MARICO", "COLPAL", "UBL", "VBL",
    # Metal / mining
    "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "JINDALSTEL", "SAIL",
    "NMDC", "NATIONALUM", "HINDZINC", "APLAPOLLO", "COALINDIA",
    # Energy
    "RELIANCE", "NTPC", "POWERGRID", "ONGC", "BPCL", "IOC", "TATAPOWER",
    "ADANIGREEN", "ADANIPOWER", "GAIL", "IGL", "PETRONET",
    # Realty / infra / cement
    "DLF", "GODREJPROP", "OBEROIRLTY", "PHOENIXLTD", "PRESTIGE", "LODHA",
    "ULTRACEMCO", "SHREECEM", "AMBUJACEM", "ACC", "LT",
    # Media / consumer / other large-caps
    "SUNTV", "PVRINOX", "NAZARA", "ASIANPAINT", "PIDILITIND", "TITAN",
    "TRENT", "DMART", "PAGEIND", "HAVELLS", "VOLTAS", "SIEMENS", "ABB",
    "CUMMINSIND", "POLYCAB", "DIXON", "PERSISTENT",
    # Telecom / adani group / diversified
    "BHARTIARTL", "IDEA", "ADANIENT", "ADANIPORTS", "GRASIM", "UPL",
    "SRF", "PIIND", "NAVINFLUOR", "DEEPAKNTR",
    # PSU
    "BEL", "HAL", "BHEL", "GAIL", "IRCTC", "CONCOR", "SAIL",
]))
