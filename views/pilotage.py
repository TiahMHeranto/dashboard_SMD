"""Page principale : KPI, RFM, personas, campagnes, scores IA, plan digital."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from lib.constants import (
    CHANNEL_LABELS,
    FEATURE_LABELS,
    NEXT_BUDGET,
    PALETTE,
    PERIOD_LABEL,
    PERSONA_BLURB,
    RISK_LABELS,
    RISK_ORDER,
    SEGMENT_LABELS,
    SNAPSHOT_LABEL,
)
from lib.data import money, nfmt, pct
from views.components import filter_header, page_header, section_header, style_chart


def kpi_row(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def _clear_pilotage_filters() -> None:
    for key in [
        "filter_segments",
        "filter_risks",
        "filter_locations",
        "filter_categories",
    ]:
        st.session_state[key] = []


def _filter(
    customers,
    scores,
    segments: list[str],
    risks: list[str],
    locations: list[str],
    categories: list[str],
):
    view = customers.copy()
    scored = scores.copy()
    if segments:
        view = view[view["Segment"].isin(segments)]
        scored = scored[scored["Segment"].isin(segments)]
    if risks and "Risk_Tier" in scored.columns:
        scored = scored[scored["Risk_Tier"].isin(risks)]
        view = view[view["Risk_Tier"].isin(risks)]
    if locations and "Location" in view.columns:
        view = view[view["Location"].isin(locations)]
        scored = scored[scored["Customer_ID"].isin(view["Customer_ID"])]
    if categories and "Favorite_Category" in view.columns:
        view = view[view["Favorite_Category"].isin(categories)]
        scored = scored[scored["Customer_ID"].isin(view["Customer_ID"])]
    return view, scored


def render_pilotage() -> None:
    data = st.session_state["bundle"]

    page_header(
        "Pilotage marketing",
        f"Commerce de détail multicanal · {PERIOD_LABEL} · données au {SNAPSHOT_LABEL}",
        "analytics",
    )

    segments = [s for s in SEGMENT_LABELS if s in set(data.customers["Segment"])]
    risk_options = [r for r in RISK_ORDER if r in set(data.customers["Risk_Tier"])]
    locations = sorted(data.customers["Location"].dropna().unique().tolist())
    categories = sorted(data.customers["Favorite_Category"].dropna().unique().tolist())

    with st.sidebar:
        filter_keys = [
            "filter_segments",
            "filter_risks",
            "filter_locations",
            "filter_categories",
        ]
        active_count = sum(bool(st.session_state.get(key, [])) for key in filter_keys)
        filter_header(active_count)
        chosen_segments = st.multiselect(
            "Profils clients",
            segments,
            placeholder="Tous les profils",
            format_func=lambda s: SEGMENT_LABELS.get(s, s),
            key="filter_segments",
        )
        risk = st.multiselect(
            "Niveaux de risque d'attrition",
            risk_options,
            placeholder="Tous les niveaux",
            format_func=lambda r: RISK_LABELS.get(r, r),
            key="filter_risks",
        )
        chosen_locations = st.multiselect(
            "Zones géographiques",
            locations,
            placeholder="Toutes les zones",
            key="filter_locations",
        )
        chosen_categories = st.multiselect(
            "Catégories préférées",
            categories,
            placeholder="Toutes les catégories",
            key="filter_categories",
        )
        active_count = sum(
            bool(value)
            for value in [chosen_segments, risk, chosen_locations, chosen_categories]
        )
        st.button(
            "Effacer les filtres",
            icon=":material/filter_alt_off:",
            width="stretch",
            disabled=active_count == 0,
            on_click=_clear_pilotage_filters,
        )
        st.caption(f"Photographie client mise à jour le {SNAPSHOT_LABEL}")

    view, scored_view = _filter(
        data.customers,
        data.scores,
        chosen_segments,
        risk,
        chosen_locations,
        chosen_categories,
    )
    campaigns = data.campaigns.copy()
    campaigns["Channel"] = campaigns["Channel"].astype(str).replace(CHANNEL_LABELS)
    by_channel = data.by_channel.copy()
    by_channel["Channel"] = by_channel["Channel"].astype(str).replace(CHANNEL_LABELS)
    monthly = data.monthly

    tabs = st.tabs(
        [
            "Vue d'ensemble",
            "Analyse client",
            "Profils clients",
            "Campagnes",
            "Scores prédictifs",
            "Plan d'investissement",
        ]
    )

    with tabs[0]:
        section_header("Indicateurs essentiels", "insights")
        aov = float(view["AOV"].mean()) if len(view) else 0.0
        rec = float(view["Recency"].mean()) if len(view) else 0.0
        kpi_row(
            [
                ("Clients", nfmt(len(view))),
                ("Chiffre d'affaires filtré", money(float(view["Monetary"].sum()) if len(view) else 0)),
                ("Panier moyen", money(aov)),
                ("Récence moyenne", f"{rec:.0f} jours"),
                ("Campagnes", str(len(campaigns))),
            ]
        )
        c1, c2 = st.columns(2)
        if not monthly.empty:
            fig = px.line(
                monthly,
                x="Date",
                y="revenue",
                title="Chiffre d'affaires mensuel",
                color_discrete_sequence=PALETTE,
            )
            fig.update_layout(xaxis_title="Mois", yaxis_title="Chiffre d'affaires ($)")
            c1.plotly_chart(style_chart(fig), width="stretch")
        pie_src = view.groupby("Segment_Label", as_index=False)["Monetary"].sum()
        fig = px.pie(
            pie_src,
            names="Segment_Label",
            values="Monetary",
            title="Répartition du chiffre d'affaires par profil client",
            color_discrete_sequence=PALETTE,
        )
        c2.plotly_chart(style_chart(fig), width="stretch")
        if not by_channel.empty:
            fig = px.bar(
                by_channel,
                x="Channel",
                y="ROI",
                title="Retour sur investissement par canal média",
                color="Channel",
                color_discrete_sequence=PALETTE,
                labels={"Channel": "Canal", "ROI": "Retour sur investissement"},
            )
            fig.update_layout(yaxis_title="Retour sur investissement", showlegend=False)
            st.plotly_chart(style_chart(fig), width="stretch")

    with tabs[1]:
        section_header("Comportement et valeur des clients", "customers")
        c1, c2 = st.columns(2)
        if "Age" in view.columns and "Gender" in view.columns:
            fig = px.histogram(
                view,
                x="Age",
                color="Gender",
                nbins=20,
                title="Répartition par âge et genre",
                color_discrete_sequence=PALETTE,
            )
            c1.plotly_chart(style_chart(fig), width="stretch")
        fig = px.scatter(
            view,
            x="Frequency",
            y="Monetary",
            color="Segment_Label",
            title="Nombre de transactions et valeur client",
            opacity=0.65,
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(
            xaxis_title="Nombre de transactions",
            yaxis_title="Chiffre d'affaires ($)",
        )
        c2.plotly_chart(style_chart(fig), width="stretch")
        show = [
            c
            for c in [
                "Customer_ID",
                "Name",
                "Age",
                "Gender",
                "Location",
                "Segment_Label",
                "Recency",
                "Frequency",
                "Monetary",
                "AOV",
                "Favorite_Category",
                "Risk_Label",
            ]
            if c in view.columns
        ]
        customer_table = view[show].head(200).rename(
            columns={
                "Customer_ID": "Identifiant client",
                "Name": "Nom",
                "Age": "Âge",
                "Gender": "Genre",
                "Location": "Zone géographique",
                "Segment_Label": "Profil client",
                "Recency": "Récence en jours",
                "Frequency": "Nombre de transactions",
                "Monetary": "Chiffre d'affaires ($)",
                "AOV": "Panier moyen ($)",
                "Favorite_Category": "Catégorie préférée",
                "Risk_Label": "Niveau de risque",
            }
        )
        st.dataframe(customer_table, width="stretch", hide_index=True)

    with tabs[2]:
        section_header("Comparaison des profils clients", "customers")
        profiles = data.profiles
        if profiles.empty:
            st.info("Aucun profil de segment disponible.")
        else:
            st.dataframe(
                profiles[
                    [
                        "Segment_Label",
                        "n_clients",
                        "pct_clients",
                        "pct_CA",
                        "age_moyen",
                        "depense_totale_usd",
                        "nb_achats",
                        "recence_j",
                        "panier_moyen_usd",
                    ]
                ].rename(
                    columns={
                        "Segment_Label": "Profil client",
                        "n_clients": "Clients",
                        "pct_clients": "Part des clients (%)",
                        "pct_CA": "Part du chiffre d'affaires (%)",
                        "age_moyen": "Âge moyen",
                        "depense_totale_usd": "Chiffre d'affaires moyen ($)",
                        "nb_achats": "Nombre de transactions",
                        "recence_j": "Récence en jours",
                        "panier_moyen_usd": "Panier moyen ($)",
                    }
                ),
                width="stretch",
                hide_index=True,
            )
            fig = px.bar(
                profiles.sort_values("Share_Revenue", ascending=False),
                x="Segment_Label",
                y=["Share_Customers", "Share_Revenue"],
                barmode="group",
                title="Part des clients et part du chiffre d'affaires",
                color_discrete_sequence=PALETTE[:2],
            )
            fig.update_layout(xaxis_title="Profil client", yaxis_title="Part")
            st.plotly_chart(style_chart(fig), width="stretch")

            mix_cols = [
                c
                for c in ["accessoires", "vetements", "chaussures", "outerwear"]
                if c in profiles.columns
            ]
            if mix_cols:
                long = profiles.melt(
                    id_vars=["Segment_Label"],
                    value_vars=mix_cols,
                    var_name="Catégorie",
                    value_name="Part_%",
                )
                long["Catégorie"] = long["Catégorie"].map(
                    {
                        "accessoires": "Accessoires",
                        "vetements": "Vêtements",
                        "chaussures": "Chaussures",
                        "outerwear": "Vêtements d'extérieur",
                    }
                )
                fig = px.bar(
                    long,
                    x="Segment_Label",
                    y="Part_%",
                    color="Catégorie",
                    title="Répartition moyenne des catégories par profil client",
                    color_discrete_sequence=PALETTE,
                )
                fig.update_layout(
                    xaxis_title="Profil client",
                    yaxis_title="Part du chiffre d'affaires (%)",
                )
                st.plotly_chart(style_chart(fig), width="stretch")

            st.subheader("Fiches des profils clients")
            for _, row in profiles.iterrows():
                key = row["Segment"]
                with st.expander(f"{row['Segment_Label']} — {int(row['n_clients'])} clients"):
                    st.markdown(PERSONA_BLURB.get(key, ""))
                    st.markdown(
                        f"- **Poids** : {row['pct_clients']:.1f} % des clients · "
                        f"{row['pct_CA']:.1f} % du chiffre d'affaires\n"
                        f"- **Valeur** : chiffre d'affaires moyen {money(row['depense_totale_usd'])} · "
                        f"fréquence {row['nb_achats']:.1f} · panier {money(row['panier_moyen_usd'])}\n"
                        f"- **Récence** : {row['recence_j']:.0f} jours · "
                        f"{row['pct_recence_gt_90j']:.1f} % à plus de 90 jours\n"
                        f"- **Canal** : {row['pct_in_store']:.0f} % magasin · "
                        f"{row['pct_femmes']:.0f} % de femmes"
                    )

    with tabs[3]:
        section_header("Performance des campagnes", "campaign")
        if campaigns.empty:
            st.info("Les indicateurs des campagnes sont indisponibles.")
        else:
            tot_budget = float(campaigns["Budget"].sum())
            tot_impr = int(campaigns["Impressions"].sum())
            tot_clicks = int(campaigns["Clicks"].sum())
            tot_conv = int(campaigns["Conversions"].sum())
            kpi_row(
                [
                    ("Budget", money(tot_budget)),
                    ("Impressions", nfmt(tot_impr)),
                    ("Taux de clics", pct(tot_clicks / tot_impr if tot_impr else 0, 2)),
                    ("Coût moyen par acquisition", money(tot_budget / tot_conv if tot_conv else 0, 2)),
                    ("Retour sur investissement global", f"{(campaigns['Attributed_Revenue'].sum() - tot_budget) / tot_budget:.2f}"),
                ]
            )
            c1, c2 = st.columns(2)
            fig = px.bar(
                by_channel,
                x="Channel",
                y="CPA",
                title="Coût par acquisition selon le canal",
                color="Channel",
                color_discrete_sequence=PALETTE,
                labels={"Channel": "Canal", "CPA": "Coût par acquisition ($)"},
            )
            fig.update_layout(showlegend=False, yaxis_title="Coût par acquisition ($)")
            c1.plotly_chart(style_chart(fig), width="stretch")
            fig = px.bar(
                by_channel,
                x="Channel",
                y="CTR",
                title="Taux de clics selon le canal",
                color="Channel",
                color_discrete_sequence=PALETTE,
                labels={"Channel": "Canal", "CTR": "Taux de clics"},
            )
            fig.update_layout(showlegend=False, yaxis_title="Taux de clics")
            c2.plotly_chart(style_chart(fig), width="stretch")
            fig = px.scatter(
                campaigns,
                x="Budget",
                y="Conversions",
                color="Channel",
                size="ROAS",
                hover_data=["Campaign_ID", "CPA", "ROI"],
                title="Budget et conversions par campagne",
                color_discrete_sequence=PALETTE,
                labels={
                    "Budget": "Budget ($)",
                    "Conversions": "Conversions",
                    "Channel": "Canal",
                    "ROAS": "Revenu publicitaire par dollar investi",
                    "Campaign_ID": "Identifiant de campagne",
                    "CPA": "Coût par acquisition ($)",
                    "ROI": "Retour sur investissement",
                },
            )
            st.plotly_chart(style_chart(fig), width="stretch")
            show_cols = [
                c
                for c in [
                    "Campaign_ID",
                    "Channel",
                    "Start_Date",
                    "End_Date",
                    "Budget",
                    "CTR",
                    "CVR",
                    "CPC",
                    "CPA",
                    "ROI",
                    "ROAS",
                    "Attributed_Revenue",
                ]
                if c in campaigns.columns
            ]
            table = campaigns[show_cols].copy()
            if "Start_Date" in table.columns:
                table["Start_Date"] = table["Start_Date"].dt.date.astype(str)
                table["End_Date"] = table["End_Date"].dt.date.astype(str)
            table = table.rename(
                columns={
                    "Campaign_ID": "Identifiant de campagne",
                    "Channel": "Canal",
                    "Start_Date": "Date de début",
                    "End_Date": "Date de fin",
                    "Budget": "Budget ($)",
                    "CTR": "Taux de clics",
                    "CVR": "Taux de conversion",
                    "CPC": "Coût par clic ($)",
                    "CPA": "Coût par acquisition ($)",
                    "ROI": "Retour sur investissement",
                    "ROAS": "Revenu publicitaire par dollar investi",
                    "Attributed_Revenue": "Chiffre d'affaires attribué ($)",
                }
            )
            st.dataframe(table, width="stretch", hide_index=True)
            st.caption(
                "Le retour sur investissement correspond au chiffre d'affaires "
                "attribué, diminué du budget, puis divisé par le budget."
            )

    with tabs[4]:
        section_header("Prévisions de risque et de valeur", "model")
        if scored_view.empty:
            st.info("Aucun client ne correspond aux filtres. Élargissez les niveaux de risque.")
        else:
            kpi_row(
                [
                    ("Probabilité moyenne d'attrition", pct(float(scored_view["Churn_Proba"].mean()))),
                    (
                        "Risque élevé",
                        nfmt(int((scored_view["Risk_Tier"] == "Eleve").sum())),
                    ),
                    (
                        "Réactivation prioritaire",
                        nfmt(int(scored_view["Winback_prioritaire"].sum())),
                    ),
                    ("Valeur client future totale", money(float(scored_view["CLV_Pred"].sum()))),
                ]
            )
            c1, c2 = st.columns(2)
            hist_src = view.copy()
            fig = px.histogram(
                hist_src,
                x="Churn_Proba",
                color="Segment_Label",
                title="Distribution du risque d'attrition",
                color_discrete_sequence=PALETTE,
                labels={
                    "Churn_Proba": "Probabilité d'attrition",
                    "Segment_Label": "Profil client",
                },
            )
            c1.plotly_chart(style_chart(fig), width="stretch")
            fig = px.box(
                hist_src,
                x="Segment_Label",
                y="CLV_Pred",
                color="Segment_Label",
                title="Valeur client future par profil client",
                color_discrete_sequence=PALETTE,
                labels={
                    "Segment_Label": "Profil client",
                    "CLV_Pred": "Valeur client future ($)",
                },
            )
            fig.update_layout(showlegend=False, yaxis_title="Valeur client future ($)")
            c2.plotly_chart(style_chart(fig), width="stretch")

            ic, il = st.columns(2)
            churn_importance = data.importance_churn.head(10).copy()
            churn_importance["feature"] = churn_importance["feature"].map(
                FEATURE_LABELS
            ).fillna(churn_importance["feature"])
            fig = px.bar(
                churn_importance.sort_values("importance"),
                x="importance",
                y="feature",
                orientation="h",
                title="Facteurs du risque d'attrition",
                color_discrete_sequence=[PALETTE[1]],
                labels={"importance": "Importance", "feature": "Facteur"},
            )
            ic.plotly_chart(style_chart(fig), width="stretch")
            value_importance = data.importance_clv.head(10).copy()
            value_importance["feature"] = value_importance["feature"].map(
                FEATURE_LABELS
            ).fillna(value_importance["feature"])
            fig = px.bar(
                value_importance.sort_values("importance"),
                x="importance",
                y="feature",
                orientation="h",
                title="Facteurs de la valeur client future",
                color_discrete_sequence=[PALETTE[2]],
                labels={"importance": "Importance", "feature": "Facteur"},
            )
            il.plotly_chart(style_chart(fig), width="stretch")

            st.subheader("Réactivation prioritaire des clients à forte valeur")
            high = view[view["Winback_prioritaire"] == 1].sort_values("CLV_Pred", ascending=False)
            if high.empty:
                high = view[view["Risk_Tier"] == "Eleve"].sort_values("CLV_Pred", ascending=False)
            show_h = [
                c
                for c in [
                    "Customer_ID",
                    "Name",
                    "Segment_Label",
                    "Recency",
                    "Frequency",
                    "Monetary",
                    "Churn_Proba",
                    "CLV_Pred",
                    "Risk_Label",
                ]
                if c in high.columns
            ]
            priority_table = high[show_h].head(50).rename(
                columns={
                    "Customer_ID": "Identifiant client",
                    "Name": "Nom",
                    "Segment_Label": "Profil client",
                    "Recency": "Récence en jours",
                    "Frequency": "Nombre de transactions",
                    "Monetary": "Chiffre d'affaires ($)",
                    "Churn_Proba": "Probabilité d'attrition",
                    "CLV_Pred": "Valeur client future ($)",
                    "Risk_Label": "Niveau de risque",
                }
            )
            st.dataframe(priority_table, width="stretch", hide_index=True)

    with tabs[5]:
        section_header("Allocation recommandée", "wallet")
        strategy = data.strategy.copy()
        strategy["Primary_Channel"] = strategy["Primary_Channel"].replace(CHANNEL_LABELS)
        mix = data.mix.copy()
        mix["Channel"] = mix["Channel"].astype(str).replace(CHANNEL_LABELS)
        if strategy.empty or mix.empty:
            st.info("Impossible de calculer le plan d'allocation.")
        else:
            st.caption(
                f"Enveloppe {money(NEXT_BUDGET)} répartie selon la valeur future et le risque, "
                "puis pondérée par le retour sur investissement historique des canaux."
            )
            c1, c2 = st.columns(2)
            fig = px.bar(
                strategy.sort_values("Budget_Recommended"),
                x="Budget_Recommended",
                y="Segment_Label",
                orientation="h",
                title=f"Budget recommandé par profil client · enveloppe de {nfmt(NEXT_BUDGET)} $",
                color_discrete_sequence=PALETTE,
            )
            fig.update_layout(xaxis_title="Budget ($)")
            c1.plotly_chart(style_chart(fig), width="stretch")
            fig = px.pie(
                mix,
                names="Channel",
                values="Budget_Recommended",
                title="Répartition média recommandée",
                color_discrete_sequence=PALETTE,
            )
            c2.plotly_chart(style_chart(fig), width="stretch")

            fig = px.scatter(
                strategy,
                x="churn",
                y=strategy["clv"] / strategy["n"],
                size="n",
                color="Segment_Label",
                title="Matrice du risque et de la valeur client",
                color_discrete_sequence=PALETTE,
                hover_data=["Primary_Channel", "high_risk", "winback"],
            )
            fig.update_layout(
                xaxis_title="Probabilité moyenne d'attrition",
                yaxis_title="Valeur future par client ($)",
            )
            st.plotly_chart(style_chart(fig), width="stretch")

            plan_show = strategy[
                [
                    "Segment_Label",
                    "n",
                    "Primary_Channel",
                    "Budget_Recommended",
                    "churn",
                    "clv",
                    "high_risk",
                    "winback",
                    "Message",
                ]
            ].rename(
                columns={
                    "Segment_Label": "Profil client",
                    "n": "Clients",
                    "Primary_Channel": "Canal",
                    "Budget_Recommended": "Budget recommandé ($)",
                    "churn": "Probabilité d'attrition",
                    "clv": "Valeur client future totale ($)",
                    "high_risk": "Risque élevé",
                    "winback": "Réactivation prioritaire",
                }
            )
            st.dataframe(plan_show, width="stretch", hide_index=True)
            with st.expander("Règles du plan"):
                st.markdown(
                    """
- **Clients à très haute valeur** : investir dans l'expérience, pas dans la remise.
- **Risque élevé et valeur future élevée** : réactivation prioritaire par courrier électronique.
- **Courrier électronique** : augmenter les investissements grâce à son meilleur retour.
- **Télévision** : réduire les investissements en raison du coût par acquisition.
- Suivre le coût par acquisition, la récence des clients dormants et le chiffre d'affaires des clients à très haute valeur.
                    """
                )
