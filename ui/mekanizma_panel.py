"""Bölüm A arayüzü — Mekanizma Hesabı sekmesi.

Sol: sabit girdi paneli. Orta/sağ: animasyonlu diyagram + ALFA slider'ı.
Alt: ALFA sweep sonuç tablosu.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.app_state import AppState
from core.mekanizma_hesap import (
    AYRILMA_ESIGI,
    hesapla_sweep,
    hesapla_tek_nokta,
)
from ui.mekanizma_widget import MekanizmaWidget

# (etiket, alan adı, min, max, step) — sabit girdiler
GIRDI_TANIMLARI = [
    ("KE (=BA) — Yay Kolu Alt Kol (mm)", "KE", 0.0, 1000.0, 0.1),
    ("KT — Yay Kolu Üst Kol (mm)", "KT", 0.0, 1000.0, 0.1),
    ("TM kulakları (mm)", "TM_kulaklari", 0.0, 1000.0, 0.1),
    ("AE — Ara bağlantı kolu (mm)", "AE", 0.0, 1000.0, 0.1),
    ("TETA (derece)", "TETA_derece", 0.0, 360.0, 0.5),
    ("Mx — M noktası X", "Mx", -1000.0, 1000.0, 0.5),
    ("My — M noktası Y", "My", -1000.0, 1000.0, 0.5),
    ("F_roket — Roket kuvveti (N)", "F_roket", 0.0, 100000.0, 1.0),
    ("KONTROL_ALFA (derece)", "KONTROL_ALFA", 0.0, 360.0, 0.5),
]

# Tablo sütunları
TABLO_BASLIKLAR = [
    "ALFA(°)",
    "BETA(°)",
    "Kalkış Mes.",
    "Füze Durumu",
    "Yay Kuvveti",
    "Yay Momenti",
    "Net Kuvvet",
]

ALFA_MIN = 0.0
ALFA_MAX = 60.5
ALFA_STEP = 0.5
SLIDER_OLCEK = 10  # 0.5° hassasiyet için slider değeri x10 tutulur


class MekanizmaPanel(QWidget):
    """Mekanizma Hesabı sekmesi."""

    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self.state = state
        self._spinler: dict[str, QDoubleSpinBox] = {}
        self._son_sweep = None
        self._kur_arayuz()
        # Merkezi state'e abone ol: Bölüm B (yay) veya Bölüm A sabit girdileri
        # değişince sweep, grafik, tablo ve diyagram yeniden hesaplanır.
        self.state.spring_changed.connect(self.yeniden_hesapla)
        self.state.mechanism_changed.connect(self.yeniden_hesapla)
        self.yeniden_hesapla()

    @property
    def params(self):
        """Merkezi state'teki mekanizma girdileri (k / L_free senkron)."""
        return self.state.mekanizma

    # ---- Arayüz kurulumu -------------------------------------------------
    def _kur_arayuz(self):
        dis_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        dis_layout.addWidget(splitter)

        # Sol: sabit girdi paneli
        sol = QWidget()
        sol_layout = QVBoxLayout(sol)
        grup = QGroupBox("Sabit Girdiler")
        form = QFormLayout(grup)
        for etiket, alan, mn, mx, step in GIRDI_TANIMLARI:
            spin = QDoubleSpinBox()
            spin.setRange(mn, mx)
            spin.setDecimals(2)
            spin.setSingleStep(step)
            spin.setValue(getattr(self.params, alan))
            spin.valueChanged.connect(self._girdi_degisti)
            self._spinler[alan] = spin
            form.addRow(etiket, spin)
        sol_layout.addWidget(grup)

        # Anlık tek-nokta sonuç paneli (slider'a bağlı)
        self._anlik_grup = QGroupBox("Anlık Değerler (slider)")
        anlik_form = QFormLayout(self._anlik_grup)
        self._lbl_alfa = QLabel("-")
        self._lbl_kalkis = QLabel("-")
        self._lbl_durum = QLabel("-")
        self._lbl_yay_k = QLabel("-")
        self._lbl_net = QLabel("-")
        anlik_form.addRow("ALFA (°):", self._lbl_alfa)
        anlik_form.addRow("Kalkış Mesafesi:", self._lbl_kalkis)
        anlik_form.addRow("Füze Durumu:", self._lbl_durum)
        anlik_form.addRow("Yay Kuvveti (N):", self._lbl_yay_k)
        anlik_form.addRow("Net Kuvvet (N):", self._lbl_net)
        sol_layout.addWidget(self._anlik_grup)
        sol_layout.addStretch(1)
        splitter.addWidget(sol)

        # Sağ: üst (diyagram + slider), alt (tablo + grafik)
        sag = QWidget()
        sag_layout = QVBoxLayout(sag)

        self._ozet_etiket = QLabel("-")
        self._ozet_etiket.setObjectName("ozet")
        sag_layout.addWidget(self._ozet_etiket)

        dik_splitter = QSplitter(Qt.Vertical)
        sag_layout.addWidget(dik_splitter, 1)

        # Üst: diyagram + slider
        ust = QWidget()
        ust_layout = QVBoxLayout(ust)
        self._diyagram = MekanizmaWidget()
        ust_layout.addWidget(self._diyagram, 1)

        slider_satir = QHBoxLayout()
        slider_satir.addWidget(QLabel(f"ALFA: {ALFA_MIN:g}°"))
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(int(ALFA_MIN * SLIDER_OLCEK))
        self._slider.setMaximum(int(ALFA_MAX * SLIDER_OLCEK))
        self._slider.setValue(int(ALFA_MIN * SLIDER_OLCEK))
        self._slider.valueChanged.connect(self._slider_degisti)
        slider_satir.addWidget(self._slider, 1)
        slider_satir.addWidget(QLabel(f"{ALFA_MAX:g}°"))
        ust_layout.addLayout(slider_satir)
        dik_splitter.addWidget(ust)

        # Alt: ALFA sweep sonuç tablosu (grafik kaldırıldı)
        self._tablo = QTableWidget(0, len(TABLO_BASLIKLAR))
        self._tablo.setHorizontalHeaderLabels(TABLO_BASLIKLAR)
        self._tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tablo.verticalHeader().setDefaultSectionSize(22)
        dik_splitter.addWidget(self._tablo)
        dik_splitter.setSizes([400, 350])

        splitter.addWidget(sag)
        splitter.setSizes([320, 900])

    # ---- Girdi değişimleri ----------------------------------------------
    def _girdi_degisti(self):
        for alan, spin in self._spinler.items():
            setattr(self.state.mekanizma, alan, spin.value())
        # Merkezi state üzerinden bildir: bu panel (ve diğer aboneler) güncellenir.
        self.state.bildir_mekanizma_degisti()

    def yeniden_hesapla(self):
        """Tüm sweep tablosunu, grafiği ve anlık paneli günceller."""
        sweep = hesapla_sweep(self.params, ALFA_MIN, ALFA_MAX, ALFA_STEP)
        self._son_sweep = sweep
        self._tabloyu_doldur(sweep)

        if sweep.ayrilma_alfa is not None:
            self._ozet_etiket.setText(
                f"Füze ALFA = {sweep.ayrilma_alfa:g}°'de ayrılıyor "
                f"(eşik {AYRILMA_ESIGI} mm)."
            )
        else:
            self._ozet_etiket.setText(
                "Bu aralıkta füze ayrılmıyor (kalkış mesafesi eşiğe ulaşmıyor)."
            )
        self._slider_degisti()

    def _tabloyu_doldur(self, sweep):
        satirlar = [
            (
                sweep.alfa_deg,
                sweep.BETA,
                sweep.kalkis_mesafesi,
                sweep.fuze_durumu,
                sweep.yay_kuvveti,
                sweep.yay_momenti,
                sweep.net_kuvvet,
            )
        ]
        n = len(sweep.alfa_deg)
        self._tablo.setRowCount(n)
        vurgu_yapildi = False
        for i in range(n):
            deger_hucreleri = [
                f"{sweep.alfa_deg[i]:.1f}",
                f"{sweep.BETA[i]:.3f}",
                f"{sweep.kalkis_mesafesi[i]:.3f}",
                sweep.fuze_durumu[i],
                f"{sweep.yay_kuvveti[i]:.3f}",
                f"{sweep.yay_momenti[i]:.3f}",
                f"{sweep.net_kuvvet[i]:.3f}",
            ]
            ilk_ayrilma = (
                not vurgu_yapildi and sweep.fuze_durumu[i] == "AYRILDI"
            )
            for j, metin in enumerate(deger_hucreleri):
                item = QTableWidgetItem(metin)
                if ilk_ayrilma:
                    item.setBackground(QColor(120, 40, 40))
                self._tablo.setItem(i, j, item)
            if ilk_ayrilma:
                vurgu_yapildi = True

    # ---- Slider (tek-nokta anlık hesap) ---------------------------------
    def _slider_degisti(self):
        alfa = self._slider.value() / SLIDER_OLCEK
        d = hesapla_tek_nokta(alfa, self.params)
        ayrildi = d["fuze_durumu"] == "AYRILDI"

        self._diyagram.guncelle(self.params, alfa, ayrildi)

        self._lbl_alfa.setText(f"{alfa:.1f}")
        self._lbl_kalkis.setText(f"{d['kalkis_mesafesi']:.3f}")
        self._lbl_durum.setText(d["fuze_durumu"])
        self._lbl_durum.setStyleSheet(
            "color: #e74c3c; font-weight: bold;"
            if ayrildi
            else "color: #2ecc71; font-weight: bold;"
        )
        self._lbl_yay_k.setText(f"{d['yay_kuvveti']:.3f}")
        self._lbl_net.setText(f"{d['net_kuvvet']:.3f}")
