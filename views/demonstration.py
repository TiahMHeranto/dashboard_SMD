"""Scoring client : profil → risque de churn et valeur future."""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib.constants import (
    FEATURE_HELP,
    FEATURE_LABELS,
    PALETTE,
    SHARE_COLS,
)
from lib.data import money, pct
from lib.models import predict


PRESETS = {
    "Client médian": None,
    "Client à risque": {
        "Age": 34,
        "Gender_Male": 0,
        "Tenure_Days": 400,
        "Recency": 180,
        "Frequency": 2,
        "Monetary": 120,
        "AOV": 60,
        "Pct_Online": 0.5,
        "N_Categories": 1,
        "N_Products": 2,
        "Avg_Basket_Qty": 1.2,
        "Avg_Discount": 0.04,
        "Avg_Days_Between": 180,
        "Share_Accessories": 0.8,
        "Share_Clothing": 0.2,
        "Share_Footwear": 0.0,
        "Share_Outerwear": 0.0,
    },
    "Client VIP": {
        "Age": 34,
        "Gender_Male": 0,
        "Tenure_Days": 800,
        "Recency": 12,
        "Frequency": 30,
        "Monetary": 2800,
        "AOV": 93,
        "Pct_Online": 0.7,
        "N_Categories": 4,
        "N_Products": 12,
        "Avg_Basket_Qty": 1.8,
        "Avg_Discount": 0.04,
        "Avg_Days_Between": 18,
        "Share_Accessories": 0.24,
        "Share_Clothing": 0.46,
        "Share_Footwear": 0.21,
        "Share_Outerwear": 0.09,
    },
}


def _defaults_from_row(row, feature_cols: list[str]) -> dict[str, float]:
    return {c: float(row[c]) for c in feature_cols}


def _number(
    col: str,
    value: float,
    *,
    min_v: float,
    max_v: float,
    step: float,
    fmt: str,
    nonce: str,
):
    return st.number_input(
        FEATURE_LABELS.get(col, col),
        min_value=min_v,
        max_value=max_v,
        value=float(value),
        step=step,
        format=fmt,
        help=FEATURE_HELP.get(col, ""),
        key=f"{nonce}_{col}",
    )


def render_demo() -> None:
    data = st.session_state["bundle"]
    churn_pipe, clv_pipe = st.session_state["pipelines"]
    cols = data.feature_cols
    feats = data.features
    medians = data.train_medians

    st.title("Scoring client")
    st.caption("Estimez le risque de churn et la valeur future à partir du profil d'un client.")

    with st.sidebar:
        st.header("Client")
        mode = st.radio(
            "Source",
            ["Base clients", "Profil type", "Saisie libre"],
        )
        source_row = None
        preset_values = dict(medians)

        if mode == "Base clients":
            options = feats.sort_values("Customer_ID")
            labels = options["label"].tolist()
            ids = options["Customer_ID"].tolist()
            idx = st.selectbox(
                "Client",
                range(len(ids)),
                format_func=lambda i: labels[i],
            )
            source_row = options.iloc[idx]
            preset_values = _defaults_from_row(source_row, cols)
            st.caption(
                f"{source_row['Name']} · {source_row.get('Segment_Label', '')} · "
                f"score actuel : churn {source_row['Churn_Proba']:.1%} · "
                f"CLV {source_row['CLV_Pred']:.0f} $"
            )
        elif mode == "Profil type":
            preset_name = st.selectbox("Profil", list(PRESETS.keys()))
            if PRESETS[preset_name] is None:
                preset_values = dict(medians)
            else:
                preset_values = {**medians, **PRESETS[preset_name]}
        else:
            preset_values = dict(medians)
            st.caption("Valeurs de départ : client médian. Ajustez puis calculez.")

    if mode == "Base clients":
        nonce = f"client_{int(source_row['Customer_ID'])}"
    elif mode == "Profil type":
        nonce = f"preset_{preset_name}"
    else:
        nonce = "libre"

    with st.form("predict_form"):
        st.subheader("Profil")
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown("**Identité & ancienneté**")
            age = _number(
                "Age", preset_values["Age"], min_v=18.0, max_v=80.0, step=1.0, fmt="%.0f", nonce=nonce
            )
            gender = st.radio(
                "Genre",
                ["Femme", "Homme"],
                index=1 if preset_values["Gender_Male"] >= 0.5 else 0,
                horizontal=True,
                key=f"{nonce}_gender",
            )
            tenure = _number(
                "Tenure_Days",
                preset_values["Tenure_Days"],
                min_v=0.0,
                max_v=2000.0,
                step=1.0,
                fmt="%.0f",
                nonce=nonce,
            )
            recency = _number(
                "Recency",
                preset_values["Recency"],
                min_v=0.0,
                max_v=800.0,
                step=1.0,
                fmt="%.0f",
                nonce=nonce,
            )
        with g2:
            st.markdown("**RFM & panier**")
            frequency = _number(
                "Frequency",
                preset_values["Frequency"],
                min_v=1.0,
                max_v=120.0,
                step=1.0,
                fmt="%.0f",
                nonce=nonce,
            )
            monetary = _number(
                "Monetary",
                preset_values["Monetary"],
                min_v=0.0,
                max_v=15000.0,
                step=10.0,
                fmt="%.2f",
                nonce=nonce,
            )
            aov = _number(
                "AOV", preset_values["AOV"], min_v=0.0, max_v=800.0, step=1.0, fmt="%.2f", nonce=nonce
            )
            pct_online = st.slider(
                FEATURE_LABELS["Pct_Online"],
                0.0,
                1.0,
                float(preset_values["Pct_Online"]),
                0.01,
                help=FEATURE_HELP["Pct_Online"],
                key=f"{nonce}_Pct_Online",
            )
        with g3:
            st.markdown("**Comportement d'achat**")
            n_cat = st.slider(
                FEATURE_LABELS["N_Categories"],
                1,
                4,
                int(preset_values["N_Categories"]),
                help=FEATURE_HELP["N_Categories"],
                key=f"{nonce}_N_Categories",
            )
            n_prod = st.slider(
                FEATURE_LABELS["N_Products"],
                1,
                20,
                int(min(20, max(1, preset_values["N_Products"]))),
                help=FEATURE_HELP["N_Products"],
                key=f"{nonce}_N_Products",
            )
            qty = _number(
                "Avg_Basket_Qty",
                preset_values["Avg_Basket_Qty"],
                min_v=1.0,
                max_v=10.0,
                step=0.1,
                fmt="%.2f",
                nonce=nonce,
            )
            discount = st.slider(
                FEATURE_LABELS["Avg_Discount"],
                0.0,
                0.4,
                float(preset_values["Avg_Discount"]),
                0.01,
                help=FEATURE_HELP["Avg_Discount"],
                key=f"{nonce}_Avg_Discount",
            )
            gap = _number(
                "Avg_Days_Between",
                preset_values["Avg_Days_Between"],
                min_v=0.0,
                max_v=800.0,
                step=1.0,
                fmt="%.1f",
                nonce=nonce,
            )

        st.markdown("**Mix catégorie** (recalé à 100 % au calcul)")
        s1, s2, s3, s4 = st.columns(4)
        shares = {}
        boxes = [s1, s2, s3, s4]
        for box, col in zip(boxes, SHARE_COLS):
            with box:
                shares[col] = st.slider(
                    FEATURE_LABELS[col],
                    0.0,
                    1.0,
                    float(preset_values.get(col, 0.0)),
                    0.01,
                    help=FEATURE_HELP[col],
                    key=f"{nonce}_{col}",
                )

        submitted = st.form_submit_button("Calculer les scores", type="primary")

    values = {
        "Age": age,
        "Gender_Male": 1.0 if gender == "Homme" else 0.0,
        "Tenure_Days": tenure,
        "Recency": recency,
        "Frequency": frequency,
        "Monetary": monetary,
        "AOV": aov,
        "Pct_Online": pct_online,
        "N_Categories": float(n_cat),
        "N_Products": float(n_prod),
        "Avg_Basket_Qty": qty,
        "Avg_Discount": discount,
        "Avg_Days_Between": gap,
        **shares,
    }

    if not submitted and "last_prediction" not in st.session_state:
        st.info("Complétez le profil puis cliquez sur **Calculer les scores**.")
        return

    if submitted:
        st.session_state["last_prediction"] = predict(
            churn_pipe, clv_pipe, values, cols, data.threshold
        )
        st.session_state["last_values"] = values
        st.session_state["last_source"] = None if source_row is None else dict(source_row)

    result = st.session_state.get("last_prediction")
    if not result:
        return

    st.divider()
    st.subheader("Résultat")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Churn")
        st.metric("Probabilité de churn", pct(result["churn_proba"], 1))
        st.metric("Décision", "À risque" if result["churn_flag"] else "Stable")
        st.metric("Palier de risque", result["risk_label"])
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=result["churn_proba"] * 100,
                number={"suffix": " %", "valueformat": ".1f"},
                title={"text": "Score churn"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": PALETTE[0]},
                    "threshold": {
                        "line": {"color": PALETTE[3], "width": 3},
                        "thickness": 0.8,
                        "value": data.threshold * 100,
                    },
                    "steps": [
                        {"range": [0, 15], "color": "#d5f5e3"},
                        {"range": [15, data.threshold * 100], "color": "#fdebd0"},
                        {"range": [data.threshold * 100, 100], "color": "#f5b7b1"},
                    ],
                },
            )
        )
        fig.update_layout(height=260, margin=dict(t=40, b=20, l=30, r=30))
        st.plotly_chart(fig, width="stretch")
        st.caption("Trait rouge : seuil d'alerte.")

    with right:
        st.markdown("#### Valeur client (CLV)")
        st.metric("CLV estimée (12 mois)", money(result["clv_pred"]))
        fig = px.bar(
            data.importance_clv.head(8).sort_values("importance"),
            x="importance",
            y="feature",
            orientation="h",
            title="Leviers de la valeur client",
            color_discrete_sequence=[PALETTE[2]],
        )
        fig.update_layout(height=280, margin=dict(t=50, b=20), yaxis_title="")
        st.plotly_chart(fig, width="stretch")

    if result["churn_flag"] and result["clv_pred"] >= 400:
        st.warning(
            "Win-back prioritaire : risque au-dessus du seuil et valeur encore élevée. "
            "Canal recommandé : Email, offre unique datée."
        )
    elif result["churn_flag"]:
        st.info(
            "Risque élevé mais CLV limitée : tunnel low-cost (email), pas d'investissement média fort."
        )
    elif result["risk_tier"] == "Moyen":
        st.info("Palier moyen : sous le seuil d'alerte, à surveiller.")
    elif result["clv_pred"] >= 1500:
        st.success("Client de valeur, risque contenu : privilégier fidélisation / statut, pas la remise.")
    else:
        st.info("Risque faible. Suivi RFM standard.")

    saved = st.session_state.get("last_source")
    if saved and saved.get("Churn_Proba") is not None:
        st.subheader("Écart vs score en base")
        c1, c2 = st.columns(2)
        c1.metric(
            "Churn simulé",
            pct(result["churn_proba"], 1),
            delta=pct(result["churn_proba"] - float(saved["Churn_Proba"]), 1),
        )
        c2.metric(
            "CLV simulée",
            money(result["clv_pred"]),
            delta=money(result["clv_pred"] - float(saved["CLV_Pred"])),
        )
        st.caption("L'écart apparaît si le profil a été modifié par rapport à la fiche client.")

    with st.expander("Variables utilisées"):
        st.dataframe(result["X"].T.rename(columns={0: "valeur"}), width="stretch")
        st.json({k: round(v, 4) for k, v in result["shares_normalized"].items()})
