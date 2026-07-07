"""Uygulama girişi — QApplication başlatma.

Yay Tahrikli Roket Fırlatma Mekanizması Hesap Uygulaması (PySide6).
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow

# Sade/modern koyu tema (mühendislik yazılımı hissi)
QSS = """
QWidget { font-size: 13px; }
QGroupBox {
    font-weight: bold;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QLabel#ozet {
    font-weight: bold;
    padding: 6px;
    background: #2c3e50;
    border-radius: 4px;
}
QDoubleSpinBox { padding: 2px 4px; }
QTableWidget { gridline-color: #3d3d3d; }
"""


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("RoketFirlatmaHesap")
    app.setStyleSheet(QSS)

    pencere = MainWindow()
    pencere.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
