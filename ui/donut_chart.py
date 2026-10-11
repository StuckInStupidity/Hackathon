from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget
from utils.config import GREEN, MUTED, RED, TEXT


class DonutChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.valid_count = 0
        self.review_count = 0
        self.anomaly_count = 0
        self.setMinimumSize(145, 145)
        self.setMaximumSize(165, 165)

    def set_values(self, valid, review, anomaly):
        self.valid_count = valid
        self.review_count = review
        self.anomaly_count = anomaly
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        total = self.valid_count + self.review_count + self.anomaly_count
        rect = QRectF(17, 17, 111, 111)
        start_angle = 90 * 16
        span_total = 360 * 16

        if total == 0:
            painter.setPen(QPen(QColor("#E9EDF4"), 13))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(rect)
        else:
            values = [
                (self.valid_count, GREEN),
                (self.review_count, "#E7A23B"),
                (self.anomaly_count, RED),
            ]
            for value, color in values:
                if value <= 0:
                    continue
                span = int(span_total * value / total)
                painter.setPen(QPen(QColor(color), 13, Qt.PenStyle.SolidLine,
                                    Qt.PenCapStyle.FlatCap))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawArc(rect, start_angle, -span)
                start_angle -= span

        painter.setPen(QColor(TEXT))
        painter.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        painter.drawText(QRectF(25, 45, 95, 30), Qt.AlignmentFlag.AlignCenter, str(total))
        painter.setPen(QColor(MUTED))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(QRectF(25, 72, 95, 20), Qt.AlignmentFlag.AlignCenter, "FACTURES")
