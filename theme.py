"""
theme.py

Two color themes, injected as CSS at runtime so the person can toggle
between them without restarting the app (Streamlit's native theming
via config.toml only supports one fixed theme set at launch, so we
override visually with CSS instead).
"""

DARK_THEME_CSS = """
<style>
.stApp { background-color: #0E1A17; }
section[data-testid="stSidebar"] { background-color: #0A1512; border-right: 1px solid #1E3A32; }
h1, h2, h3, h4, p, span, label, .stMarkdown { color: #E1F5EE !important; }
[data-testid="stMetricValue"] { color: #9FE1CB !important; }
[data-testid="stMetricLabel"] { color: #8FA69D !important; }
.stTabs [data-baseweb="tab"] { color: #8FA69D; }
.stTabs [aria-selected="true"] { color: #9FE1CB !important; border-bottom-color: #1D9E75 !important; }
div[data-testid="stDataFrame"] { border: 1px solid #1E3A32; border-radius: 8px; }
.stButton button, .stDownloadButton button {
    background-color: #132621; color: #9FE1CB; border: 1px solid #1E3A32;
}
.stButton button:hover { border-color: #1D9E75; color: #E1F5EE; }
.stSelectbox div, .stMultiSelect div { color: #E1F5EE !important; }
a { color: #5DCAA5 !important; }
.card-accent { background: #132621; border-left: 3px solid #5DCAA5; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; }
</style>
"""

LIGHT_THEME_CSS = """
<style>
.stApp { background-color: #FFF6ED; }
section[data-testid="stSidebar"] { background-color: #FBEEDF; border-right: 1px solid #E8D9C5; }
h1, h2, h3, h4, p, span, label, .stMarkdown { color: #3A2E22 !important; }
[data-testid="stMetricValue"] { color: #3B6D11 !important; }
[data-testid="stMetricLabel"] { color: #8A7B68 !important; }
.stTabs [data-baseweb="tab"] { color: #8A7B68; }
.stTabs [aria-selected="true"] { color: #993C1D !important; border-bottom-color: #D85A30 !important; }
div[data-testid="stDataFrame"] { border: 1px solid #E8D9C5; border-radius: 8px; }
.stButton button, .stDownloadButton button {
    background-color: #FFFFFF; color: #5A4636; border: 1px solid #E8D9C5;
}
.stButton button:hover { border-color: #D85A30; color: #993C1D; }
a { color: #993C1D !important; }
.card-accent { background: #FFFFFF; border-left: 3px solid #D85A30; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
</style>
"""


def apply_theme(theme_name: str) -> str:
    """Returns the CSS block for the given theme name ('Dark' or 'Light')."""
    return DARK_THEME_CSS if theme_name == "Dark" else LIGHT_THEME_CSS
