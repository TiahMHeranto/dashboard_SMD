"""Composants visuels partagés par les pages du tableau de bord."""

from __future__ import annotations

from html import escape

import plotly.graph_objects as go
import streamlit as st


ICONS = {
    "analytics": '<path d="M4 19V9h4v10H4Zm6 0V5h4v14h-4Zm6 0v-7h4v7h-4Z"/>',
    "campaign": '<path d="M3 11v2h2l4 3V8l-4 3H3Zm11.5 1a3.5 3.5 0 0 0-2.5-3.35v6.7A3.5 3.5 0 0 0 14.5 12Zm-2.5-8v2.05a6 6 0 0 1 0 11.9V20a8 8 0 0 0 0-16Z"/>',
    "customers": '<path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm0 2c-4.42 0-8 2-8 4.5V20h16v-1.5C20 16 16.42 14 12 14Z"/>',
    "filter": '<path d="M4 5h16v2H4V5Zm3 6h10v2H7v-2Zm3 6h4v2h-4v-2Z"/>',
    "insights": '<path d="M3 17h2.5l4.2-5.6 3 3.6 5.3-7H21v2h-2l-6.3 8.4-3-3.6L6.5 19H3v-2Z"/>',
    "model": '<path d="M12 2 4 6v6c0 5.1 3.4 9.7 8 11 4.6-1.3 8-5.9 8-11V6l-8-4Zm0 4a3 3 0 1 1 0 6 3 3 0 0 1 0-6Zm0 14.7a8.7 8.7 0 0 1-5-4.1c.1-1.7 3.3-2.6 5-2.6s4.9.9 5 2.6a8.7 8.7 0 0 1-5 4.1Z"/>',
    "wallet": '<path d="M20 7V5a2 2 0 0 0-2-2H5a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3h15a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Zm-2-2v2H5a1 1 0 0 1 0-2h13Zm2 14H5a1 1 0 0 1-1-1V8.83c.31.11.65.17 1 .17h15v2h-4a3 3 0 0 0 0 6h4v2Zm0-4h-4a1 1 0 0 1 0-2h4v2Z"/>',
}


def icon_svg(name: str) -> str:
    """Retourne une icône SVG décorative et accessible."""
    path = ICONS.get(name, ICONS["analytics"])
    return (
        '<svg aria-hidden="true" viewBox="0 0 24 24" '
        'fill="currentColor" focusable="false">'
        f"{path}</svg>"
    )


def inject_theme() -> None:
    """Applique le thème visuel commun à l'application."""
    st.markdown(
        """
        <style>
        :root {
            --brand: #3157d5;
            --brand-soft: #eef2ff;
            --ink: #172033;
            --muted: #667085;
            --line: #e7eaf0;
            --surface: #ffffff;
            --canvas: #f7f8fb;
        }
        #MainMenu, footer, .stAppDeployButton {display: none;}
        header[data-testid="stHeader"] {background: rgba(247,248,251,.88);}
        .stApp {background: var(--canvas);}
        .block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1500px;}
        [data-testid="stSidebar"] {background: #fff; border-right: 1px solid var(--line);}
        [data-testid="stSidebar"] .block-container {padding-top: 1.75rem;}
        h1, h2, h3 {color: var(--ink); letter-spacing: -.02em;}
        p, label, [data-testid="stCaptionContainer"] {color: var(--muted);}
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 1rem 1.1rem;
            box-shadow: 0 1px 2px rgba(16,24,40,.03);
        }
        [data-testid="stMetricLabel"] {font-weight: 600;}
        [data-testid="stMetricValue"] {color: var(--ink);}
        [data-testid="stPlotlyChart"], [data-testid="stDataFrame"],
        [data-testid="stForm"], details {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: .55rem;
            box-shadow: 0 1px 2px rgba(16,24,40,.03);
        }
        div[data-baseweb="select"] > div, [data-testid="stNumberInput"] input {
            border-color: var(--line);
            border-radius: 10px;
        }
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 10px;
            font-weight: 650;
        }
        button[kind="primary"] {background: var(--brand); border-color: var(--brand);}
        .stTabs [data-baseweb="tab-list"] {
            gap: .35rem;
            border-bottom: 1px solid var(--line);
        }
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            padding: 0 .9rem;
            border-radius: 9px 9px 0 0;
            font-weight: 600;
        }
        .page-heading {display:flex; align-items:flex-start; gap:.9rem; margin-bottom:1.6rem;}
        .page-heading__icon, .section-heading__icon {
            display:grid; place-items:center; color:var(--brand); background:var(--brand-soft);
            border-radius:12px; flex:0 0 auto;
        }
        .page-heading__icon {width:46px; height:46px;}
        .section-heading__icon {width:34px; height:34px; border-radius:9px;}
        .page-heading svg {width:24px; height:24px;}
        .section-heading svg {width:18px; height:18px;}
        .page-heading h1 {font-size:1.9rem; line-height:1.15; margin:0 0 .25rem;}
        .page-heading p {font-size:.93rem; margin:0;}
        .section-heading {display:flex; align-items:center; gap:.7rem; margin:1.2rem 0 .75rem;}
        .section-heading h2 {font-size:1.12rem; margin:0;}
        .filter-heading {display:flex; align-items:center; gap:.65rem; margin-bottom:.35rem;}
        .filter-heading svg {width:20px; height:20px; color:var(--brand);}
        .filter-heading h2 {font-size:1.15rem; margin:0;}
        .filter-summary {
            padding:.7rem .8rem; margin:.8rem 0 1rem; border-radius:10px;
            color:#344054; background:var(--brand-soft); font-size:.82rem; font-weight:600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, icon: str = "analytics") -> None:
    st.markdown(
        '<div class="page-heading">'
        f'<div class="page-heading__icon">{icon_svg(icon)}</div>'
        f"<div><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>"
        "</div>",
        unsafe_allow_html=True,
    )


def section_header(title: str, icon: str = "insights") -> None:
    st.markdown(
        '<div class="section-heading">'
        f'<div class="section-heading__icon">{icon_svg(icon)}</div>'
        f"<h2>{escape(title)}</h2></div>",
        unsafe_allow_html=True,
    )


def filter_header(active_count: int) -> None:
    st.markdown(
        f'<div class="filter-heading">{icon_svg("filter")}<h2>Filtres</h2></div>'
        f'<div class="filter-summary">{active_count} critère'
        f'{"s" if active_count != 1 else ""} actif'
        f'{"s" if active_count != 1 else ""}</div>',
        unsafe_allow_html=True,
    )


def style_chart(fig: go.Figure, *, height: int | None = None) -> go.Figure:
    """Uniformise la présentation des graphiques Plotly."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(t=64, b=40, l=45, r=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#475467", size=12),
        title_font=dict(color="#172033", size=16),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#172033", font_color="#ffffff"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e7eaf0")
    fig.update_yaxes(gridcolor="#eef0f4", zeroline=False)
    return fig
