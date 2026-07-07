"""Bölüm C arayüzü — Çalışma Noktaları sekmesi.

İki bağımsız kart (yan yana):
  1. Yüklü Boy verildiğinde yük hesabı.
  2. Hedef Yük verildiğinde boy hesabı.
Her iki kart merkezi AppState'ten k (Yay Sabiti) ve L_free (Serbest Boy) okur;
`spring_changed` sinyaline abonedir, dolayısıyla bu sekme açık olmasa bile
Bölüm B değiştiğinde arka planda güncellenir (bayat veri kalmaz).
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from core.app_state import AppState


class CalismaNoktalariPanel(QWidget):
    """Çalışma Noktaları sekmesi."""

    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self.state = state
        self._kur_arayuz()
        # Bölüm B değişince (sekme kapalı olsa bile) arka planda güncelle
        self.state.spring_changed.connect(self.yeniden_hesapla)

    def _kur_arayuz(self):
        layout = QHBoxLayout(self)

        # --- Kart 1: Yüklü Boy -> Yük ---
        kart1 = QGroupBox("Girdi 1 — Yüklü Boy verildiğinde Yük")
        f1 = QFormLayout(kart1)
        self._loaded_height = QDoubleSpinBox()
        self._loaded_height.setRange(0.0, 1000.0)
        self._loaded_height.setDecimals(3)
        self._loaded_height.setSingleStep(0.1)
        self._loaded_height.setValue(37.0)
        self._loaded_height.valueChanged.connect(self.yeniden_hesapla)
        f1.addRow("Loaded Height — Yüklü Boy (mm):", self._loaded_height)
        self._lbl_yuk = QLabel("-")
        self._lbl_defl1 = QLabel("-")
        f1.addRow("Hesaplanan Yük (N):", self._lbl_yuk)
        f1.addRow("Deflection (mm):", self._lbl_defl1)
        layout.addWidget(kart1, 1)

        # --- Kart 2: Hedef Yük -> Boy ---
        kart2 = QGroupBox("Girdi 2 — Hedef Yük verildiğinde Boy")
        f2 = QFormLayout(kart2)
        self._hedef_yuk = QDoubleSpinBox()
        self._hedef_yuk.setRange(0.0, 100000.0)
        self._hedef_yuk.setDecimals(3)
        self._hedef_yuk.setSingleStep(1.0)
        self._hedef_yuk.setValue(150.0)
        self._hedef_yuk.valueChanged.connect(self.yeniden_hesapla)
        f2.addRow("Hedef Yük (N):", self._hedef_yuk)
        self._lbl_boy = QLabel("-")
        self._lbl_defl2 = QLabel("-")
        f2.addRow("Hesaplanan Yüklü Boy (mm):", self._lbl_boy)
        f2.addRow("Deflection (mm):", self._lbl_defl2)
        layout.addWidget(kart2, 1)

    def yeniden_hesapla(self):
        k = self.state.k
        L_free = self.state.L_free

        # Kart 1: Yük = k * (L_free - Loaded_Height)
        loaded = self._loaded_height.value()
        defl1 = L_free - loaded
        yuk = k * defl1
        self._lbl_yuk.setText(f"{yuk:.3f}")
        self._lbl_defl1.setText(f"{defl1:.3f}")

        # Kart 2: Yüklü Boy = L_free - (Hedef_Yuk / k)
        hedef = self._hedef_yuk.value()
        if k != 0:
            defl2 = hedef / k
            boy = L_free - defl2
            self._lbl_boy.setText(f"{boy:.3f}")
            self._lbl_defl2.setText(f"{defl2:.3f}")
        else:
            self._lbl_boy.setText("-")
            self._lbl_defl2.setText("-")
