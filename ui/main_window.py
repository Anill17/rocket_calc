"""Ana pencere — 3 sekmeli QMainWindow.

Bölüm A (Mekanizma), B (Yay Tasarımı) ve C (Çalışma Noktaları) sekmelerini
merkezi bir AppState üzerinden birbirine bağlar. Bölüm B'deki k ve L_free
değişince `spring_changed` sinyaliyle A ve C otomatik güncellenir; sekmeler
arası geçişte bayat veri görünmez.
"""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from core.app_state import AppState
from ui.calisma_noktalari_panel import CalismaNoktalariPanel
from ui.mekanizma_panel import MekanizmaPanel
from ui.yay_panel import YayPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yay Tahrikli Roket Fırlatma Hesap Uygulaması")
        self.resize(1200, 800)
        self.setMinimumSize(1100, 750)

        # Merkezi paylaşılan durum (single source of truth)
        self.state = AppState(self)

        # Sekmeler — hepsi aynı AppState'i paylaşır
        self._mekanizma_panel = MekanizmaPanel(self.state)
        self._yay_panel = YayPanel(self.state)
        self._calisma_panel = CalismaNoktalariPanel(self.state)

        tablar = QTabWidget()
        tablar.addTab(self._mekanizma_panel, "Mekanizma Hesabı")
        tablar.addTab(self._yay_panel, "Yay Tasarımı")
        tablar.addTab(self._calisma_panel, "Çalışma Noktaları")
        self.setCentralWidget(tablar)

        # Başlangıçta tüm görünümleri güncel değerlerle doldur
        self.state.ilk_yayin()
