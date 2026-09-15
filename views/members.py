"""Présentation des membres du Groupe 8 SMD."""

from __future__ import annotations

from html import escape

import streamlit as st

from views.components import icon_svg, page_header, section_header


MEMBERS = [
    ("RAZAFINDRATSIMBA Henintsoa Sarobidy", "4550_GID"),
    ("RAKOTONIAINA Mirandy Tianasoa", "4567_GID"),
    ("RAMERISON Fanomezamihaja Voharilafatra", "4571_GID"),
    ("LALAHARIJAONA HERIARINIVO Tiaheranto Mandaniaina", "4614_OCC"),
    ("SAHONDRAHARIVONY Miray Nivolana", "4622_OCC"),
    ("RAKOTOARINELINA Jessarel Fidèle", "4629_OCC"),
]


def _member_cards() -> str:
    cards = []
    for name, identifier in MEMBERS:
        cards.append(
            '<article class="member-card">'
            f'<div class="member-card__icon">{icon_svg("customers")}</div>'
            f"<h3>{escape(name)}</h3>"
            f"<p>Identifiant<br><strong>{escape(identifier)}</strong></p>"
            "</article>"
        )
    return f'<div class="team-grid">{"".join(cards)}</div>'


def render_members() -> None:
    page_header(
        "Membres du groupe",
        "Groupe 8 SMD - M1 ENI",
        "group",
        accent=True,
    )
    section_header("Notre équipe", "group")
    st.markdown(_member_cards(), unsafe_allow_html=True)
