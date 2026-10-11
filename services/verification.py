import json
from pathlib import Path
from services.parser import parse_invoice

def compare_invoice_with_json(txt_path, cerfa):
    anomalies = []

    if parse_invoice is None:
        anomalies.append({"class": "Invoice", "field": "file", "message": "Parser indisponible"})
        return anomalies

    lots = parse_invoice(txt_path)
    if not lots:
        anomalies.append({"class": "Invoice", "field": "file", "message": "Impossible de lire le fichier TXT"})
        return anomalies

    parsed = [inv for lot in lots for inv in lot.invoices]
    if not parsed:
        anomalies.append({"class": "Invoice", "field": "file", "message": "Aucune facture dans le TXT"})
        return anomalies

    inv = parsed[0]

    checks = [
        ("tier_number", inv.tier_number, cerfa.get("tier_number")),
        ("lot_number", inv.lot_number, cerfa.get("lot_number")),
        ("invoice_number", inv.invoice_number, cerfa.get("invoice_number")),
        ("client_number", inv.client_number, cerfa.get("client_number")),
        ("total_local_service_fee", inv.total_local_service_fee, cerfa.get("total_local_service_fee")),
        ("total_outsider_service_fee", inv.total_outsider_service_fee, cerfa.get("total_outsider_service_fee")),
    ]
    for field, txt_val, js_val in checks:
        if str(txt_val) != str(js_val):
            anomalies.append({"class": "Invoice", "field": field,
                              "message": f"TXT={txt_val} / JSON={js_val}"})

    if cerfa.get("cerfa_identifier") != "12278*01":
        anomalies.append({"class": "Cerfa", "field": "cerfa_identifier",
                          "message": f"Attendu 12278*01, trouvé {cerfa.get('cerfa_identifier')}"})

    if cerfa.get("cerfa_code") != "S3404":
        anomalies.append({"class": "Cerfa", "field": "cerfa_code",
                          "message": f"Attendu S3404, trouvé {cerfa.get('cerfa_code')}"})

    performers = cerfa.get("performers", [])
    if not performers:
        anomalies.append({"class": "Cerfa", "field": "performers",
                          "message": "Aucun intervenant dans le JSON"})
    else:
        for idx, perf in enumerate(performers):
            if not perf.get("has_signature", False):
                anomalies.append({
                    "class": "Cerfa", "field": "performers",
                    "message": f"Signature manquante pour l'intervenant {idx + 1} ({perf.get('number', '')})",
                })

    #txt_services = {(s.type.value, s.number) for s in inv.services}
    #js_services = {(s.get("type"), s.get("number")) for s in cerfa.get("services", [])}
    #if txt_services != js_services:
        #anomalies.append({"class": "Invoice", "field": "services","message": "Prestations différentes entre TXT et JSON"})

    total_service_fee = cerfa.get("total_service_fee")
    expected_total = inv.total_local_service_fee + inv.total_outsider_service_fee
    if total_service_fee is not None and expected_total != total_service_fee:
        anomalies.append({"class": "Cerfa", "field": "total_service_fee",
                          "message": f"TXT={expected_total} / JSON={total_service_fee}"})

    return anomalies


def calculate_divergent_amount(txt_path, cerfa):
    """Écart absolu des totaux financiers TXT/JSON comparés."""
    if parse_invoice is None:
        return 0.0
    try:
        lots = parse_invoice(txt_path)
        parsed = [i for lot in (lots or []) for i in lot.invoices]
        if not parsed:
            return 0.0
        invoice = parsed[0]
        total = 0.0
        for field in ("total_local_service_fee", "total_outsider_service_fee"):
            txt_value = getattr(invoice, field, None)
            json_value = cerfa.get(field)
            if txt_value is None or json_value is None:
                continue
            try:
                total += abs(float(txt_value) - float(json_value))
            except (TypeError, ValueError):
                continue
        return total
    except Exception:
        return 0.0


def verify_pending(invoices):
    """Vérifie les factures « À VÉRIFIER » ayant un JSON associé.
    Retourne le nombre de factures traitées."""
    processed = 0
    for inv in invoices:
        if inv.get("status") != "À VÉRIFIER":
            continue

        txt_path = inv.get("file_path")
        json_path = inv.get("json_path")
        if not txt_path or not json_path:
            continue

        if Path(txt_path).stem.casefold() != Path(json_path).stem.casefold():
            inv["anomalies"] = [{
                "class": "Cerfa", "field": "json",
                "message": f"Noms incompatibles : {Path(txt_path).name} / {Path(json_path).name}",
            }]
            continue

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                cerfa = json.load(f)
        except Exception as e:
            inv["status"] = "ANOMALIE"
            inv["anomalies"] = [{"class": "Cerfa", "field": "json",
                                 "message": f"Impossible de lire le JSON : {e}"}]
            processed += 1
            continue

        anomalies = compare_invoice_with_json(txt_path, cerfa)
        inv["divergent_amount"] = calculate_divergent_amount(txt_path, cerfa)
        inv["anomalies"] = anomalies
        inv["status"] = "ANOMALIE" if anomalies else "VALIDE"
        processed += 1
    return processed
