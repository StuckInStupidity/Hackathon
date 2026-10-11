"""Données de démonstration (non utilisées par défaut)."""

DEMO_CLINICS = [
    "Clinique Saint-Joseph",
    "Clinique des Pins",
    "Centre Médical du Lac",
    "Polyclinique Horizon",
]
DEMO_ANOMALIES = [
    ("Invoice", "total_local_service_fee", "Total différent du CERFA"),
    ("Invoice", "total_outsider_service_fee", "Montant extérieur incohérent"),
    ("Invoice", "services", "Prestation non reconnue"),
    ("Cerfa", "has_signature", "Signature manquante"),
    ("Cerfa", "performers", "Intervenant inconnu"),
]
DEMO_INVOICES = []


def make_sample_invoices():
    def anomaly(cls, field, message):
        return {"class": cls, "field": field, "message": message}

    rows = [
        ("Clinique Saint-Joseph", "ANOMALIE", 1250.0, 310.0, [
            anomaly("Invoice", "total_local_service_fee", "Total différent du CERFA"),
            anomaly("Cerfa", "has_signature", "Signature manquante"),
        ]),
        ("Clinique Saint-Joseph", "ANOMALIE", 840.0, 120.0, [
            anomaly("Invoice", "total_local_service_fee", "Total différent du CERFA"),
        ]),
        ("Clinique Saint-Joseph", "VALIDE", 460.0, 0.0, []),
        ("Clinique des Pins", "ANOMALIE", 2100.0, 780.0, [
            anomaly("Invoice", "services", "Prestation non reconnue"),
            anomaly("Invoice", "total_outsider_service_fee", "Montant extérieur incohérent"),
        ]),
        ("Clinique des Pins", "VALIDE", 380.0, 0.0, []),
        ("Clinique des Pins", "VALIDE", 520.0, 0.0, []),
        ("Centre Médical du Lac", "ANOMALIE", 690.0, 90.0, [
            anomaly("Cerfa", "performers", "Intervenant inconnu"),
        ]),
        ("Centre Médical du Lac", "VALIDE", 910.0, 0.0, []),
        ("Centre Médical du Lac", "VALIDE", 300.0, 0.0, []),
        ("Polyclinique Horizon", "VALIDE", 1500.0, 0.0, []),
        ("Polyclinique Horizon", "ANOMALIE", 1780.0, 410.0, [
            anomaly("Invoice", "total_local_service_fee", "Total différent du CERFA"),
            anomaly("Invoice", "services", "Prestation non reconnue"),
        ]),
    ]

    invoices = []
    for i, (clinic, status, amount, divergent, anomalies) in enumerate(rows, 1):
        invoices.append({
            "status": status,
            "contact": "Exemple",
            "invoice": f"FAC-EX-{i:04d}",
            "document": f"exemple_{i:03d}.txt",
            "json": "exemple.json",
            "clinic": clinic,
            "amount": amount,
            "divergent_amount": divergent,
            "anomalies": anomalies,
            "demo": True,
            "sample": True,
        })
    return invoices
