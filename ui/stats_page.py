from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget
from utils.config import BG, FIELD_LABELS, MUTED, TEXT, UNKNOWN_CLINIC, YELLOW
from services.stats import compute_stats
from ui.widgets import fill_ranking_table, make_card, make_label, make_ranking_table
from utils.formatting import format_euro, format_percent


class StatsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.setStyleSheet(f"background-color: {BG};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(16)
        layout.addWidget(make_label("Statistiques", 25, TEXT, True))
        layout.addWidget(make_label(
            "Indicateurs calculés à partir des factures TXT effectivement contrôlées.",
            11, MUTED))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)

        def make_kpi(title):
            card = make_card()
            card.setMinimumHeight(125)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 16, 18, 16)
            cl.setSpacing(6)
            cl.addWidget(make_label(title, 10, MUTED, True))
            value = make_label("0", 25, TEXT, True)
            detail = make_label("", 10, MUTED)
            detail.setWordWrap(True)
            cl.addWidget(value)
            cl.addWidget(detail)
            cl.addStretch()
            kpi_row.addWidget(card, 1)
            return value, detail

        self.kpi_rate, self.kpi_rate_detail = make_kpi("TAUX DE FACTURES EN ANOMALIE")
        self.kpi_amount, self.kpi_amount_detail = make_kpi("MONTANT DIVERGENT")
        self.kpi_checked, self.kpi_checked_detail = make_kpi("FACTURES CONTRÔLÉES")
        layout.addLayout(kpi_row)

        self.stats_hint = make_label(
            "Aucune facture contrôlée pour le moment. Importez des fichiers TXT et JSON, "
            "puis lancez la vérification.", 11, YELLOW)
        self.stats_hint.setWordWrap(True)
        layout.addWidget(self.stats_hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(14)
        self.table_clinic = make_ranking_table(
            ["Clinique", "Factures contrôlées", "Factures en anomalie",
             "Taux d'anomalie", "Montant divergent", "Indice"], stretch_col=0)
        self.table_field = make_ranking_table(
            ["Champ", "Type", "Occurrences", "Part des anomalies", "Indice"], stretch_col=0)
        cl.addWidget(make_label("Classement des cliniques", 14, TEXT, True))
        cl.addWidget(self.table_clinic)
        cl.addWidget(make_label("Classement des champs en anomalie", 14, TEXT, True))
        cl.addWidget(self.table_field)
        layout.addWidget(scroll, 1)

    def refresh(self, invoices):
        s = compute_stats(invoices)
        checked = s["total_checked"]

        self.kpi_rate.setText(format_percent(s["rate"]))
        self.kpi_rate_detail.setText(
            f"{s['total_anomalies']} anomalie(s) sur {checked} facture(s) contrôlée(s)"
            if checked else "Aucune facture contrôlée")
        self.kpi_amount.setText(format_euro(s["divergent_total"]))
        self.kpi_amount_detail.setText(
            f"Soit {format_percent(s['amount_rate'])} du montant contrôlé "
            f"({format_euro(s['amount_total'])})"
            if s["amount_total"] else "Montant total des écarts financiers détectés")
        self.kpi_checked.setText(str(checked))
        self.kpi_checked_detail.setText(f"{s['pending']} facture(s) en attente de vérification")
        self.stats_hint.setVisible(checked == 0)

        # Cliniques
        ranking = s["clinic_ranking"]
        max_clinic = max((e["anomalies"] for _, e in ranking), default=0)
        clinic_rows = []
        for name, e in ranking:
            rate = e["anomalies"] / e["total"] * 100 if e["total"] else 0.0
            clinic_rows.append((
                [name or UNKNOWN_CLINIC, e["total"], e["anomalies"], format_percent(rate),
                 format_euro(e["divergent"]), ""],
                e["anomalies"] / max_clinic if max_clinic else 0.0,
            ))
        fill_ranking_table(self.table_clinic, clinic_rows)

        # Champs
        fields = s["field_ranking"]
        max_field = fields[0][1] if fields else 0
        field_rows = []
        for (cls, field), count in fields:
            label = FIELD_LABELS.get((cls, field), field)
            share = count / s["total_errors"] * 100 if s["total_errors"] else 0.0
            field_rows.append((
                [label, cls, count, format_percent(share), ""],
                count / max_field if max_field else 0.0,
            ))
        fill_ranking_table(self.table_field, field_rows)
