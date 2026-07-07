"""Bölüm B arayüzü — Yay Tasarımı sekmesi (Compression Spring Design).

Sol: girdi spin box'ları. Sağ: canlı güncellenen hesaplanan değerler.
Girdi değişince merkezi AppState güncellenir ve `spring_changed` yayınlanır;
Bölüm A ve C bu sinyale abonedir.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from core.app_state import AppState

# (etiket, alan, min, max, step, ondalık)
GIRDI_TANIMLARI = [
    ("d — Tel çapı (mm)", "d", 0.01, 100.0, 0.1, 2),
    ("OD — Dış çap (mm)", "OD", 0.01, 500.0, 0.1, 2),
    ("L_free — Serbest boy (mm)", "L_free", 0.0, 1000.0, 0.1, 2),
    ("Nt — Toplam sarım", "Nt", 0.0, 200.0, 0.5, 2),
    ("G — Kayma modülü (MPa)", "G", 0.0, 500000.0, 100.0, 1),
    ("tau_allow — İzin verilen gerilme (MPa)", "tau_allow", 0.0, 10000.0, 10.0, 1),
    ("end_coils — Uç sarım sayısı", "end_coils", 0.0, 20.0, 0.5, 2),
]

# (etiket, sonuç alanı, birim)
SONUC_TANIMLARI = [
    ("ID — İç çap", "ID", "mm"),
    ("D — Ortalama çap", "D", "mm"),
    ("C — Yay indeksi", "C", ""),
    ("Na — Aktif sarım", "Na", ""),
    ("k — Yay Sabiti", "k", "N/mm"),
    ("Ls — Tam sıkışma boyu", "Ls", "mm"),
    ("p — Adım (Pitch)", "p", "mm"),
    ("Kw — Wahl Faktörü", "Kw", ""),
    ("F_max_safe — Max Güvenli Yük", "F_max_safe", "N"),
    ("x_max_safe — Max Güvenli Sıkışma", "x_max_safe", "mm"),
]


class YayPanel(QWidget):
    """Yay Tasarımı sekmesi."""

    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self.state = state
        self._spinler: dict[str, QDoubleSpinBox] = {}
        self._sonuc_etiketleri: dict[str, QLabel] = {}
        self._kur_arayuz()
        # Kendi görünümünü de spring_changed üzerinden güncelle (tek yol)
        self.state.spring_changed.connect(self._gorunumu_guncelle)

    def _kur_arayuz(self):
        layout = QHBoxLayout(self)

        # Sol: girdiler
        girdi_grup = QGroupBox("Yay Girdileri")
        girdi_form = QFormLayout(girdi_grup)
        for etiket, alan, mn, mx, step, ond in GIRDI_TANIMLARI:
            spin = QDoubleSpinBox()
            spin.setRange(mn, mx)
            spin.setDecimals(ond)
            spin.setSingleStep(step)
            spin.setValue(getattr(self.state.yay, alan))
            spin.valueChanged.connect(
                lambda deger, a=alan: self._girdi_degisti(a, deger)
            )
            self._spinler[alan] = spin
            girdi_form.addRow(etiket, spin)
        layout.addWidget(girdi_grup, 1)

        # Sağ: sonuçlar + uyarı
        sag = QWidget()
        sag_layout = QVBoxLayout(sag)
        sonuc_grup = QGroupBox("Hesaplanan Değerler")
        sonuc_form = QFormLayout(sonuc_grup)
        for etiket, alan, birim in SONUC_TANIMLARI:
            lbl = QLabel("-")
            self._sonuc_etiketleri[alan] = lbl
            son_etiket = f"{etiket} ({birim}):" if birim else f"{etiket}:"
            sonuc_form.addRow(son_etiket, lbl)
        sag_layout.addWidget(sonuc_grup)

        self._uyari = QLabel("")
        self._uyari.setWordWrap(True)
        self._uyari.setStyleSheet("color: #e74c3c; font-weight: bold;")
        sag_layout.addWidget(self._uyari)
        sag_layout.addStretch(1)
        layout.addWidget(sag, 1)

    def _girdi_degisti(self, alan: str, deger: float):
        setattr(self.state.yay, alan, deger)
        # Merkezi state'i senkronla ve tüm abonelere (A, C ve bu panel) haber ver
        self.state.bildir_yay_degisti()

    def _gorunumu_guncelle(self):
        s = self.state.yay_sonuclari
        degerler = {
            "ID": s.ID, "D": s.D, "C": s.C, "Na": s.Na, "k": s.k,
            "Ls": s.Ls, "p": s.p, "Kw": s.Kw,
            "F_max_safe": s.F_max_safe, "x_max_safe": s.x_max_safe,
        }
        for alan, lbl in self._sonuc_etiketleri.items():
            lbl.setText(f"{degerler[alan]:.3f}")

        # Yay indeksi C uyarısı
        c_lbl = self._sonuc_etiketleri["C"]
        if not s.uretilebilir:
            c_lbl.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self._uyari.setText(
                "⚠ Üretilebilir bir yay için C > 4 olmalı "
                f"(şu an C = {s.C:.3f})."
            )
        else:
            c_lbl.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self._uyari.setText("")
