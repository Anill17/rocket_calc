"""PyQtGraph tabanlı animasyonlu mekanizma diyagramı widget'ı.

B-A-E-K-T-M noktalarını çizgilerle birleştirir. T noktası ALFA'ya bağlı
olarak hareket eder; Füze Durumu "AYRILDI" olduğunda görsel uyarı verir.
"""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from core.mekanizma_hesap import MekanizmaGirdileri, hesapla_geometri_noktalari

# Kolların (bağlantı çizgilerinin) noktaları
KOL_BAGLANTILARI = [
    ("B", "A"),
    ("A", "E"),
    ("E", "K"),
    ("K", "T"),
    ("T", "M"),
]

RENK_ITIYOR = (46, 204, 113)   # yeşil
RENK_AYRILDI = (231, 76, 60)   # kırmızı


class MekanizmaWidget(pg.PlotWidget):
    """Mekanizmanın 2D animasyonlu şeması."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground("#1e1e1e")
        self.setAspectLocked(True)
        self.showGrid(x=True, y=True, alpha=0.2)
        self.getPlotItem().setLabel("bottom", "X (mm)")
        self.getPlotItem().setLabel("left", "Y (mm)")
        self.getPlotItem().setTitle("Mekanizma Diyagramı")

        # Kollar (bağlantı çizgileri)
        self._kol_cizgi = self.plot(
            [], [], pen=pg.mkPen("#dddddd", width=2.5), connect="pairs"
        )

        # Sabit pivot/anchor noktaları (B, K, M)
        self._sabit_noktalar = pg.ScatterPlotItem(
            size=12, brush=pg.mkBrush("#3498db"), pen=pg.mkPen("w", width=1)
        )
        self.addItem(self._sabit_noktalar)

        # Hareketli E ve A noktaları (K etrafında alfa ile döner)
        self._hareketli_noktalar = pg.ScatterPlotItem(
            size=13, brush=pg.mkBrush("#f39c12"), pen=pg.mkPen("w", width=1.2)
        )
        self.addItem(self._hareketli_noktalar)

        # Hareketli T noktası (durum rengine göre yeşil/kırmızı)
        self._t_nokta = pg.ScatterPlotItem(
            size=16, brush=pg.mkBrush(*RENK_ITIYOR), pen=pg.mkPen("w", width=1.5)
        )
        self.addItem(self._t_nokta)

        # Nokta etiketleri
        self._etiketler: dict[str, pg.TextItem] = {}
        for isim in ("B", "A", "E", "K", "T", "M"):
            t = pg.TextItem(isim, color="#ffffff", anchor=(0.5, 1.4))
            self.addItem(t)
            self._etiketler[isim] = t

    def guncelle(self, params: MekanizmaGirdileri, alfa_deg: float, ayrildi: bool):
        """Verilen ALFA açısına göre diyagramı yeniden çizer."""
        noktalar = hesapla_geometri_noktalari(params, alfa_deg)

        # Kolları çiz (connect="pairs": ardışık nokta çiftleri arasında çizgi)
        xs, ys = [], []
        for a, b in KOL_BAGLANTILARI:
            xs += [noktalar[a][0], noktalar[b][0]]
            ys += [noktalar[a][1], noktalar[b][1]]
        self._kol_cizgi.setData(xs, ys)

        # Sabit pivot/anchor noktaları (B, K, M)
        sabit = [noktalar[k] for k in ("B", "K", "M")]
        self._sabit_noktalar.setData(
            [pt[0] for pt in sabit], [pt[1] for pt in sabit]
        )

        # Hareketli E, A noktaları
        hareketli = [noktalar[k] for k in ("E", "A")]
        self._hareketli_noktalar.setData(
            [pt[0] for pt in hareketli], [pt[1] for pt in hareketli]
        )

        # T noktası — durum rengine göre
        renk = RENK_AYRILDI if ayrildi else RENK_ITIYOR
        self._t_nokta.setBrush(pg.mkBrush(*renk))
        self._t_nokta.setData([noktalar["T"][0]], [noktalar["T"][1]])

        # Arka plan uyarısı
        self.setBackground("#3a1e1e" if ayrildi else "#1e1e1e")

        # Etiket konumları
        for isim, t in self._etiketler.items():
            t.setPos(*noktalar[isim])
