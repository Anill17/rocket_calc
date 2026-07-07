"""Bölüm B — Yay Tasarım Hesaplayıcısı (Compression Spring Design).

Basma yayının mekanik tasarım hesaplarını yapar. Excel (KC_S_Hesap.xlsx)
formüllerinden birebir çevrilmiştir.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class YayGirdileri:
    """Bölüm B kullanıcı girdileri (varsayılan değerlerle)."""

    d: float = 1.6          # Tel çapı — Wire Diameter (mm)
    OD: float = 7.8         # Dış çap — Outer Diameter (mm)
    L_free: float = 40.8    # Serbest boy — Free Length (mm)
    Nt: float = 17          # Toplam sarım sayısı — Total Coils
    G: float = 79240        # Kayma modülü — Shear Modulus (MPa)
    tau_allow: float = 940  # İzin verilen kayma gerilmesi (MPa)
    end_coils: float = 2    # Uç tipi için çıkarılacak sarım sayısı


@dataclass
class YaySonuclari:
    """Bölüm B hesaplanan değerler."""

    ID: float           # İç çap (mm)
    D: float            # Ortalama çap — Mean Diameter (mm)
    C: float            # Yay indeksi — Spring Index
    Na: float           # Aktif sarım sayısı — Active Coils
    k: float            # Yay Sabiti — Spring Rate (N/mm)
    Ls: float           # Tam sıkışma boyu — Solid Height (mm)
    p: float            # Adım — Pitch (mm)
    Kw: float           # Wahl Faktörü
    F_max_safe: float   # Max Güvenli Yük (N)
    x_max_safe: float   # Max Güvenli Sıkışma (mm)
    uretilebilir: bool  # C > 4 ise True


def hesapla_yay(g: YayGirdileri) -> YaySonuclari:
    """Yay tasarım değerlerini hesaplar."""
    ID = g.OD - 2 * g.d
    D = g.OD - g.d
    C = D / g.d if g.d != 0 else float("inf")

    Na = g.Nt - g.end_coils

    # Yay Sabiti (Spring Rate) [N/mm]
    if D != 0 and Na != 0:
        k = (g.G * g.d ** 4) / (8 * D ** 3 * Na)
    else:
        k = float("inf")

    Ls = g.d * g.Nt                       # Tam sıkışma boyu (Solid Height)
    p = (g.L_free - 2 * g.d) / Na if Na != 0 else float("inf")  # Adım (Pitch)

    # Wahl Faktörü
    if (4 * C - 4) != 0 and C != 0:
        Kw = ((4 * C - 1) / (4 * C - 4)) + (0.615 / C)
    else:
        Kw = float("inf")

    # Max Güvenli Yük [N]
    if Kw != 0 and D != 0:
        F_max_safe = (g.tau_allow * math.pi * g.d ** 3) / (8 * Kw * D)
    else:
        F_max_safe = float("inf")

    x_max_safe = F_max_safe / k if k not in (0, float("inf")) else float("inf")

    return YaySonuclari(
        ID=ID,
        D=D,
        C=C,
        Na=Na,
        k=k,
        Ls=Ls,
        p=p,
        Kw=Kw,
        F_max_safe=F_max_safe,
        x_max_safe=x_max_safe,
        uretilebilir=C > 4,
    )
