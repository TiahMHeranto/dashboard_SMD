"""Dashboard marketing — pilotage et scoring client."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

st.set_page_config(
    page_title="Pilotage marketing",
    layout="wide",
)

from lib.data import load_bundle, missing_inputs  # noqa: E402
from lib.models import load_pipelines  # noqa: E402
from views.components import inject_theme  # noqa: E402
from views.demonstration import render_demo  # noqa: E402
from views.pilotage import render_pilotage  # noqa: E402


@st.cache_data(show_spinner="Chargement des données…")
def _cached_bundle():
    return load_bundle()


@st.cache_resource(show_spinner="Chargement des modèles…")
def _cached_pipelines():
    return load_pipelines()


def main() -> None:
    missing = missing_inputs()
    if missing:
        st.error("Données indisponibles. Contactez l'équipe data.")
        st.stop()

    st.session_state["bundle"] = _cached_bundle()
    st.session_state["pipelines"] = _cached_pipelines()
    inject_theme()

    page = st.navigation(
        [
            st.Page(
                render_pilotage,
                title="Pilotage",
                icon=":material/space_dashboard:",
                default=True,
                url_path="pilotage",
            ),
            st.Page(
                render_demo,
                title="Évaluation client",
                icon=":material/query_stats:",
                url_path="scoring",
            ),
        ]
    )
    page.run()


if __name__ == "__main__":
    main()
