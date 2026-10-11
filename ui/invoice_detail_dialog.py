from PySide6.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout
from utils.config import FIELD_LABELS, MUTED, TEXT, UNKNOWN_CLINIC
from ui.widgets import make_button, make_card, make_label
from utils.formatting import format_euro

def is_anomalous(invoice):
    return invoice.get("status") == "ANOMALIE"


class InvoiceDetailDialog(QDialog):
    def __init__(self, invoice, parent=None, on_validate=None):
        super().__init__(parent)
        self.invoice = invoice
        self.on_validate = on_validate
        self.setWindowTitle("Détail de la facture")
        self.resize(560, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(16)

        layout.addWidget(make_label("Détail du dossier", 21, TEXT, True))
        layout.addWidget(make_label("Informations du document sélectionné", 11, MUTED))

        card = make_card()
        card_layout = QGridLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setHorizontalSpacing(20)
        card_layout.setVerticalSpacing(15)

        fields = [
            ("Statut", invoice.get("status", "À VÉRIFIER")),
            ("Clinique", invoice.get("clinic") or UNKNOWN_CLINIC),
            ("Contact", invoice.get("contact", "-")),
            ("Numéro de facture", invoice.get("invoice", "-")),
            ("Facture TXT", invoice.get("document", "-")),
            ("Justificatif JSON", invoice.get("json") or "Non fourni"),
        ]
        if is_anomalous(invoice):
            fields.append(("Montant divergent",
                           format_euro(invoice.get("divergent_amount", 0) or 0)))

        for row, (field_name, value) in enumerate(fields):
            card_layout.addWidget(make_label(field_name, 10, MUTED), row, 0)
            card_layout.addWidget(make_label(value, 12, TEXT, True), row, 1)

        layout.addWidget(card)
        layout.addWidget(make_label("Rapport de contrôle", 14, TEXT, True))

        explanation = QLabel(self._build_message())
        explanation.setWordWrap(True)
        explanation.setStyleSheet(
            """
            color: #667085;
            background: #F8FAFD;
            border: 1px solid #E8ECF2;
            border-radius: 10px;
            padding: 14px;
            font-size: 11px;
            """
        )
        layout.addWidget(explanation)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if invoice.get("status") == "ANOMALIE":
            validate_button = make_button("Valider", primary=True)
            validate_button.clicked.connect(self.validate_invoice)
            button_layout.addWidget(validate_button)

        close_button = make_button("Fermer")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def _build_message(self):
        invoice = self.invoice
        anomalies = invoice.get("anomalies") or []
        if invoice.get("status") == "À VÉRIFIER":
            return (
                "Cette facture est en attente de vérification. "
                "Le bouton « Procéder à la vérification » traite les factures "
                "TXT à vérifier qui possèdent un justificatif JSON associé."
            )
        if anomalies:
            title = (
                "Anomalies détectées (facture validée manuellement) :"
                if invoice.get("manually_validated")
                else "Anomalies détectées :"
            )
            lines = []
            for a in anomalies:
                label = FIELD_LABELS.get((a.get("class"), a.get("field")), a.get("field", "?"))
                lines.append(f"• {a.get('class', '?')} › {label} : {a.get('message', '')}")
            return title + "\n" + "\n".join(lines)
        return (
            "Statut actuellement enregistré. Les factures de démonstration "
            "servent uniquement à illustrer l'interface."
        )

    def validate_invoice(self):
        self.invoice["status"] = "VALIDE"
        self.invoice["manually_validated"] = True
        if callable(self.on_validate):
            self.on_validate()
        self.accept()
