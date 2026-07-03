"""
links_directory.py

Curated external links for the app's content tabs. Split into:
  - NEWS_RSS_FEEDS: live-fetchable RSS feeds (market/sector news)
  - PODCASTS: curated podcast links (India market/sector focused)
  - BUFFETT_REPORTS: official Berkshire Hathaway shareholder letters
    and related primary-source material (links only — we never
    reproduce their contents, only link out)
  - TRADER_INTERVIEWS: notable long-form interviews with traders/investors
  - BROKERS: login URLs for the broker dropdown
  - QUICK_LINKS: charting / screening tools
"""

NEWS_RSS_FEEDS = [
    {"name": "Economic Times — Markets", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},
    {"name": "Moneycontrol — Business", "url": "https://www.moneycontrol.com/rss/business.xml"},
    {"name": "Moneycontrol — Markets", "url": "https://www.moneycontrol.com/rss/marketreports.xml"},
    {"name": "Business Standard — Markets", "url": "https://www.business-standard.com/rss/markets-106.rss"},
    {"name": "Livemint — Markets", "url": "https://www.livemint.com/rss/markets"},
]

PODCASTS = [
    {"name": "The Daily Brief — Zerodha", "url": "https://zerodha.com/z-connect/daily-brief", "note": "Daily markets + business news, 10-15 min"},
    {"name": "Paisa Vaisa — Anupam Gupta", "url": "https://open.spotify.com/show/1s4wpjJ1D3AAsPTMYY5Www", "note": "Personal finance + market conversations"},
    {"name": "Capitalmind Podcast", "url": "https://www.capitalmind.in/podcast/", "note": "Deep-dive market and macro analysis"},
    {"name": "Alpha Ideas — Aveek Mitra", "url": "https://open.spotify.com/show/5vh4XCK9jyoWScmxLGx1oO", "note": "Stock-picking and sector rotation focused"},
    {"name": "Business Standard Podcast", "url": "https://www.business-standard.com/podcast", "note": "Daily business + market wrap"},
]

BUFFETT_REPORTS = [
    {"name": "Berkshire Hathaway — Annual Shareholder Letters (all years)", "url": "https://www.berkshirehathaway.com/letters/letters.html"},
    {"name": "Berkshire Hathaway — Latest Annual Report (10-K)", "url": "https://www.berkshirehathaway.com/reports.html"},
    {"name": "Berkshire Hathaway — Annual Meeting Info", "url": "https://www.berkshirehathaway.com/meet.html"},
    {"name": "Berkshire Hathaway — Official Site", "url": "https://www.berkshirehathaway.com/"},
]

TRADER_INTERVIEWS = [
    {"name": "Rakesh Jhunjhunwala — CNBC-TV18 interviews (playlist)", "url": "https://www.youtube.com/results?search_query=rakesh+jhunjhunwala+interview+cnbc"},
    {"name": "Raamdeo Agrawal — Motilal Oswal Wealth Creation talks", "url": "https://www.youtube.com/results?search_query=raamdeo+agrawal+wealth+creation"},
    {"name": "Vijay Kedia — investor interviews", "url": "https://www.youtube.com/results?search_query=vijay+kedia+interview"},
    {"name": "Porinju Veliyath — market interviews", "url": "https://www.youtube.com/results?search_query=porinju+veliyath+interview"},
    {"name": "Samir Arora — Helios Capital interviews", "url": "https://www.youtube.com/results?search_query=samir+arora+helios+interview"},
    {"name": "Nikhil Kamath — WTF podcast (business + markets)", "url": "https://www.youtube.com/@WTFisthisPodcast"},
]

BOOKS_INTERNATIONAL_TRADERS = [
    "Reminiscences of a Stock Operator — Edwin Lefèvre",
    "Market Wizards — Jack Schwager",
    "Trading in the Zone — Mark Douglas",
    "One Up On Wall Street — Peter Lynch",
    "The Intelligent Investor — Benjamin Graham",
    "Common Stocks and Uncommon Profits — Philip Fisher",
    "How to Make Money in Stocks — William O'Neil",
    "How I Made $2,000,000 in the Stock Market — Nicolas Darvas",
]

BOOKS_INDIAN_TRADERS = [
    "Coffee Can Investing — Saurabh Mukherjea",
    "The Unusual Billionaires — Saurabh Mukherjea",
    "Diamonds in the Dust — Saurabh Mukherjea",
    "Value Investing and Behavioral Finance — Parag Parikh",
    "How to Make Money Trading With Charts — Ashwani Gujral",
]

BOOKS_FINANCIAL_ASTROLOGY_INDIA = [
    "Stock Market Astrology (Astrological Theory of Business Cycle) — Indrodeep Banerjee",
    "Astrology For Stock Market — Padam Singh & Krishna Attri",
    "Stock Market Using Vedic Astrology for Beginners — Vinayak Bhatt",
    "Mystics of Sarvato Bhadra Chakra and Astrological Predictions (Norms for Financial Gains in Share Market) — M.K. Agarwal",
]

BROKERS = [
    {"name": "Angel One", "url": "https://trade.angelone.in/Login/UserLogin"},
    {"name": "Zerodha Kite", "url": "https://kite.zerodha.com/"},
    {"name": "Upstox", "url": "https://pro.upstox.com/"},
    {"name": "Groww", "url": "https://groww.in/login"},
]

QUICK_LINKS = [
    {"name": "Chartink — screener & scans", "url": "https://chartink.com/"},
    {"name": "TradingView — charts", "url": "https://www.tradingview.com/"},
    {"name": "NSE India — official site", "url": "https://www.nseindia.com/"},
]
