import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import InvoiceApp

def main():
    app = QApplication(sys.argv)
    win = InvoiceApp()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
