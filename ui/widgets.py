from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QProgressBar,
    QPushButton, QTableWidget, QTableWidgetItem, QWidget,
)

from utils.config import RED, TEXT
from ui.styles import TABLE_STYLE


def make_label(text, size=12, color=TEXT, bold=False):
    label = QLabel(text)
    label.setStyleSheet(
        f"""
        color: {color};
        font-size: {size}px;
        font-weight: {"bold" if bold else "normal"};
        background-color: transparent;
        """
    )
    return label


def make_button(text, primary=False):
    button = QPushButton(text)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setMinimumHeight(40)

    if primary:
        button.setStyleSheet(
            """
            QPushButton {
                background-color: #315EFB;
                color: white;
                border: none;
                border-radius: 9px;
                padding: 10px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #244DE0; }
            QPushButton:pressed { background-color: #1D40C2; }
            QPushButton:disabled {
                background-color: #AAB8E8;
                color: #F5F7FF;
            }
            """
        )
    else:
        button.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                color: #344054;
                border: 1px solid #E2E7EF;
                border-radius: 9px;
                padding: 9px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F4F7FC;
                border-color: #CCD5E3;
            }
            """
        )
    return button


def make_card():
    card = QFrame()
    card.setObjectName("card")
    card.setStyleSheet(
        """
        QFrame#card {
            background-color: white;
            border: 1px solid #E8ECF2;
            border-radius: 14px;
        }
        """
    )
    return card


def make_bar(ratio):
    container = QWidget()
    container.setStyleSheet("background: transparent;")
    layout = QHBoxLayout(container)
    layout.setContentsMargins(8, 0, 8, 0)
    bar = QProgressBar()
    bar.setRange(0, 1000)
    bar.setValue(int(max(0.0, min(1.0, ratio)) * 1000))
    bar.setTextVisible(False)
    bar.setFixedHeight(8)
    bar.setStyleSheet(
        f"""
        QProgressBar {{ background: #EEF1F6; border: none; border-radius: 4px; }}
        QProgressBar::chunk {{ background: {RED}; border-radius: 4px; }}
        """
    )
    layout.addWidget(bar)
    return container


def make_ranking_table(headers, stretch_col=0):
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setWordWrap(False)
    table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(44)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)
    header = table.horizontalHeader()
    header.setFixedHeight(40)
    for col in range(len(headers)):
        header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)
    last = len(headers) - 1
    header.setSectionResizeMode(last, QHeaderView.ResizeMode.Fixed)
    header.resizeSection(last, 160)
    table.setStyleSheet(TABLE_STYLE)
    return table


def fill_ranking_table(table, rows):
    table.setRowCount(len(rows))
    table.setFixedHeight(40 + max(len(rows), 3) * 44 + 4)
    bar_col = table.columnCount() - 1
    for r, (cells, ratio) in enumerate(rows):
        for c, value in enumerate(cells):
            item = QTableWidgetItem(str(value))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if c == 0:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setToolTip(str(value))
            else:
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                )
            table.setItem(r, c, item)
        table.setCellWidget(r, bar_col, make_bar(ratio))
