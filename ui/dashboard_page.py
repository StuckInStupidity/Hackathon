from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QHeaderView, QLineEdit, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from utils.config import BG, GREEN, MUTED, RED, TEXT, YELLOW
from ui.donut_chart import DonutChart
from ui.styles import SEARCH_INPUT_STYLE, TABLE_STYLE
from ui.widgets import make_button, make_card, make_label


class DashboardPage(QWidget):
    import_requested = Signal()
    verify_requested = Signal()
    invoice_opened = Signal(object)  # object : conserve l'identité du dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.invoices = []
        self.filtered_invoices = []
        self._build()

    # ---------- construction ----------
    def _build(self):
        self.setStyleSheet(f"background-color: {BG};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        main_layout.addLayout(self._build_header())
        main_layout.addLayout(self._build_summary_row())
        main_layout.addWidget(self._build_table_card())

    def _build_header(self):
        header = QHBoxLayout()
        title_area = QVBoxLayout()
        title_area.setSpacing(5)
        title_area.addWidget(make_label("Tableau de bord", 25, TEXT, True))
        title_area.addWidget(make_label("Suivi et vérification des dépenses de santé", 11, MUTED))
        header.addLayout(title_area)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher une facture...")
        self.search_input.setFixedWidth(210)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet(SEARCH_INPUT_STYLE)
        self.search_input.textChanged.connect(self.apply_filter)
        header.addWidget(self.search_input)

        import_button = make_button("+ Importer des fichiers", False)
        import_button.clicked.connect(self.import_requested.emit)
        header.addWidget(import_button)

        self.verify_button = make_button("Procéder à la vérification", True)
        self.verify_button.clicked.connect(self.verify_requested.emit)
        header.addWidget(self.verify_button)
        return header

    def _build_summary_row(self):
        row = QHBoxLayout()
        row.setSpacing(18)

        pending_card = make_card()
        pending_card.setMinimumHeight(170)
        pl = QVBoxLayout(pending_card)
        pl.setContentsMargins(22, 20, 22, 20)
        pl.setSpacing(9)
        pl.addWidget(make_label("À TRAITER", 10, MUTED, True))
        self.pending_number = make_label("0", 34, TEXT, True)
        pl.addWidget(self.pending_number)
        pl.addWidget(make_label("Factures en attente de vérification", 11, MUTED))
        pl.addStretch()
        pl.addWidget(make_label("●  Statut : À VÉRIFIER", 10, YELLOW, True))
        row.addWidget(pending_card, 1)

        chart_card = make_card()
        chart_card.setMinimumHeight(170)
        cl = QHBoxLayout(chart_card)
        cl.setContentsMargins(18, 12, 18, 12)
        cl.setSpacing(15)

        self.donut = DonutChart()
        cl.addWidget(self.donut, 0, Qt.AlignmentFlag.AlignVCenter)

        legend = QVBoxLayout()
        legend.setSpacing(11)
        legend.addWidget(make_label("Répartition des statuts", 12, TEXT, True))
        self.valid_legend = make_label("●  Validées : 0", 10, GREEN)
        self.review_legend = make_label("●  À vérifier : 0", 10, YELLOW)
        self.anomaly_legend = make_label("●  Anomalies : 0", 10, RED)
        legend.addWidget(self.valid_legend)
        legend.addWidget(self.review_legend)
        legend.addWidget(self.anomaly_legend)
        legend.addStretch()
        cl.addLayout(legend, 1)
        row.addWidget(chart_card, 1)
        return row

    def _build_table_card(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        head = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(4)
        titles.addWidget(make_label("Factures récentes", 16, TEXT, True))
        titles.addWidget(make_label(
            "Chaque fichier TXT représente une facture ; le JSON représente son justificatif.",
            10, MUTED))
        head.addLayout(titles)
        head.addStretch()
        self.count_label = make_label("0 facture(s)", 10, MUTED)
        head.addWidget(self.count_label)
        layout.addLayout(head)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["STATUT", "CONTACT", "N° FACTURE", "FACTURE TXT", "JUSTIFICATIF JSON"])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(46)
        hv = self.table.horizontalHeader()
        hv.setStretchLastSection(True)
        hv.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)
        return card

    # ---------- données ----------
    def refresh(self, invoices):
        """Met à jour le tableau (en respectant la recherche) et les compteurs."""
        self.invoices = invoices
        self.apply_filter()

        valid = sum(1 for i in invoices if i.get("status") == "VALIDE")
        review = sum(1 for i in invoices if i.get("status") == "À VÉRIFIER")
        anomaly = sum(1 for i in invoices if i.get("status") == "ANOMALIE")

        self.pending_number.setText(str(review))
        self.donut.set_values(valid, review, anomaly)
        self.valid_legend.setText(f"●  Validées : {valid}")
        self.review_legend.setText(f"●  À vérifier : {review}")
        self.anomaly_legend.setText(f"●  Anomalies : {anomaly}")

    def apply_filter(self):
        text = self.search_input.text().strip().lower()
        if not text:
            self.filtered_invoices = self.invoices
        else:
            self.filtered_invoices = [
                inv for inv in self.invoices
                if any(text in str(inv.get(k, "")).lower()
                       for k in ("invoice", "contact", "document", "json"))
            ]
        self._fill_table(self.filtered_invoices)

    def _fill_table(self, invoices):
        self.table.setRowCount(len(invoices))
        for row, inv in enumerate(invoices):
            for col, key in enumerate(("status", "contact", "invoice", "document", "json")):
                item = QTableWidgetItem(inv.get(key, ""))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
        self.count_label.setText(f"{len(invoices)} facture(s)")

    def _on_double_click(self, _item):
        row = self.table.currentRow()
        if 0 <= row < len(self.filtered_invoices):
            self.invoice_opened.emit(self.filtered_invoices[row])
