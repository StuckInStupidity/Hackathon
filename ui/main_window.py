from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QMainWindow, QMessageBox, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget,
)

from utils.config import BG, NAVY, WHITE
from services.importer import import_files
from services.verification import verify_pending
from ui.dashboard_page import DashboardPage
from ui.invoice_detail_dialog import InvoiceDetailDialog
from ui.stats_page import StatsPage
from ui.styles import NAV_ACTIVE, NAV_INACTIVE
from ui.widgets import make_label


class InvoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iMSA | Contrôle des factures")
        self.resize(1450, 880)
        self.setMinimumSize(1100, 700)

        self.invoices = []
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_sidebar())

        self.dashboard = DashboardPage()
        self.dashboard.import_requested.connect(self.import_documents)
        self.dashboard.verify_requested.connect(self.proceed_verification)
        self.dashboard.invoice_opened.connect(self.open_invoice_detail)

        self.stats = StatsPage()

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {BG};")
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.stats)
        root.addWidget(self.stack, 1)

        self.set_page(0)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(225)
        sidebar.setStyleSheet(f"background-color: {NAVY}; border: none;")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 25, 20, 22)
        layout.setSpacing(10)

        layout.addWidget(make_label("iMSA", 26, WHITE, True))
        layout.addWidget(make_label("CONTRÔLE DES FACTURES", 9, "#B8C6D9", True))
        layout.addSpacing(30)

        self.nav_dashboard = QPushButton("  ▦    Tableau de bord")
        self.nav_stats = QPushButton("  ▤    Statistiques")
        self.nav_buttons = [self.nav_dashboard, self.nav_stats]
        for index, button in enumerate(self.nav_buttons):
            button.setMinimumHeight(43)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, i=index: self.set_page(i))
            layout.addWidget(button)

        layout.addStretch()
        layout.addWidget(make_label("●  Prototype local", 11, "#B8C6D9"))
        return sidebar

    # ---------- navigation ----------
    def set_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setStyleSheet(NAV_ACTIVE if i == index else NAV_INACTIVE)
        if index == 1:
            self.stats.refresh(self.invoices)

    def refresh_all(self):
        self.dashboard.refresh(self.invoices)
        self.stats.refresh(self.invoices)

    # ---------- actions ----------
    def open_invoice_detail(self, invoice):
        InvoiceDetailDialog(invoice, self, on_validate=self.refresh_all).exec()

    def import_documents(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Importer les documents", "", "Fichiers TXT/JSON (*.txt *.json)")
        if not files:
            return
        import_files(self.invoices, files)
        self.refresh_all()

    def proceed_verification(self):
        processed = verify_pending(self.invoices)
        self.refresh_all()
        if processed == 0:
            QMessageBox.information(
                self, "Vérification",
                "Aucune facture TXT à vérifier avec un fichier JSON associé "
                "portant exactement le même nom.")
