"""
chart_utils.py

Builds the quadrant-shaded RRG scatter chart used across the app
(sector view, stock view, dual-benchmark view) so the plotting logic
lives in exactly one place.
"""

from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go

from rrg_engine import QUADRANT_COLORS

PALETTE = ["#8e44ad", "#16a085", "#d35400", "#2c3e50", "#c0392b",
           "#2980b9", "#27ae60", "#f39c12", "#7f8c8d", "#e84393",
           "#1abc9c", "#e67e22", "#34495e", "#9b59b6", "#f368e0"]


def build_rrg_figure(
    rrg_data: dict[str, pd.DataFrame],
    x_title: str = "RS-Ratio  (relative strength trend →)",
    y_title: str = "RS-Momentum  (trend acceleration →)",
    height: int = 600,
) -> go.Figure:
    fig = go.Figure()

    non_empty = [df for df in rrg_data.values() if not df.empty]
    if non_empty:
        all_ratios = pd.concat([df["rs_ratio"] for df in non_empty])
        all_moms = pd.concat([df["rs_momentum"] for df in non_empty])
        pad = 2
        x_min, x_max = all_ratios.min() - pad, all_ratios.max() + pad
        y_min, y_max = all_moms.min() - pad, all_moms.max() + pad
    else:
        x_min, x_max, y_min, y_max = 95, 105, 95, 105
    x_min, x_max = min(x_min, 95), max(x_max, 105)
    y_min, y_max = min(y_min, 95), max(y_max, 105)

    fig.add_shape(type="rect", x0=100, x1=x_max, y0=100, y1=y_max,
                  fillcolor=QUADRANT_COLORS["Leading"], opacity=0.10, line_width=0)
    fig.add_shape(type="rect", x0=100, x1=x_max, y0=y_min, y1=100,
                  fillcolor=QUADRANT_COLORS["Weakening"], opacity=0.10, line_width=0)
    fig.add_shape(type="rect", x0=x_min, x1=100, y0=y_min, y1=100,
                  fillcolor=QUADRANT_COLORS["Lagging"], opacity=0.10, line_width=0)
    fig.add_shape(type="rect", x0=x_min, x1=100, y0=100, y1=y_max,
                  fillcolor=QUADRANT_COLORS["Improving"], opacity=0.10, line_width=0)

    fig.add_hline(y=100, line_dash="dot", line_color="gray")
    fig.add_vline(x=100, line_dash="dot", line_color="gray")

    fig.add_annotation(x=x_max, y=y_max, text="LEADING", showarrow=False,
                        font=dict(color=QUADRANT_COLORS["Leading"], size=13), xanchor="right", yanchor="top")
    fig.add_annotation(x=x_max, y=y_min, text="WEAKENING", showarrow=False,
                        font=dict(color=QUADRANT_COLORS["Weakening"], size=13), xanchor="right", yanchor="bottom")
    fig.add_annotation(x=x_min, y=y_min, text="LAGGING", showarrow=False,
                        font=dict(color=QUADRANT_COLORS["Lagging"], size=13), xanchor="left", yanchor="bottom")
    fig.add_annotation(x=x_min, y=y_max, text="IMPROVING", showarrow=False,
                        font=dict(color=QUADRANT_COLORS["Improving"], size=13), xanchor="left", yanchor="top")

    for i, (name, df) in enumerate(rrg_data.items()):
        if df.empty:
            continue
        color = PALETTE[i % len(PALETTE)]
        n = len(df)
        fig.add_trace(go.Scatter(
            x=df["rs_ratio"], y=df["rs_momentum"],
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=[6] * (n - 1) + [12], color=color,
                        symbol=["circle"] * (n - 1) + ["star"]),
            name=name,
            hovertemplate=f"<b>{name}</b><br>RS-Ratio: %{{x:.2f}}<br>RS-Momentum: %{{y:.2f}}<extra></extra>",
        ))

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        height=height,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(l=40, r=40, t=30, b=40),
    )
    return fig


def build_summary_table(rrg_data: dict[str, pd.DataFrame], label_col: str = "Sector") -> pd.DataFrame:
    rows = []
    for name, df in rrg_data.items():
        if df.empty:
            continue
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        rows.append({
            label_col: name,
            "Quadrant": last["quadrant"],
            "RS-Ratio": round(last["rs_ratio"], 2),
            "RS-Momentum": round(last["rs_momentum"], 2),
            "Δ RS-Ratio": round(last["rs_ratio"] - prev["rs_ratio"], 2),
            "Δ RS-Momentum": round(last["rs_momentum"] - prev["rs_momentum"], 2),
        })
    if not rows:
        return pd.DataFrame(columns=[label_col, "Quadrant", "RS-Ratio", "RS-Momentum", "Δ RS-Ratio", "Δ RS-Momentum"])
    return pd.DataFrame(rows).sort_values("Quadrant")
