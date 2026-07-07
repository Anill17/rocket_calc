"""Bölüm A — Mekanizma Hesabı (ALFA sweep + tek-nokta hesabı).

Dönen kolun (ALFA açısı) fonksiyonu olarak yay kuvveti, yay momenti,
net kuvvet ve füze durumunu hesaplar. Excel (KC_S_Hesap.xlsx) I5:S126
satırlarından birebir çevrilmiştir.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

# Füzenin "AYRILDI" sayıldığı kalkış mesafesi eşiği (mm)
AYRILMA_ESIGI = 3.2


@dataclass
class MekanizmaGirdileri:
    """Bölüm A sabit girdileri (varsayılan değerlerle)."""

    KE: float = 10.0          # Yay Kolu Alt Kol uzunluğu (mm) — BA = KE
    KT: float = 15.0          # Yay Kolu Üst Kol uzunluğu (mm)
    TM_kulaklari: float = 8.4  # TM kolu kulakları toplamı (mm)
    AE: float = 20.0          # Ara bağlantı kolu uzunluğu (mm)
    TETA_derece: float = 120.0  # Teta açısı (derece) — sabit montaj açısı
    Mx: float = 53.0          # M noktası X koordinatı
    My: float = -1.0          # M noktası Y koordinatı
    F_roket: float = 150.0    # Roket kuvveti (N) — referans değeri
    KONTROL_ALFA: float = 22.0  # Kontrol alfa açısı (derece)

    # Bölüm B'den beslenen türetilmiş sabitler:
    YAY_SABITI_k: float = 0.0     # Yay Sabiti (Spring Rate, N/mm)
    YAY_SARMAL_BOYU: float = 0.0  # Serbest Boy (Free Length, mm)

    @property
    def BA(self) -> float:
        """Excel'de C4 = C5, yani BA = KE."""
        return self.KE


def hesapla_tek_nokta(alfa_deg: float, p: MekanizmaGirdileri) -> dict:
    """Tek bir ALFA açısı için tüm değerleri hesaplar (slider için hafif).

    Sweep tablosunu yeniden hesaplamak yerine slider her hareket ettiğinde
    yalnızca bu fonksiyon çağrılır.
    """
    alfa_rad = math.radians(alfa_deg)

    # Tx, Ty: KT kolunun ucunun (T noktası) X, Y koordinatları
    aci = math.radians(270 - alfa_deg + p.TETA_derece)
    Tx = p.KT * math.cos(aci)
    Ty = p.KT * math.sin(aci)

    # BETA açısı (hareketli) — M noktasına göre T noktasının açısal konumu
    BETA = math.degrees(
        math.atan2(
            -Tx * (p.Mx - Tx) - Ty * (p.My - Ty),
            -Tx * (p.My - Ty) + Ty * (p.Mx - Tx),
        )
    ) % 360

    # Kalkış Mesafesi (lineer hareket, KE koluna bağlı)
    kalkis_mesafesi = p.KE * (1 - math.cos(alfa_rad))

    # Füze Durumu (eşik: 3.2 mm)
    fuze_durumu = "AYRILDI" if kalkis_mesafesi >= AYRILMA_ESIGI else "ITIYOR"

    # Anlık Yay Boyu (T noktasından M noktasına olan mesafe, eksi kulak boyu)
    anlik_yay_boyu = math.sqrt((p.Mx - Tx) ** 2 + (p.My - Ty) ** 2) - p.TM_kulaklari

    # Yay Kuvveti (Hooke kanunu: k * sıkışma miktarı)
    yay_kuvveti = p.YAY_SABITI_k * (p.YAY_SARMAL_BOYU - anlik_yay_boyu)

    # Yay Momenti (kuvvet kolu * moment kolu farkı)
    payda_moment = anlik_yay_boyu + p.TM_kulaklari
    if payda_moment != 0:
        yay_momenti = (yay_kuvveti / payda_moment) * (Ty * p.Mx - Tx * p.My)
    else:
        yay_momenti = float("nan")

    # Net Kuvvet (moment / kol uzunluğu * cos(alfa))
    payda_net = p.KE * math.cos(alfa_rad)
    net_kuvvet = yay_momenti / payda_net if payda_net != 0 else float("nan")

    return {
        "alfa_deg": alfa_deg,
        "alfa_rad": alfa_rad,
        "BETA": BETA,
        "kalkis_mesafesi": kalkis_mesafesi,
        "fuze_durumu": fuze_durumu,
        "Tx": Tx,
        "Ty": Ty,
        "anlik_yay_boyu": anlik_yay_boyu,
        "yay_kuvveti": yay_kuvveti,
        "yay_momenti": yay_momenti,
        "net_kuvvet": net_kuvvet,
    }


@dataclass
class SweepSonucu:
    """ALFA sweep için vektörel sonuçlar (grafik ve tablo için)."""

    alfa_deg: np.ndarray
    alfa_rad: np.ndarray
    BETA: np.ndarray
    kalkis_mesafesi: np.ndarray
    fuze_durumu: list = field(default_factory=list)
    Tx: np.ndarray = None
    Ty: np.ndarray = None
    anlik_yay_boyu: np.ndarray = None
    yay_kuvveti: np.ndarray = None
    yay_momenti: np.ndarray = None
    net_kuvvet: np.ndarray = None
    ayrilma_alfa: float = None  # İlk "AYRILDI" açısı (derece), yoksa None


def hesapla_sweep(
    p: MekanizmaGirdileri,
    alfa_min: float = 0.0,
    alfa_max: float = 60.5,
    step: float = 0.5,
) -> SweepSonucu:
    """ALFA aralığı boyunca tüm sütunları numpy ile vektörel hesaplar."""
    # np.arange kayan nokta hatalarına karşı: son değeri dahil etmek için
    n = int(round((alfa_max - alfa_min) / step)) + 1
    alfa_deg = alfa_min + step * np.arange(n)
    alfa_rad = np.radians(alfa_deg)

    aci = np.radians(270 - alfa_deg + p.TETA_derece)
    Tx = p.KT * np.cos(aci)
    Ty = p.KT * np.sin(aci)

    BETA = np.degrees(
        np.arctan2(
            -Tx * (p.Mx - Tx) - Ty * (p.My - Ty),
            -Tx * (p.My - Ty) + Ty * (p.Mx - Tx),
        )
    ) % 360

    kalkis_mesafesi = p.KE * (1 - np.cos(alfa_rad))

    fuze_durumu = [
        "AYRILDI" if km >= AYRILMA_ESIGI else "ITIYOR" for km in kalkis_mesafesi
    ]

    anlik_yay_boyu = np.sqrt((p.Mx - Tx) ** 2 + (p.My - Ty) ** 2) - p.TM_kulaklari
    yay_kuvveti = p.YAY_SABITI_k * (p.YAY_SARMAL_BOYU - anlik_yay_boyu)

    payda_moment = anlik_yay_boyu + p.TM_kulaklari
    with np.errstate(divide="ignore", invalid="ignore"):
        yay_momenti = np.where(
            payda_moment != 0,
            (yay_kuvveti / payda_moment) * (Ty * p.Mx - Tx * p.My),
            np.nan,
        )
        payda_net = p.KE * np.cos(alfa_rad)
        net_kuvvet = np.where(payda_net != 0, yay_momenti / payda_net, np.nan)

    # İlk "AYRILDI" açısını bul
    ayrilma_idx = np.argmax(kalkis_mesafesi >= AYRILMA_ESIGI)
    if kalkis_mesafesi[ayrilma_idx] >= AYRILMA_ESIGI:
        ayrilma_alfa = float(alfa_deg[ayrilma_idx])
    else:
        ayrilma_alfa = None

    return SweepSonucu(
        alfa_deg=alfa_deg,
        alfa_rad=alfa_rad,
        BETA=BETA,
        kalkis_mesafesi=kalkis_mesafesi,
        fuze_durumu=fuze_durumu,
        Tx=Tx,
        Ty=Ty,
        anlik_yay_boyu=anlik_yay_boyu,
        yay_kuvveti=yay_kuvveti,
        yay_momenti=yay_momenti,
        net_kuvvet=net_kuvvet,
        ayrilma_alfa=ayrilma_alfa,
    )


def hesapla_geometri_noktalari(p: MekanizmaGirdileri, alfa_deg: float) -> dict:
    """Mekanizma diyagramı için B, A, E, K, T, M noktalarını döndürür.

    B, K, M sabit pivot/anchor noktalarıdır. E, A, T ise aynı ALFA değişkenine
    bağlı olarak K etrafında dönen hareketli noktalardır:
      - E ve A, K etrafında alfa açısıyla döner; B-A-E-K bir paralelkenar
        mekanizması olduğundan BA her zaman KE'ye paralel kalır.
      - T, aynı alfa'ya bağlı ama TETA sabit ofsetli farklı açısal formülle döner.

    Not: E ve A artık KONTROL_ALFA'ya değil, canlı `alfa_deg` (slider) değerine
    bağlıdır — böylece slider hareket ettikçe E, A ve T birlikte animasyon yapar.
    """
    a = math.radians(alfa_deg)

    B = (-p.AE, 0.0)                                    # sabit pivot
    K = (0.0, 0.0)                                      # sabit pivot
    M = (p.Mx, p.My)                                    # sabit anchor

    # Hareketli noktalar (K etrafında alfa ile döner)
    E = (-p.KE * math.sin(a), -p.KE * math.cos(a))
    A = (-p.AE - p.KE * math.sin(a), -p.KE * math.cos(a))

    aci = math.radians(270 - alfa_deg + p.TETA_derece)
    T = (p.KT * math.cos(aci), p.KT * math.sin(aci))

    return {"B": B, "A": A, "E": E, "K": K, "T": T, "M": M}


def hesapla_TM_referans(p: MekanizmaGirdileri) -> float:
    """TM (Yay Kolu uzunluğu, referans) = alfa=0 anındaki T-M mesafesi."""
    d = hesapla_tek_nokta(0.0, p)
    return math.sqrt((p.Mx - d["Tx"]) ** 2 + (p.My - d["Ty"]) ** 2)
