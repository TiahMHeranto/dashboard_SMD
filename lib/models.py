"""Chargement des pipelines sklearn (churn + CLV) et inférence."""

from __future__ import annotations

from typing import Any

import joblib
import pandas as pd

from .constants import RISK_LABELS, SHARE_COLS
from .data import MODELS_DIR


def load_pipelines() -> tuple[Any, Any]:
    churn = joblib.load(MODELS_DIR / "churn_model.pkl")
    clv = joblib.load(MODELS_DIR / "clv_model.pkl")
    return churn, clv


def risk_tier(proba: float, threshold: float) -> str:
    if proba >= threshold:
        return "Eleve"
    if proba >= 0.15:
        return "Moyen"
    return "Faible"


def normalize_shares(values: dict[str, float]) -> dict[str, float]:
    total = sum(float(values.get(c, 0) or 0) for c in SHARE_COLS)
    out = dict(values)
    if total <= 0:
        out["Share_Clothing"] = 1.0
        for c in SHARE_COLS:
            if c != "Share_Clothing":
                out[c] = 0.0
        return out
    for c in SHARE_COLS:
        out[c] = float(out.get(c, 0) or 0) / total
    return out


def features_frame(values: dict[str, float], feature_cols: list[str]) -> pd.DataFrame:
    row = {c: float(values.get(c, 0) or 0) for c in feature_cols}
    if row.get("Frequency", 0) > 0 and row.get("AOV", 0) == 0:
        row["AOV"] = row["Monetary"] / row["Frequency"]
    return pd.DataFrame([row], columns=feature_cols)


def predict(
    churn_pipe: Any,
    clv_pipe: Any,
    values: dict[str, float],
    feature_cols: list[str],
    threshold: float,
) -> dict[str, Any]:
    values = normalize_shares(values)
    X = features_frame(values, feature_cols)
    proba = float(churn_pipe.predict_proba(X)[:, 1][0])
    clv = float(max(0.0, clv_pipe.predict(X)[0]))
    tier = risk_tier(proba, threshold)
    return {
        "X": X,
        "churn_proba": proba,
        "churn_flag": int(proba >= threshold),
        "clv_pred": clv,
        "risk_tier": tier,
        "risk_label": RISK_LABELS[tier],
        "threshold": threshold,
        "shares_normalized": {c: values[c] for c in SHARE_COLS},
    }
