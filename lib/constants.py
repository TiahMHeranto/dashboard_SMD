"""Constantes métier du dashboard."""

from __future__ import annotations

PALETTE = ["#1B4F72", "#148F77", "#B9770E", "#922B21", "#6C3483", "#1A5276"]

RISK_ORDER = ["Faible", "Moyen", "Eleve"]
RISK_LABELS = {"Faible": "Faible", "Moyen": "Moyen", "Eleve": "Élevé"}
RISK_COLORS = {"Faible": "#148F77", "Moyen": "#B9770E", "Eleve": "#922B21"}

SEGMENT_LABELS = {
    "VIP / Champions": "VIP / Champions",
    "Online reguliers (Clothing)": "Online réguliers (Clothing)",
    "In-Store reguliers": "In-Store réguliers",
    "Petits dormants (Accessoires)": "Petits dormants (Accessoires)",
    "Gros paniers occasionnels (Outerwear)": "Gros paniers occasionnels (Outerwear)",
    "Chaussures ponctuels": "Chaussures ponctuels",
}

PLAYBOOK = {
    "VIP / Champions": (
        "Email",
        "Concierge, avant-première, cashback statut — pas de braderie",
    ),
    "Online reguliers (Clothing)": (
        "Social",
        "UGC, visuel Clothing, retargeting visiteurs Online",
    ),
    "In-Store reguliers": (
        "In-Store",
        "Coupons / QR pont digital, fidélité magasin",
    ),
    "Petits dormants (Accessoires)": (
        "Email",
        "Win-back 15 % une fois, preuve sociale, deadline 10 j",
    ),
    "Gros paniers occasionnels (Outerwear)": (
        "Online",
        "Reminder panier / look complet, urgence légère",
    ),
    "Chaussures ponctuels": (
        "Email",
        "Cross-sell et relance au renouvellement",
    ),
}

PERSONA_BLURB = {
    "VIP / Champions": "Cœur de CA (11,6 % des clients, 41,4 % du chiffre). Fidéliser par le statut, pas par la remise.",
    "Online reguliers (Clothing)": "Plus gros volume. Digital-first, Clothing dominant. Social + checkout mobile.",
    "In-Store reguliers": "100 % magasin, panier régulier. Pont magasin–digital plutôt que paid agressif.",
    "Petits dormants (Accessoires)": "Récence élevée, petits paniers Accessoires. Réactivation Email seulement si ROI positif.",
    "Gros paniers occasionnels (Outerwear)": "Peu d'achats mais AOV élevé, Outerwear. Relance avant-saison, pas de promo continue.",
    "Chaussures ponctuels": "Niche Footwear. Cross-sell et relance au renouvellement, canal Email.",
}

FEATURE_LABELS = {
    "Age": "Âge",
    "Gender_Male": "Genre (homme)",
    "Tenure_Days": "Ancienneté (jours)",
    "Recency": "Récence (jours)",
    "Frequency": "Fréquence (tickets)",
    "Monetary": "CA historique ($)",
    "AOV": "Panier moyen ($)",
    "Pct_Online": "Part des achats Online",
    "N_Categories": "Nb de catégories",
    "N_Products": "Nb de produits distincts",
    "Avg_Basket_Qty": "Qté moyenne / ticket",
    "Avg_Discount": "Remise moyenne",
    "Avg_Days_Between": "Jours moyens entre achats",
    "Share_Accessories": "Part Accessories",
    "Share_Clothing": "Part Clothing",
    "Share_Footwear": "Part Footwear",
    "Share_Outerwear": "Part Outerwear",
}

FEATURE_HELP = {
    "Age": "Âge déclaré à l'inscription.",
    "Gender_Male": "Homme ou femme.",
    "Tenure_Days": "Jours depuis l'inscription.",
    "Recency": "Jours depuis le dernier achat.",
    "Frequency": "Nombre de tickets sur l'historique disponible.",
    "Monetary": "Chiffre d'affaires historique du client.",
    "AOV": "Panier moyen (CA / nombre de tickets).",
    "Pct_Online": "Part des tickets canal Online (0 = tout magasin, 1 = tout web).",
    "N_Categories": "Catégories distinctes achetées (1 à 4).",
    "N_Products": "SKU distincts achetés.",
    "Avg_Basket_Qty": "Quantité moyenne d'articles par ticket.",
    "Avg_Discount": "Remise moyenne vs prix catalogue.",
    "Avg_Days_Between": "Écart moyen entre deux tickets. Si un seul achat : égal à la récence.",
    "Share_Accessories": "Part du CA Accessories (les 4 parts devraient sommer à 1).",
    "Share_Clothing": "Part du CA Clothing.",
    "Share_Footwear": "Part du CA Footwear.",
    "Share_Outerwear": "Part du CA Outerwear.",
}

SHARE_COLS = [
    "Share_Accessories",
    "Share_Clothing",
    "Share_Footwear",
    "Share_Outerwear",
]

CHANNEL_ORDER = ["Email", "Social", "Online", "In-Store", "TV"]

NEXT_BUDGET = 150_000

SNAPSHOT_LABEL = "31/07/2026"
PERIOD_LABEL = "juillet 2024 – juillet 2026"
