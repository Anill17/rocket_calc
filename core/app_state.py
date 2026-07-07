"""Merkezi uygulama durumu (shared state).

Paneller bağımsız değildir; aralarında veri bağımlılığı vardır. Bu sınıf tek
gerçek kaynak (single source of truth) olarak Bölüm A (mekanizma) ve Bölüm B
(yay) girdilerini tutar; `k` ve `L_free` computed property'dir.

Bağımlılıklar:
  - Bölüm B değişince -> `spring_changed` sinyali -> Bölüm A (sweep/grafik/AYRILDI)
    ve Bölüm C (yük/boy) yeniden hesaplanır. Bölüm A'nın YAY_SABITI_k ve
    YAY_SARMAL_BOYU alanları buradan senkronlanır, böylece hiç bayat veri kalmaz.
  - Bölüm A sabit girdileri değişince -> `mechanism_changed` sinyali.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from core.mekanizma_hesap import MekanizmaGirdileri
from core.yay_hesap import YayGirdileri, YaySonuclari, hesapla_yay


class AppState(QObject):
    """Tüm panellerin paylaştığı merkezi durum."""

    # Bölüm B girdileri (dolayısıyla k / L_free) değişti
    spring_changed = Signal()
    # Bölüm A sabit girdileri (KE, KT, Mx, ...) değişti
    mechanism_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._yay = YayGirdileri()
        self._mek = MekanizmaGirdileri()
        self._spring_senkron()  # _mek'in yay alanlarını başta doldur

    # ---- Girdi nesnelerine erişim ---------------------------------------
    @property
    def yay(self) -> YayGirdileri:
        return self._yay

    @property
    def mekanizma(self) -> MekanizmaGirdileri:
        return self._mek

    # ---- Computed property'ler ------------------------------------------
    @property
    def yay_sonuclari(self) -> YaySonuclari:
        """Bölüm B girdilerinden hesaplanan güncel yay değerleri."""
        return hesapla_yay(self._yay)

    @property
    def k(self) -> float:
        """Yay Sabiti (Spring Rate, N/mm) — Bölüm A'daki YAY_SABITI_k."""
        return self.yay_sonuclari.k

    @property
    def L_free(self) -> float:
        """Serbest Boy (mm) — Bölüm A'daki YAY_SARMAL_BOYU."""
        return self._yay.L_free

    # ---- Senkronizasyon --------------------------------------------------
    def _spring_senkron(self):
        """Bölüm A'nın yay bağımlı alanlarını Bölüm B'den güncel tutar."""
        self._mek.YAY_SABITI_k = self.k
        self._mek.YAY_SARMAL_BOYU = self.L_free

    # ---- Değişiklik bildirimleri (panellerden çağrılır) -----------------
    def bildir_yay_degisti(self):
        """Bölüm B'de bir girdi değişti: senkronla ve abonelere haber ver."""
        self._spring_senkron()
        self.spring_changed.emit()

    def bildir_mekanizma_degisti(self):
        """Bölüm A sabit girdilerinden biri değişti: abonelere haber ver."""
        self.mechanism_changed.emit()

    def ilk_yayin(self):
        """Başlangıçta tüm görünümleri güncel değerlerle doldurmak için."""
        self._spring_senkron()
        self.spring_changed.emit()
        self.mechanism_changed.emit()
