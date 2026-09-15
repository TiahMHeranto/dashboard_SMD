"""Chemins et assemblage des données du dashboard."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .constants import (
    CHANNEL_ORDER,
    NEXT_BUDGET,
    PLAYBOOK,
    RISK_LABELS,
    SEGMENT_LABELS,
)


def find_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "DatasetsInitial" / "sales_data.csv").exists():
            return candidate
        if (candidate / "app.py").exists() and (candidate / "lib").is_dir():
            return candidate
    raise FileNotFoundError("Racine du dashboard introuvable (app.py).")


def _models_dir(root: Path) -> Path:
    for candidate in (root / "modeles", root / "Livrable finale" / "modeles"):
        if (candidate / "churn_model.pkl").exists():
            return candidate
    return root / "modeles"


ROOT = find_root()
DATA_DIR = ROOT / "DatasetsInitial"
LIVRABLE = ROOT / "Livrable finale"
EXPORTS = LIVRABLE / "exports_modeles"
ANNEXES = LIVRABLE / "annexes"
MODELS_DIR = _models_dir(ROOT)
CLUSTERS_PATH = ROOT / "clients_avec_clusters.csv"
PROFILES_PATH = ROOT / "Livrables" / "annexes" / "profils_segments.csv"


def money(x: float, digits: int = 0) -> str:
    fmt = f"{x:,.{digits}f} $".replace(",", " ")
    return fmt


def pct(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}%}".replace(".", ",")


def nfmt(x: float, digits: int = 0) -> str:
    return f"{x:,.{digits}f}".replace(",", " ")


@dataclass
class DashboardBundle:
    customers: pd.DataFrame
    scores: pd.DataFrame
    campaigns: pd.DataFrame
    by_channel: pd.DataFrame
    monthly: pd.DataFrame
    profiles: pd.DataFrame
    strategy: pd.DataFrame
    mix: pd.DataFrame
    features: pd.DataFrame
    train_medians: dict[str, float]
    selection: dict
    holdout: dict
    importance_churn: pd.DataFrame
    importance_clv: pd.DataFrame
    feature_cols: list[str]
    threshold: float


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _campaign_kpis(raw: pd.DataFrame) -> pd.DataFrame:
    c = raw.copy()
    c["Start_Date"] = pd.to_datetime(c["Start_Date"])
    c["End_Date"] = pd.to_datetime(c["End_Date"])
    c["CTR"] = np.where(c["Impressions"] > 0, c["Clicks"] / c["Impressions"], 0.0)
    c["CVR"] = np.where(c["Clicks"] > 0, c["Conversions"] / c["Clicks"], 0.0)
    c["CPC"] = np.where(c["Clicks"] > 0, c["Budget"] / c["Clicks"], np.nan)
    c["CPA"] = np.where(c["Conversions"] > 0, c["Budget"] / c["Conversions"], np.nan)
    c["ROI"] = np.where(c["Budget"] > 0, (c["Attributed_Revenue"] - c["Budget"]) / c["Budget"], np.nan)
    c["ROAS"] = np.where(c["Budget"] > 0, c["Attributed_Revenue"] / c["Budget"], np.nan)
    return c


def _by_channel(campaigns: pd.DataFrame) -> pd.DataFrame:
    g = campaigns.groupby("Channel", as_index=False).agg(
        n=("Campaign_ID", "count"),
        Budget=("Budget", "sum"),
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks", "sum"),
        Conversions=("Conversions", "sum"),
        revenue=("Attributed_Revenue", "sum"),
    )
    tot_b = g["Budget"].sum()
    g["pct_budget"] = g["Budget"] / tot_b
    g["pct_conv"] = g["Conversions"] / g["Conversions"].sum()
    g["CTR"] = np.where(g["Impressions"] > 0, g["Clicks"] / g["Impressions"], 0.0)
    g["CVR"] = np.where(g["Clicks"] > 0, g["Conversions"] / g["Clicks"], 0.0)
    g["CPC"] = np.where(g["Clicks"] > 0, g["Budget"] / g["Clicks"], np.nan)
    g["CPA"] = np.where(g["Conversions"] > 0, g["Budget"] / g["Conversions"], np.nan)
    g["ROI"] = np.where(g["Budget"] > 0, (g["revenue"] - g["Budget"]) / g["Budget"], np.nan)
    g["ROAS"] = np.where(g["Budget"] > 0, g["revenue"] / g["Budget"], np.nan)
    g["Channel"] = pd.Categorical(g["Channel"], CHANNEL_ORDER, ordered=True)
    return g.sort_values("Channel").reset_index(drop=True)


def _monthly_sales(sales: pd.DataFrame) -> pd.DataFrame:
    s = sales.copy()
    s["Date"] = pd.to_datetime(s["Date"])
    monthly = (
        s.set_index("Date")
        .resample("ME")
        .agg(revenue=("Sale_Price", "sum"), orders=("Sale_ID", "count"))
        .reset_index()
    )
    return monthly


def _favorite_category(row: pd.Series) -> str:
    mapping = {
        "Accessories": float(row.get("cat_Accessories", 0) or 0),
        "Clothing": float(row.get("cat_Clothing", 0) or 0),
        "Footwear": float(row.get("cat_Footwear", 0) or 0),
        "Outerwear": float(row.get("cat_Outerwear", 0) or 0),
    }
    return max(mapping, key=mapping.get)


def _operational_features(
    customers: pd.DataFrame,
    sales: pd.DataFrame,
    products: pd.DataFrame,
    feature_cols: list[str],
) -> pd.DataFrame:
    """Photo opérationnelle : features calculées au dernier ticket."""
    snap = sales["Date"].max()
    merged = sales.merge(products, on="Product_ID", how="left")
    merged["Unit_Price_Paid"] = np.where(
        merged["Quantity"] > 0, merged["Sale_Price"] / merged["Quantity"], np.nan
    )
    merged["Discount_Rate"] = np.where(
        merged["Price"] > 0, 1 - (merged["Unit_Price_Paid"] / merged["Price"]), 0.0
    )
    agg = merged.groupby("Customer_ID").agg(
        Frequency=("Sale_ID", "count"),
        Monetary=("Sale_Price", "sum"),
        Last_Purchase=("Date", "max"),
        N_Products=("Product_ID", "nunique"),
        N_Categories=("Category", "nunique"),
        Pct_Online=("Channel", lambda s: float((s == "Online").mean())),
        Avg_Basket_Qty=("Quantity", "mean"),
        Avg_Discount=("Discount_Rate", "mean"),
    )
    ordered = merged.sort_values(["Customer_ID", "Date"])
    ordered["gap_days"] = ordered.groupby("Customer_ID")["Date"].diff().dt.days
    inter = ordered.groupby("Customer_ID")["gap_days"].mean().rename("Avg_Days_Between")
    agg = agg.join(inter)
    cat_spend = merged.pivot_table(
        index="Customer_ID",
        columns="Category",
        values="Sale_Price",
        aggfunc="sum",
        fill_value=0,
    ).add_prefix("Spend_")
    agg = agg.join(cat_spend)

    cur = customers.merge(agg, on="Customer_ID", how="left")
    cur["Frequency"] = cur["Frequency"].fillna(0).astype(int)
    cur["Monetary"] = cur["Monetary"].fillna(0.0)
    for col in ["N_Products", "N_Categories", "Pct_Online", "Avg_Basket_Qty", "Avg_Discount"]:
        cur[col] = cur[col].fillna(0)
    cur["Recency"] = (snap - cur["Last_Purchase"]).dt.days
    cur["Recency"] = cur["Recency"].fillna((snap - cur["Join_Date"]).dt.days)
    cur["Tenure_Days"] = (snap - cur["Join_Date"]).dt.days.clip(lower=0)
    cur["AOV"] = np.where(cur["Frequency"] > 0, cur["Monetary"] / cur["Frequency"], 0.0)
    cur["Avg_Days_Between"] = cur["Avg_Days_Between"].fillna(cur["Recency"].clip(lower=1))
    cur["Gender_Male"] = (cur["Gender"] == "Male").astype(int)
    for col in [c for c in cur.columns if str(c).startswith("Spend_")]:
        cur[col] = cur[col].fillna(0.0)
        cur[col.replace("Spend_", "Share_")] = np.where(
            cur["Monetary"] > 0, cur[col] / cur["Monetary"], 0.0
        )
    for col in feature_cols:
        if col not in cur.columns:
            cur[col] = 0.0
    return cur.loc[cur["Frequency"] > 0].copy()


def _strategy(scores: pd.DataFrame, by_channel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    seg = scores.groupby("Segment", as_index=False).agg(
        n=("Customer_ID", "count"),
        ca=("Monetary", "sum"),
        churn=("Churn_Proba", "mean"),
        clv=("CLV_Pred", "sum"),
        high_risk=("Risk_Tier", lambda s: int((s == "Eleve").sum())),
        winback=("Winback_prioritaire", "sum"),
    )
    rows = []
    for _, r in seg.iterrows():
        name = str(r["Segment"])
        channel, message = PLAYBOOK.get(
            name,
            (
                "Email",
                "Suivi de la récence, de la fréquence et de la valeur avec une offre "
                "adaptée à la catégorie préférée",
            ),
        )
        rows.append({"Segment": name, "Primary_Channel": channel, "Message": message})
    plan = seg.merge(pd.DataFrame(rows), on="Segment")
    plan["Alloc_Score"] = plan["clv"].fillna(0) * (0.5 + plan["churn"].fillna(0.2))
    plan.loc[plan["Alloc_Score"] < 0, "Alloc_Score"] = 0
    total_score = plan["Alloc_Score"].sum() or 1
    plan["Budget_Share"] = plan["Alloc_Score"] / total_score
    plan["Budget_Recommended"] = plan["Budget_Share"] * NEXT_BUDGET
    plan["Segment_Label"] = plan["Segment"].map(SEGMENT_LABELS).fillna(plan["Segment"])

    ch = by_channel.copy()
    ch["roi_pos"] = ch["ROI"].clip(lower=0) + 0.05
    ch["Channel_Share_Perf"] = ch["roi_pos"] / ch["roi_pos"].sum()
    persona_need = plan.groupby("Primary_Channel")["Budget_Recommended"].sum()
    persona_need = persona_need / persona_need.sum()
    mix = ch[["Channel", "Channel_Share_Perf", "ROI", "CPA", "CTR"]].copy()
    mix["Channel_Share_Persona"] = mix["Channel"].map(persona_need).fillna(0.05)
    mix["Channel_Share_Persona"] = mix["Channel_Share_Persona"] / mix["Channel_Share_Persona"].sum()
    mix["Channel_Share"] = 0.6 * mix["Channel_Share_Perf"] + 0.4 * mix["Channel_Share_Persona"]
    mix["Budget_Recommended"] = mix["Channel_Share"] * NEXT_BUDGET
    return plan, mix


def load_bundle() -> DashboardBundle:
    selection = _read_json(EXPORTS / "selection.json")
    holdout = _read_json(EXPORTS / "holdout_metrics.json")
    feature_cols: list[str] = list(selection["feature_cols"])
    threshold = float(selection["churn_threshold"])

    customers_raw = pd.read_csv(DATA_DIR / "customers_data.csv", parse_dates=["Join_Date"])
    sales = pd.read_csv(DATA_DIR / "sales_data.csv", parse_dates=["Date"])
    products = pd.read_csv(DATA_DIR / "products_data.csv")
    scores = pd.read_csv(LIVRABLE / "customer_scores.csv")
    camps_raw = pd.read_csv(ANNEXES / "kpi_campagnes_attribution.csv")
    profiles = pd.read_csv(PROFILES_PATH)
    train = pd.read_csv(EXPORTS / "train.csv")
    importance_churn = pd.read_csv(EXPORTS / "importance_churn.csv")
    importance_clv = pd.read_csv(EXPORTS / "importance_clv.csv")

    campaigns = _campaign_kpis(camps_raw)
    by_channel = _by_channel(campaigns)
    monthly = _monthly_sales(sales)

    view = scores.merge(
        customers_raw[["Customer_ID", "Age", "Gender", "Location", "Join_Date"]],
        on="Customer_ID",
        how="left",
    )
    if CLUSTERS_PATH.exists():
        clusters = pd.read_csv(CLUSTERS_PATH)
        keep = [
            c
            for c in [
                "Customer_ID",
                "avg_basket",
                "cat_Accessories",
                "cat_Clothing",
                "cat_Footwear",
                "cat_Outerwear",
                "Channel",
            ]
            if c in clusters.columns
        ]
        view = view.merge(clusters[keep], on="Customer_ID", how="left")
        view["Favorite_Category"] = view.apply(_favorite_category, axis=1)
        view["Pct_InStore"] = view["Channel"] if "Channel" in view.columns else np.nan
    else:
        view["Favorite_Category"] = "n.d."
        view["Pct_InStore"] = np.nan

    view["AOV"] = np.where(view["Frequency"] > 0, view["Monetary"] / view["Frequency"], 0.0)
    view["Segment_Label"] = view["Segment"].map(SEGMENT_LABELS).fillna(view["Segment"])
    view["Risk_Label"] = view["Risk_Tier"].map(RISK_LABELS).fillna(view["Risk_Tier"])

    profiles = profiles.copy()
    profiles["Segment_Label"] = profiles["Segment"].map(SEGMENT_LABELS).fillna(profiles["Segment"])
    profiles["Share_Customers"] = profiles["pct_clients"] / 100.0
    profiles["Share_Revenue"] = profiles["pct_CA"] / 100.0

    strategy, mix = _strategy(scores, by_channel)

    feats = _operational_features(customers_raw, sales, products, feature_cols)
    feats = feats.merge(
        scores[["Customer_ID", "Segment", "Churn_Proba", "CLV_Pred", "Risk_Tier", "Winback_prioritaire"]],
        on="Customer_ID",
        how="left",
        suffixes=("", "_score"),
    )
    feats["Segment_Label"] = feats["Segment"].map(SEGMENT_LABELS).fillna(feats["Segment"])
    feats["label"] = (
        feats["Customer_ID"].astype(str)
        + " — "
        + feats["Name"].fillna("")
        + " ("
        + feats["Segment_Label"].fillna("n.d.")
        + ")"
    )

    medians = {col: float(train[col].median()) for col in feature_cols}

    return DashboardBundle(
        customers=view,
        scores=scores,
        campaigns=campaigns,
        by_channel=by_channel,
        monthly=monthly,
        profiles=profiles,
        strategy=strategy,
        mix=mix,
        features=feats,
        train_medians=medians,
        selection=selection,
        holdout=holdout,
        importance_churn=importance_churn,
        importance_clv=importance_clv,
        feature_cols=feature_cols,
        threshold=threshold,
    )


def missing_inputs() -> list[str]:
    needed = [
        DATA_DIR / "customers_data.csv",
        DATA_DIR / "sales_data.csv",
        DATA_DIR / "products_data.csv",
        LIVRABLE / "customer_scores.csv",
        ANNEXES / "kpi_campagnes_attribution.csv",
        PROFILES_PATH,
        EXPORTS / "selection.json",
        EXPORTS / "holdout_metrics.json",
        EXPORTS / "train.csv",
        MODELS_DIR / "churn_model.pkl",
        MODELS_DIR / "clv_model.pkl",
    ]
    return [str(p) for p in needed if not p.exists()]
