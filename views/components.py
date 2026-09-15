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
    "group": '<path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-.32 0-.63.05-.91.14A5 5 0 0 1 15 11h1Zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3Zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5C15 14.17 10.33 13 8 13Zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5Z"/>',
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
            --brand: #16794a;
            --brand-soft: #edf8f2;
            --accent: #2e9d68;
            --palette-red: #c94040;
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
        [data-testid="stHorizontalBlock"] {gap: 1.15rem;}
        [data-testid="stSidebar"] {background: #fff; border-right: 1px solid var(--line);}
        [data-testid="stSidebar"] .block-container {padding-top: 1.75rem; padding-bottom: 2rem;}
        /* Logo texte "GROUPE 8" injecté dans l'emplacement natif du logo Streamlit
           (stLogoSpacer, vide depuis qu'on n'utilise plus st.logo). Cet emplacement
           est structurellement fixé au-dessus du menu de navigation, donc c'est le
           seul moyen fiable de garder la marque en haut à gauche, au-dessus des liens. */
        [data-testid="stSidebarHeader"] {
            padding-left: .25rem;
        }
        [data-testid="stLogoSpacer"] {
            display: flex;
            align-items: center;
            gap: .55rem;
            height: auto;
            width: auto;
        }
        [data-testid="stLogoSpacer"]::before {
            content: "8";
            display: grid;
            place-items: center;
            width: 34px;
            height: 34px;
            flex: 0 0 auto;
            border-radius: 9px;
            background: linear-gradient(135deg, var(--brand), var(--accent));
            color: #fff;
            font-weight: 800;
            font-size: 1.05rem;
        }
        [data-testid="stLogoSpacer"]::after {
            content: "GROUPE 8\\A SMD · M ENI";
            white-space: pre-line;
            font-size: .74rem;
            line-height: 1.3;
            font-weight: 700;
            color: var(--ink);
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--canvas);
            border-radius: 14px;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: var(--surface);
            border-radius: 14px;
        }
        h1, h2, h3 {color: var(--ink); letter-spacing: -.02em;}
        p, label, [data-testid="stCaptionContainer"] {color: var(--muted);}
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-left: 3px solid var(--brand);
            border-radius: 12px;
            padding: .65rem .85rem;
            min-height: 74px;
            box-shadow: 0 1px 2px rgba(16,24,40,.03);
            transition: box-shadow .15s ease, transform .15s ease;
        }
        [data-testid="stMetric"]:hover {
            box-shadow: 0 4px 14px rgba(16,24,40,.08);
            transform: translateY(-1px);
        }
        [data-testid="stHorizontalBlock"] > div:nth-of-type(2) [data-testid="stMetric"] {border-left-color: var(--accent);}
        [data-testid="stHorizontalBlock"] > div:nth-of-type(3) [data-testid="stMetric"] {border-left-color: #B9770E;}
        [data-testid="stHorizontalBlock"] > div:nth-of-type(4) [data-testid="stMetric"] {border-left-color: #6C3483;}
        [data-testid="stHorizontalBlock"] > div:nth-of-type(5) [data-testid="stMetric"] {border-left-color: var(--palette-red);}
        [data-testid="stMetricLabel"] {font-weight: 600; font-size: .74rem;}
        [data-testid="stMetricLabel"] p {overflow-wrap: break-word;}
        [data-testid="stMetricValue"] {color: var(--ink); font-size: 1.5rem;}
        .kpi-row {margin-bottom: .3rem;}
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
            gap: .3rem;
            border-bottom: 1px solid var(--line);
            flex-wrap: wrap;
        }
        .stTabs [data-baseweb="tab"] {
            height: 2.85rem;
            padding: 0 1rem;
            border-radius: 10px 10px 0 0;
            font-weight: 600;
            color: var(--muted);
            transition: background .15s ease, color .15s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {background: var(--brand-soft); color: var(--ink);}
        .stTabs [aria-selected="true"] {
            background: var(--brand-soft) !important;
            color: var(--brand) !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {background-color: var(--brand);}
        .stTabs [data-baseweb="tab-panel"] {padding-top: 1.35rem;}
        .page-heading {display:flex; align-items:flex-start; gap:.9rem; margin-bottom:1.6rem;}
        .page-heading__icon, .section-heading__icon {
            display:grid; place-items:center; color:var(--brand); background:var(--brand-soft);
            border-radius:12px; flex:0 0 auto;
        }
        .page-heading__icon {width:46px; height:46px;}
        .page-heading--accent .page-heading__icon {
            color: var(--accent);
            background: #e9f7f0;
        }
        .section-heading__icon {width:34px; height:34px; border-radius:9px;}
        .page-heading svg {width:24px; height:24px;}
        .section-heading svg {width:18px; height:18px;}
        .page-heading h1 {font-size:1.9rem; line-height:1.15; margin:0 0 .25rem;}
        .page-heading p {font-size:.93rem; margin:0;}
        .page-heading > div:last-child::after {
            content:"";
            display:block;
            width:54px;
            height:3px;
            margin-top:.65rem;
            border-radius:999px;
            background:linear-gradient(90deg, var(--brand) 0 72%, var(--palette-red) 72%);
        }
        .section-heading {display:flex; align-items:center; gap:.7rem; margin:1.2rem 0 .75rem;}
        .section-heading__icon {position:relative;}
        .section-heading__icon::after {
            content:"";
            position:absolute;
            right:-2px;
            bottom:-2px;
            width:7px;
            height:7px;
            border:2px solid #fff;
            border-radius:50%;
            background:var(--palette-red);
        }
        .section-heading h2 {font-size:1.12rem; margin:0;}
        .filter-heading {display:flex; align-items:center; justify-content:space-between; gap:.65rem; margin-bottom:.1rem;}
        .filter-heading__label {display:flex; align-items:center; gap:.6rem;}
        .filter-heading svg {width:20px; height:20px; color:var(--brand);}
        .filter-heading h2 {font-size:1.15rem; margin:0;}
        .filter-heading__badge {
            display:inline-flex; align-items:center; justify-content:center;
            min-width:1.5rem; height:1.5rem; padding:0 .4rem; border-radius:999px;
            background:var(--brand); color:#fff; font-size:.75rem; font-weight:700;
        }
        .filter-heading__badge--idle {background:var(--line); color:var(--muted);}
        .filter-empty {
            padding:.55rem .7rem; margin:.6rem 0 .9rem; border-radius:9px;
            color:var(--muted); background:var(--canvas); border:1px dashed var(--line);
            font-size:.78rem;
        }
        .filter-chips {display:flex; flex-wrap:wrap; gap:.4rem; margin:.6rem 0 1rem;}
        .filter-chip {
            display:inline-flex; align-items:baseline; gap:.3rem;
            padding:.32rem .6rem; border-radius:999px; font-size:.76rem; line-height:1.1;
            background:var(--brand-soft); border:1px solid #d5ecdf; color:#0f5c38;
            max-width:100%;
        }
        .filter-chip strong {font-weight:700; color:var(--brand);}
        .filter-chip span.chip-val {
            overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:12rem;
        }
        .filter-group-title {
            display:flex; align-items:center; gap:.45rem; margin:.15rem 0 .5rem;
            font-size:.72rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
            color:var(--muted);
        }
        .filter-group-title svg {width:15px; height:15px; color:var(--brand); flex:0 0 auto;}
        [data-testid="stSidebar"] [data-testid="stPills"] [data-testid="stButtonGroup"],
        [data-testid="stSidebar"] [data-testid="stButtonGroup"] {
            gap:.4rem;
        }
        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            font-size:.8rem;
            padding:.4rem .5rem;
        }
        .quick-filters-label {
            font-size:.72rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
            color:var(--muted); margin:0 0 .5rem;
        }
        /* Le sticky doit être posé sur le wrapper Streamlit (stLayoutWrapper), pas sur
           la carte elle-même : sinon son conteneur direct a exactement la même hauteur
           que la carte et il n'y a aucune marge de manœuvre pour "rester collé". */
        [data-testid="stLayoutWrapper"]:has(> .st-key-pilotage_filter_bar) {
            position: sticky;
            top: 3.4rem;
            z-index: 30;
        }
        .st-key-pilotage_filter_bar {
            background: var(--surface);
            border-radius: 14px;
            box-shadow: 0 6px 18px rgba(16,24,40,.1);
            margin-bottom: 1.4rem;
        }
        .st-key-pilotage_filter_bar [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent;
        }
        .team-grid {
            display:grid;
            grid-template-columns:repeat(3, minmax(0, 1fr));
            gap:1rem;
            margin-top:.8rem;
        }
        .member-card {
            position:relative;
            min-height:150px;
            padding:1.15rem;
            overflow:hidden;
            border:1px solid var(--line);
            border-top:4px solid var(--brand);
            border-radius:14px;
            background:#fff;
            box-shadow:0 2px 8px rgba(16,24,40,.05);
        }
        .member-card:nth-child(even) {border-top-color:var(--accent);}
        .member-card__icon {
            display:grid; place-items:center; width:38px; height:38px;
            margin-bottom:.8rem; border-radius:10px; color:var(--brand);
            background:var(--brand-soft);
        }
        .member-card:nth-child(even) .member-card__icon {
            color:var(--accent); background:#e9f7f0;
        }
        .member-card__icon svg {width:20px; height:20px;}
        .member-card h3 {margin:0 0 .5rem; font-size:1rem; line-height:1.35;}
        .member-card p {margin:0; font-size:.82rem;}
        .member-card strong {color:var(--ink); font-family:Consolas, monospace;}
        @media (max-width: 900px) {
            .team-grid {grid-template-columns:repeat(2, minmax(0, 1fr));}
        }
        @media (max-width: 600px) {
            .team-grid {grid-template-columns:1fr;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def evaluation_theme() -> None:
    """Renforce la palette blanc, vert et rouge de la page d'évaluation."""
    st.markdown(
        """
        <style>
        [data-testid="stForm"] {
            border-top: 4px solid transparent;
            border-image: linear-gradient(
                90deg,
                var(--brand) 0 90%,
                var(--palette-red) 90%
            ) 1;
            background:
                linear-gradient(180deg, rgba(46,157,104,.045), transparent 95px),
                #ffffff;
        }
        [data-testid="stMetric"] {
            border-left: 4px solid var(--brand);
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] {
            padding: .7rem .8rem;
            border-left: 3px solid var(--accent);
            border-radius: 0 10px 10px 0;
            background: #f1faf5;
        }
        [data-testid="stSidebar"] [data-testid="stSegmentedControl"] {
            margin-bottom: .4rem;
        }
        [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--canvas);
            border-radius: 12px;
            height: 100%;
        }
        [data-testid="stSlider"] [role="slider"] {
            background-color: var(--brand);
        }
        [data-testid="stFormSubmitButton"] > button {
            color: #ffffff;
            background: var(--brand);
            border-color: var(--brand);
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            background: #105f39;
            border-color: #105f39;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(
    title: str,
    subtitle: str,
    icon: str = "analytics",
    *,
    accent: bool = False,
) -> None:
    css_class = "page-heading page-heading--accent" if accent else "page-heading"
    st.markdown(
        f'<div class="{css_class}">'
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
    badge_class = "filter-heading__badge" if active_count else "filter-heading__badge filter-heading__badge--idle"
    st.markdown(
        '<div class="filter-heading">'
        f'<div class="filter-heading__label">{icon_svg("filter")}<h2>Filtres</h2></div>'
        f'<span class="{badge_class}">{active_count}</span>'
        "</div>",
        unsafe_allow_html=True,
    )


def filter_group_title(title: str, icon: str = "filter") -> None:
    """Petit intitulé de sous-groupe de filtres, utilisé dans la barre latérale."""
    st.markdown(
        f'<div class="filter-group-title">{icon_svg(icon)}<span>{escape(title)}</span></div>',
        unsafe_allow_html=True,
    )


def active_filters_summary(groups: list[tuple[str, list[str]]], *, max_values: int = 2) -> None:
    """Affiche les filtres actifs sous forme de puces lisibles, ou un état vide."""
    active = [(label, values) for label, values in groups if values]
    if not active:
        st.markdown(
            '<div class="filter-empty">Aucun filtre actif — toutes les données sont affichées.</div>',
            unsafe_allow_html=True,
        )
        return
    chips = []
    for label, values in active:
        shown = ", ".join(escape(str(v)) for v in values[:max_values])
        extra = len(values) - max_values
        if extra > 0:
            shown += f" +{extra}"
        chips.append(
            f'<span class="filter-chip"><strong>{escape(label)}</strong>'
            f'<span class="chip-val">{shown}</span></span>'
        )
    st.markdown(f'<div class="filter-chips">{"".join(chips)}</div>', unsafe_allow_html=True)


def _row_sizes(n: int) -> list[int]:
    """Découpe n cartes KPI en lignes équilibrées (max 6 par ligne, éviter 1 orpheline)."""
    if n <= 6:
        return [n]
    rows, remaining = [], n
    while remaining > 6:
        rows.append(6)
        remaining -= 6
    rows.append(remaining if remaining else 0)
    return [r for r in rows if r]


def kpi_row(items: list[tuple[str, str]], *, help_map: dict[str, str] | None = None) -> None:
    """Affiche des cartes st.metric avec une répartition équilibrée par ligne."""
    help_map = help_map or {}
    st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
    offset = 0
    for size in _row_sizes(len(items)):
        cols = st.columns(size, gap="small")
        for col, (label, value) in zip(cols, items[offset : offset + size]):
            col.metric(label, value, help=help_map.get(label))
        offset += size
    st.markdown("</div>", unsafe_allow_html=True)


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
