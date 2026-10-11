import json
from pathlib import Path
from utils.config import UNKNOWN_CLINIC

def new_pending_invoice(txt_path):
    """Crée une entrée « À VÉRIFIER » pour un fichier TXT importé."""
    return {
        "status": "À VÉRIFIER", "contact": "-", "invoice": "-",
        "document": Path(txt_path).name, "json": "", "json_path": None,
        "file_path": txt_path, "clinic": UNKNOWN_CLINIC, "amount": 0,
        "divergent_amount": 0, "anomalies": [], "demo": False, "sample": False,
    }

def _key(path):
    return str(Path(path).resolve()).casefold()

def import_files(invoices, files):
    """Met à jour la liste `invoices` (en place) à partir des fichiers choisis."""
    # Conserver les fichiers déjà importés lors d'une précédente importation.
    json_paths = {_key(f): str(Path(f).resolve())
                  for f in files if Path(f).suffix.casefold() == ".json"}
    txt_paths = {_key(f): str(Path(f).resolve())
                 for f in files if Path(f).suffix.casefold() == ".txt"}
    for inv in invoices:
        old_json = inv.get("json_path")
        old_txt = inv.get("file_path")
        if old_json and Path(old_json).is_file():
            json_paths[_key(old_json)] = str(Path(old_json).resolve())
        if old_txt and Path(old_txt).is_file():
            txt_paths[_key(old_txt)] = str(Path(old_txt).resolve())
    json_by_stem = {}
    for js in json_paths.values():
        json_by_stem.setdefault(Path(js).stem.casefold(), []).append(js)

    for txt in txt_paths.values():
        existing = next((i for i in invoices
                         if i.get("file_path") and _key(i["file_path"]) == _key(txt)), None)
        if existing is None:
            existing = new_pending_invoice(txt)
            invoices.append(existing)

        matches = json_by_stem.get(Path(txt).stem.casefold(), [])
        same_dir = [js for js in matches
                    if Path(js).parent.resolve() == Path(txt).parent.resolve()]
        if len(same_dir) == 1:
            js = same_dir[0]
        elif len(matches) == 1:
            js = matches[0]
        elif len(matches) == 0:
            existing["json"] = ""
            existing["json_path"] = None
            continue
        else:
            existing["json"] = ""
            existing["json_path"] = None
            existing["anomalies"] = [{
                "class": "Cerfa", "field": "json",
                "message": "Plusieurs JSON portent ce nom ; association ambiguë. "
                           "Importez-les dans le même dossier que le TXT ou renommez-les.",
            }]
            continue

        try:
            with open(js, "r", encoding="utf-8") as f:
                cerfa = json.load(f)
        except Exception as e:
            existing["json"] = Path(js).name
            existing["json_path"] = js
            existing["anomalies"] = [{"class": "Cerfa", "field": "json",
                                      "message": f"Impossible de lire le JSON : {e}"}]
            continue

        existing.update({
            "document": Path(txt).name, "json": Path(js).name,
            "json_path": js, "file_path": txt,
            "contact": cerfa.get("client_number", "-"),
            "invoice": cerfa.get("invoice_number", "-"),
            "clinic": cerfa.get("tier_number", UNKNOWN_CLINIC),
            "amount": cerfa.get("total_service_fee", 0),
        })
        # Une nouvelle association doit pouvoir être vérifiée.
        if existing.get("status") not in ("VALIDE", "ANOMALIE"):
            existing["status"] = "À VÉRIFIER"
