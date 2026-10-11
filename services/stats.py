from collections import Counter
from utils.config import UNKNOWN_CLINIC


def is_txt_invoice(invoice):
    return invoice.get("document", "").lower().endswith(".txt")

def is_checked(invoice):
    return invoice.get("status") in ("VALIDE", "ANOMALIE")

def is_anomalous(invoice):
    return invoice.get("status") == "ANOMALIE"


def _number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0

def compute_stats(all_invoices):
    invoices = [i for i in all_invoices if is_txt_invoice(i)]
    checked = [i for i in invoices if is_checked(i)]
    anomalous = [i for i in checked if is_anomalous(i)]

    total_checked = len(checked)
    total_anomalies = len(anomalous)
    divergent_total = sum(_number(i.get("divergent_amount")) for i in anomalous)
    amount_total = sum(_number(i.get("amount")) for i in checked)

    clinics = {}
    for inv in checked:
        name = inv.get("clinic") or UNKNOWN_CLINIC
        entry = clinics.setdefault(name, {"total": 0, "anomalies": 0, "divergent": 0.0})
        entry["total"] += 1
        if is_anomalous(inv):
            entry["anomalies"] += 1
            entry["divergent"] += _number(inv.get("divergent_amount"))
    clinic_ranking = sorted(
        clinics.items(),
        key=lambda item: (item[1]["anomalies"], item[1]["divergent"]),
        reverse=True,
    )

    counter = Counter()
    for inv in anomalous:
        for a in inv.get("anomalies") or []:
            counter[(a.get("class", "?"), a.get("field", "?"))] += 1

    return {
        "total_checked": total_checked,
        "total_anomalies": total_anomalies,
        "rate": total_anomalies / total_checked * 100 if total_checked else 0.0,
        "divergent_total": divergent_total,
        "amount_total": amount_total,
        "amount_rate": divergent_total / amount_total * 100 if amount_total else 0.0,
        "pending": sum(1 for i in invoices if i.get("status") == "À VÉRIFIER"),
        "clinic_ranking": clinic_ranking,
        "field_ranking": counter.most_common(),
        "total_errors": sum(counter.values()),
    }
