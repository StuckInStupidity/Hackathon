NAV_ACTIVE = """
    QPushButton {
        text-align: left;
        color: white;
        background: #2C3D59;
        border: none;
        border-radius: 9px;
        padding-left: 10px;
        font-size: 12px;
        font-weight: bold;
    }
"""

NAV_INACTIVE = """
    QPushButton {
        text-align: left;
        color: #B8C6D9;
        background: transparent;
        border: none;
        border-radius: 9px;
        padding-left: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    QPushButton:hover { background: #22324D; color: white; }
"""

SEARCH_INPUT_STYLE = """
    QLineEdit {
        background: white;
        border: 1px solid #E3E8F0;
        border-radius: 9px;
        padding: 0 12px;
        font-size: 11px;
        color: #344054;
    }
    QLineEdit:focus { border: 1px solid #315EFB; }
"""

TABLE_STYLE = """
    QTableWidget {
        background: white;
        alternate-background-color: #F8FAFD;
        color: #344054;
        border: none;
        border-radius: 10px;
        font-size: 12px;
        selection-background-color: #EAF0FF;
        selection-color: #1E293B;
        outline: none;
    }
    QTableWidget::item {
        padding: 10px 8px;
        border-bottom: 1px solid #EEF1F6;
    }
    QTableWidget::item:hover { background: #F0F5FF; }
    QHeaderView::section {
        background: #F8FAFC;
        color: #8490A3;
        border: none;
        border-bottom: 1px solid #E8ECF2;
        padding: 13px 10px;
        font-size: 9px;
        font-weight: bold;
    }
    QScrollBar:vertical {
        background: #F8FAFC;
        width: 8px;
        margin: 2px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background: #D5DDE8;
        min-height: 25px;
        border-radius: 4px;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical { height: 0px; }
"""
