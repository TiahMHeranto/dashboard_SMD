"""Page principale : KPI, RFM, personas, campagnes, scores IA, plan digital."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from lib.constants import (
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


def kpi_row(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def _filter(customers, scores, segment: str, risks: list[str]):
    view = customers.copy()
    scored = scores.copy()
    if segment != "Tous":
        view = view[view["Segment"] == segment]
        scored = scored[scored["Segment"] == segment]
    if risks and "Risk_Tier" in scored.columns:
        scored = scored[scored["Risk_Tier"].isin(risks)]
        view = view[view["Risk_Tier"].isin(risks)]
    return view, scored


def render_pilotage() -> None:
    data = st.session_state["bundle"]

    st.title("Pilotage marketing")
    st.caption(f"Retail multi-canal · {PERIOD_LABEL} · données au {SNAPSHOT_LABEL}")

    segments = ["Tous"] + [s for s in SEGMENT_LABELS if s in set(data.customers["Segment"])]
    risk_options = [r for r in RISK_ORDER if r in set(data.customers["Risk_Tier"])]

    with st.sidebar:
        st.header("Filtres")
        chosen_label = st.selectbox(
            "Persona",
            segments,
            format_func=lambda s: "Tous" if s == "Tous" else SEGMENT_LABELS.get(s, s),
        )
        risk = st.multiselect(
            "Palier de risque churn",
            risk_options,
            default=risk_options,
            format_func=lambda r: RISK_LABELS.get(r, r),
        )
        st.markdown("---")
        st.caption(f"Dernière photo client : {SNAPSHOT_LABEL}")

    view, scored_view = _filter(data.customers, data.scores, chosen_label, risk)
    campaigns = data.campaigns
    by_channel = data.by_channel
    monthly = data.monthly

    tabs = st.tabs(
        [
            "Vue d'ensemble",
            "Clients & RFM",
            "Personas",
            "Campagnes",
            "Scores",
            "Plan média",
        ]
    )

    with tabs[0]:
        aov = float(view["AOV"].mean()) if len(view) else 0.0
        rec = float(view["Recency"].mean()) if len(view) else 0.0
        kpi_row(
            [
                ("Clients", nfmt(len(view))),
                ("CA (filtre)", money(float(view["Monetary"].sum()) if len(view) else 0)),
                ("Panier moyen", money(aov)),
                ("Récence moy.", f"{rec:.0f} j"),
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
            fig.update_layout(xaxis_title="Mois", yaxis_title="CA ($)")
            c1.plotly_chart(fig, width="stretch")
        pie_src = view.groupby("Segment_Label", as_index=False)["Monetary"].sum()
        fig = px.pie(
            pie_src,
            names="Segment_Label",
            values="Monetary",
            title="Poids CA par persona",
            color_discrete_sequence=PALETTE,
        )
        c2.plotly_chart(fig, width="stretch")
        if not by_channel.empty:
            fig = px.bar(
                by_channel,
                x="Channel",
                y="ROI",
                title="ROI par canal média",
                color="Channel",
                color_discrete_sequence=PALETTE,
            )
            fig.update_layout(yaxis_title="ROI", showlegend=False)
            st.plotly_chart(fig, width="stretch")

    with tabs[1]:
        c1, c2 = st.columns(2)
        if "Age" in view.columns and "Gender" in view.columns:
            fig = px.histogram(
                view,
                x="Age",
                color="Gender",
                nbins=20,
                title="Âge × genre",
                color_discrete_sequence=PALETTE,
            )
            c1.plotly_chart(fig, width="stretch")
        fig = px.scatter(
            view,
            x="Frequency",
            y="Monetary",
            color="Segment_Label",
            title="Fréquence vs valeur",
            opacity=0.65,
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(xaxis_title="Fréquence", yaxis_title="CA ($)")
        c2.plotly_chart(fig, width="stretch")
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
        st.dataframe(view[show].head(200), width="stretch", hide_index=True)

    with tabs[2]:
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
                        "Segment_Label": "Persona",
                        "n_clients": "Clients",
                        "pct_clients": "% clients",
                        "pct_CA": "% CA",
                        "age_moyen": "Âge moy.",
                        "depense_totale_usd": "CA moy. ($)",
                        "nb_achats": "Fréquence",
                        "recence_j": "Récence (j)",
                        "panier_moyen_usd": "Panier ($)",
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
                title="Part des clients vs part du CA",
                color_discrete_sequence=PALETTE[:2],
            )
            fig.update_layout(xaxis_title="Persona", yaxis_title="Part")
            st.plotly_chart(fig, width="stretch")

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
                        "accessoires": "Accessories",
                        "vetements": "Clothing",
                        "chaussures": "Footwear",
                        "outerwear": "Outerwear",
                    }
                )
                fig = px.bar(
                    long,
                    x="Segment_Label",
                    y="Part_%",
                    color="Catégorie",
                    title="Mix catégorie moyen par persona",
                    color_discrete_sequence=PALETTE,
                )
                fig.update_layout(xaxis_title="Persona", yaxis_title="Part du CA (%)")
                st.plotly_chart(fig, width="stretch")

            st.subheader("Fiches personas")
            for _, row in profiles.iterrows():
                key = row["Segment"]
                with st.expander(f"{row['Segment_Label']} — {int(row['n_clients'])} clients"):
                    st.markdown(PERSONA_BLURB.get(key, ""))
                    st.markdown(
                        f"- **Poids** : {row['pct_clients']:.1f} % des clients · "
                        f"{row['pct_CA']:.1f} % du CA\n"
                        f"- **Valeur** : CA moyen {money(row['depense_totale_usd'])} · "
                        f"fréquence {row['nb_achats']:.1f} · panier {money(row['panier_moyen_usd'])}\n"
                        f"- **Récence** : {row['recence_j']:.0f} j · "
                        f"{row['pct_recence_gt_90j']:.1f} % à plus de 90 j\n"
                        f"- **Canal** : {row['pct_in_store']:.0f} % magasin · "
                        f"{row['pct_femmes']:.0f} % de femmes"
                    )

    with tabs[3]:
        if campaigns.empty:
            st.info("KPI campagnes introuvables.")
        else:
            tot_budget = float(campaigns["Budget"].sum())
            tot_impr = int(campaigns["Impressions"].sum())
            tot_clicks = int(campaigns["Clicks"].sum())
            tot_conv = int(campaigns["Conversions"].sum())
            kpi_row(
                [
                    ("Budget", money(tot_budget)),
                    ("Impressions", nfmt(tot_impr)),
                    ("CTR", pct(tot_clicks / tot_impr if tot_impr else 0, 2)),
                    ("CPA moy.", money(tot_budget / tot_conv if tot_conv else 0, 2)),
                    ("ROI global", f"{(campaigns['Attributed_Revenue'].sum() - tot_budget) / tot_budget:.2f}"),
                ]
            )
            c1, c2 = st.columns(2)
            fig = px.bar(
                by_channel,
                x="Channel",
                y="CPA",
                title="CPA par canal",
                color="Channel",
                color_discrete_sequence=PALETTE,
            )
            fig.update_layout(showlegend=False, yaxis_title="CPA ($)")
            c1.plotly_chart(fig, width="stretch")
            fig = px.bar(
                by_channel,
                x="Channel",
                y="CTR",
                title="CTR par canal",
                color="Channel",
                color_discrete_sequence=PALETTE,
            )
            fig.update_layout(showlegend=False, yaxis_title="CTR")
            c2.plotly_chart(fig, width="stretch")
            fig = px.scatter(
                campaigns,
                x="Budget",
                y="Conversions",
                color="Channel",
                size="ROAS",
                hover_data=["Campaign_ID", "CPA", "ROI"],
                title="Budget vs conversions (taille = ROAS)",
                color_discrete_sequence=PALETTE,
            )
            st.plotly_chart(fig, width="stretch")
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
            st.dataframe(table, width="stretch", hide_index=True)
            st.caption("ROI = (CA attribué − budget) / budget.")

    with tabs[4]:
        if scored_view.empty:
            st.info("Aucun client dans le filtre. Élargissez le palier de risque.")
        else:
            kpi_row(
                [
                    ("Proba churn moy.", pct(float(scored_view["Churn_Proba"].mean()))),
                    (
                        "Risque élevé",
                        nfmt(int((scored_view["Risk_Tier"] == "Eleve").sum())),
                    ),
                    (
                        "Win-back prioritaire",
                        nfmt(int(scored_view["Winback_prioritaire"].sum())),
                    ),
                    ("CLV prédite totale", money(float(scored_view["CLV_Pred"].sum()))),
                ]
            )
            c1, c2 = st.columns(2)
            hist_src = view.copy()
            fig = px.histogram(
                hist_src,
                x="Churn_Proba",
                color="Segment_Label",
                title="Distribution du score churn",
                color_discrete_sequence=PALETTE,
            )
            c1.plotly_chart(fig, width="stretch")
            fig = px.box(
                hist_src,
                x="Segment_Label",
                y="CLV_Pred",
                color="Segment_Label",
                title="CLV prédite par persona",
                color_discrete_sequence=PALETTE,
            )
            fig.update_layout(showlegend=False, yaxis_title="CLV ($)")
            c2.plotly_chart(fig, width="stretch")

            ic, il = st.columns(2)
            fig = px.bar(
                data.importance_churn.head(10).sort_values("importance"),
                x="importance",
                y="feature",
                orientation="h",
                title="Importance — churn",
                color_discrete_sequence=[PALETTE[1]],
            )
            ic.plotly_chart(fig, width="stretch")
            fig = px.bar(
                data.importance_clv.head(10).sort_values("importance"),
                x="importance",
                y="feature",
                orientation="h",
                title="Importance — CLV",
                color_discrete_sequence=[PALETTE[2]],
            )
            il.plotly_chart(fig, width="stretch")

            st.subheader("Priorité win-back (risque élevé, CLV haute)")
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
            st.dataframe(high[show_h].head(50), width="stretch", hide_index=True)

    with tabs[5]:
        strategy = data.strategy
        mix = data.mix
        if strategy.empty or mix.empty:
            st.info("Impossible de calculer le plan d'allocation.")
        else:
            st.caption(
                f"Enveloppe {money(NEXT_BUDGET)} répartie selon la valeur future et le risque, "
                "puis mixée avec le ROI historique des canaux."
            )
            c1, c2 = st.columns(2)
            fig = px.bar(
                strategy.sort_values("Budget_Recommended"),
                x="Budget_Recommended",
                y="Segment_Label",
                orientation="h",
                title=f"Budget recommandé par persona (enveloppe {nfmt(NEXT_BUDGET)} $)",
                color_discrete_sequence=PALETTE,
            )
            fig.update_layout(xaxis_title="Budget ($)")
            c1.plotly_chart(fig, width="stretch")
            fig = px.pie(
                mix,
                names="Channel",
                values="Budget_Recommended",
                title="Mix média recommandé",
                color_discrete_sequence=PALETTE,
            )
            c2.plotly_chart(fig, width="stretch")

            fig = px.scatter(
                strategy,
                x="churn",
                y=strategy["clv"] / strategy["n"],
                size="n",
                color="Segment_Label",
                title="Matrice risque × valeur (taille = effectif)",
                color_discrete_sequence=PALETTE,
                hover_data=["Primary_Channel", "high_risk", "winback"],
            )
            fig.update_layout(xaxis_title="Proba churn moyenne", yaxis_title="CLV / client ($)")
            st.plotly_chart(fig, width="stretch")

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
                    "Segment_Label": "Persona",
                    "n": "Clients",
                    "Primary_Channel": "Canal",
                    "Budget_Recommended": "Budget reco. ($)",
                    "churn": "Proba churn",
                    "clv": "CLV totale ($)",
                    "high_risk": "Risque élevé",
                    "winback": "Win-back",
                }
            )
            st.dataframe(plan_show, width="stretch", hide_index=True)
            with st.expander("Règles du plan"):
                st.markdown(
                    """
- **VIP** : investir dans l'expérience, pas dans la remise.
- **Risque élevé × CLV haute** : win-back prioritaire (Email).
- **Email** : augmenter (meilleur ROI). **TV** : réduire (CPA).
- Suivi : CPA, récence des dormants, CA VIP.
                    """
                )
