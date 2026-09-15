"""Constantes métier du dashboard."""

from __future__ import annotations

PALETTE = ["#1B4F72", "#148F77", "#B9770E", "#922B21", "#6C3483", "#1A5276"]

RISK_ORDER = ["Faible", "Moyen", "Eleve"]
RISK_LABELS = {"Faible": "Faible", "Moyen": "Moyen", "Eleve": "Élevé"}
RISK_COLORS = {"Faible": "#16794A", "Moyen": "#FFFFFF", "Eleve": "#C94040"}

SEGMENT_LABELS = {
    "VIP / Champions": "Clients à très haute valeur",
    "Online reguliers (Clothing)": "Clients en ligne réguliers · Vêtements",
    "In-Store reguliers": "Clients réguliers en magasin",
    "Petits dormants (Accessoires)": "Clients dormants · Accessoires",
    "Gros paniers occasionnels (Outerwear)": "Gros paniers occasionnels · Vêtements d'extérieur",
    "Chaussures ponctuels": "Acheteurs occasionnels · Chaussures",
}

PLAYBOOK = {
    "VIP / Champions": (
        "Email",
        "Conciergerie, avant-première et avantage de statut, sans remise massive",
    ),
    "Online reguliers (Clothing)": (
        "Social",
        "Contenus clients, visuels de vêtements et reciblage des visiteurs en ligne",
    ),
    "In-Store reguliers": (
        "In-Store",
        "Coupons avec code à scanner, passerelle numérique et fidélité en magasin",
    ),
    "Petits dormants (Accessoires)": (
        "Email",
        "Réactivation avec 15 % de remise unique, preuve sociale et délai de 10 jours",
    ),
    "Gros paniers occasionnels (Outerwear)": (
        "Online",
        "Rappel du panier, tenue complète et urgence modérée",
    ),
    "Chaussures ponctuels": (
        "Email",
        "Vente croisée et relance au renouvellement",
    ),
}

PERSONA_BLURB = {
    "VIP / Champions": "Cœur du chiffre d'affaires : 11,6 % des clients et 41,4 % du revenu. Fidéliser par le statut, pas par la remise.",
    "Online reguliers (Clothing)": "Plus gros volume. Parcours numérique prioritaire et vêtements dominants. Réseaux sociaux et paiement mobile.",
    "In-Store reguliers": "Achats exclusivement en magasin et panier régulier. Créer un pont entre magasin et numérique.",
    "Petits dormants (Accessoires)": "Récence élevée et petits paniers d'accessoires. Réactivation par courrier électronique si elle reste rentable.",
    "Gros paniers occasionnels (Outerwear)": "Peu d'achats mais panier moyen élevé, dominé par les vêtements d'extérieur. Relance avant-saison.",
    "Chaussures ponctuels": "Segment spécialisé dans les chaussures. Vente croisée et relance au renouvellement par courrier électronique.",
}

FEATURE_LABELS = {
    "Age": "Âge",
    "Gender_Male": "Genre (homme)",
    "Tenure_Days": "Ancienneté (jours)",
    "Recency": "Récence (jours)",
    "Frequency": "Nombre de transactions",
    "Monetary": "Chiffre d'affaires historique ($)",
    "AOV": "Panier moyen ($)",
    "Pct_Online": "Part des achats en ligne",
    "N_Categories": "Nombre de catégories",
    "N_Products": "Nombre de produits distincts",
    "Avg_Basket_Qty": "Quantité moyenne par transaction",
    "Avg_Discount": "Remise moyenne",
    "Avg_Days_Between": "Jours moyens entre achats",
    "Share_Accessories": "Part des accessoires",
    "Share_Clothing": "Part des vêtements",
    "Share_Footwear": "Part des chaussures",
    "Share_Outerwear": "Part des vêtements d'extérieur",
}

FEATURE_HELP = {
    "Age": "Âge déclaré à l'inscription.",
    "Gender_Male": "Homme ou femme.",
    "Tenure_Days": "Jours depuis l'inscription.",
    "Recency": "Jours depuis le dernier achat.",
    "Frequency": "Nombre de tickets sur l'historique disponible.",
    "Monetary": "Chiffre d'affaires historique du client.",
    "AOV": "Panier moyen : chiffre d'affaires divisé par le nombre de transactions.",
    "Pct_Online": "Part des transactions réalisées en ligne : 0 pour tout en magasin, 1 pour tout sur le site.",
    "N_Categories": "Catégories distinctes achetées (1 à 4).",
    "N_Products": "Nombre de références produit distinctes achetées.",
    "Avg_Basket_Qty": "Quantité moyenne d'articles par transaction.",
    "Avg_Discount": "Remise moyenne par rapport au prix catalogue.",
    "Avg_Days_Between": "Écart moyen entre deux transactions. Pour un achat unique, il est égal à la récence.",
    "Share_Accessories": "Part du chiffre d'affaires consacrée aux accessoires.",
    "Share_Clothing": "Part du chiffre d'affaires consacrée aux vêtements.",
    "Share_Footwear": "Part du chiffre d'affaires consacrée aux chaussures.",
    "Share_Outerwear": "Part du chiffre d'affaires consacrée aux vêtements d'extérieur.",
}

SHARE_COLS = [
    "Share_Accessories",
    "Share_Clothing",
    "Share_Footwear",
    "Share_Outerwear",
]

CHANNEL_ORDER = ["Email", "Social", "Online", "In-Store", "TV"]
CHANNEL_LABELS = {
    "Email": "Courrier électronique",
    "Social": "Réseaux sociaux",
    "Online": "En ligne",
    "In-Store": "En magasin",
    "TV": "Télévision",
}

NEXT_BUDGET = 150_000

SNAPSHOT_LABEL = "31/07/2026"
PERIOD_LABEL = "juillet 2024 – juillet 2026"
