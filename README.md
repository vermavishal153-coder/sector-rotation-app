# Sector Rotation Dashboard — India (Angel One)

An RRG-style (Relative Rotation Graph) sector rotation dashboard for
NSE sectoral indices vs Nifty 50, built with Streamlit + Plotly.

Sectors are placed into 4 quadrants based on relative strength vs
Nifty 50 and how fast that relative strength is changing:

| Quadrant  | Meaning |
|-----------|---------|
| **Leading**   | Outperforming and still accelerating (strongest) |
| **Weakening** | Outperforming but momentum fading |
| **Lagging**   | Underperforming and still decelerating (weakest) |
| **Improving** | Underperforming but momentum turning up |

Sectors typically rotate **clockwise**: Improving → Leading → Weakening → Lagging → Improving.

## 1. Install

```bash
cd sector_rotation_app
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Try it with mock data first (no credentials needed)

```bash
streamlit run app.py
```

This opens the dashboard in your browser at `http://localhost:8501`.
Leave "Data source" set to **Mock data (test)** in the sidebar — this
generates realistic-looking synthetic price series so you can check
the chart, quadrant colors, table, and sector list before touching
any real API.

## 3. Set up Angel One SmartAPI credentials

1. Open a trading account with Angel One if you don't have one, and
   log in to the SmartAPI developer portal: https://smartapi.angelbroking.com/
2. Create an app there to get your **API key**.
3. In your Angel One account, enable **TOTP-based 2FA** (not just
   SMS/email OTP). When you set it up you'll be shown a QR code and a
   base32 secret string — save that secret, it's your `ANGEL_TOTP_SECRET`.
   (`pyotp.TOTP(secret).now()` regenerates the 6-digit code the API needs
   at login time, so you never have to type OTPs manually.)
4. Set these as environment variables (or put them in a `.env` file and
   load it — see note below):

```bash
export ANGEL_API_KEY="your_api_key"
export ANGEL_CLIENT_CODE="your_client_code"     # your Angel One login id
export ANGEL_PASSWORD="your_trading_pin"
export ANGEL_TOTP_SECRET="your_base32_totp_secret"
```

**Never commit these to source control.** If you'd rather use a `.env`
file, install `python-dotenv` and add `from dotenv import load_dotenv;
load_dotenv()` at the top of `app.py`.

## 4. Switch to live data

In the sidebar, change "Data source" to **Angel One (live)**. The app
will:
- log in to SmartAPI using your credentials + a freshly generated TOTP code
- download Angel One's public instrument master once (cached for 24h)
  to resolve index names (e.g. "NIFTY BANK") to symbol tokens
- pull daily EOD candles for Nifty 50 and each selected sector index
  over your chosen lookback window
- recompute the RRG quadrants and chart from real data

If a fetch fails (bad credentials, market holiday quirks, rate limits),
the app shows the error and falls back to mock data so it never crashes.

## 5. Customize

- **Sectors**: edit `DEFAULT_SECTORS` in `data_sources/mock_data.py`
  and `data_sources/angel_one_client.py`, or just deselect/reselect
  in the sidebar multiselect.
- **Smoothing windows**: the RS-Ratio and RS-Momentum rolling windows
  are adjustable live in the sidebar — shorter windows react faster
  but are noisier; longer windows are smoother but lag more.
- **Trail length**: how many recent points are drawn per sector on
  the chart (the "tail" showing its recent path through the quadrants).

## Project structure

```
sector_rotation_app/
├── app.py                          # Streamlit UI
├── rrg_engine.py                   # RS-Ratio / RS-Momentum / quadrant math
├── data_sources/
│   ├── mock_data.py                # synthetic data for testing
│   └── angel_one_client.py         # Angel One SmartAPI integration
├── requirements.txt
└── README.md
```

## A note on the RRG math

The exact JdK RS-Ratio / RS-Momentum formulas used by the original
RRG (as seen on Bloomberg/StockCharts) aren't publicly documented in
full. `rrg_engine.py` uses the standard open-source approximation:
a rolling z-score of relative strength (re-centered on 100) for
RS-Ratio, and a rolling z-score of that indicator's rate of change
for RS-Momentum. It captures the same behavior — quadrant rotation,
relative outperformance, momentum shifts — and is transparent/auditable,
which matters more for a personal tool than exactly replicating a
commercial black box.
