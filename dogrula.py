"""Doğrulama betiği — Bölüm 9.

Varsayılan girdilerle:
  - Bölüm B yay hesabını yapar (k, L_free -> Bölüm A'ya beslenir).
  - ALFA=0 için tek-nokta hesabı ile sweep tablosunun ilk satırını karşılaştırır
    (tutarlı olmalı).
  - Sonuçları ekrana yazar; Excel I5:S5 satırıyla elle karşılaştırılabilir.

Bu betik GUI gerektirmez (sadece core modüller).
"""

from __future__ import annotations

from core.mekanizma_hesap import (
    MekanizmaGirdileri,
    hesapla_sweep,
    hesapla_tek_nokta,
    hesapla_TM_referans,
)
from core.yay_hesap import YayGirdileri, hesapla_yay


def main():
    # Bölüm B
    yay = hesapla_yay(YayGirdileri())
    print("=== BÖLÜM B — Yay Tasarımı ===")
    for ad, deg in [
        ("ID", yay.ID), ("D", yay.D), ("C", yay.C), ("Na", yay.Na),
        ("k", yay.k), ("Ls", yay.Ls), ("p", yay.p), ("Kw", yay.Kw),
        ("F_max_safe", yay.F_max_safe), ("x_max_safe", yay.x_max_safe),
    ]:
        print(f"  {ad:12s} = {deg:.4f}")
    print(f"  Üretilebilir (C>4): {yay.uretilebilir}")

    # Bölüm A — Bölüm B'den k ve L_free beslenir
    p = MekanizmaGirdileri(YAY_SABITI_k=yay.k, YAY_SARMAL_BOYU=YayGirdileri().L_free)
    print(f"\n  TM referans (alfa=0) = {hesapla_TM_referans(p):.4f}")

    # ALFA=0 tek-nokta
    tek = hesapla_tek_nokta(0.0, p)
    print("\n=== BÖLÜM A — ALFA=0 tek-nokta (Excel I5:S5 ile karşılaştır) ===")
    for k in ["alfa_deg", "alfa_rad", "BETA", "kalkis_mesafesi", "fuze_durumu",
              "Tx", "Ty", "anlik_yay_boyu", "yay_kuvveti", "yay_momenti",
              "net_kuvvet"]:
        v = tek[k]
        print(f"  {k:16s} = {v if isinstance(v, str) else f'{v:.4f}'}")

    # Sweep ilk satırı ile tutarlılık kontrolü
    sweep = hesapla_sweep(p)
    print("\n=== Tutarlılık: sweep[0] vs tek-nokta(0) ===")
    kontroller = {
        "BETA": (sweep.BETA[0], tek["BETA"]),
        "kalkis_mesafesi": (sweep.kalkis_mesafesi[0], tek["kalkis_mesafesi"]),
        "Tx": (sweep.Tx[0], tek["Tx"]),
        "Ty": (sweep.Ty[0], tek["Ty"]),
        "anlik_yay_boyu": (sweep.anlik_yay_boyu[0], tek["anlik_yay_boyu"]),
        "yay_kuvveti": (sweep.yay_kuvveti[0], tek["yay_kuvveti"]),
        "yay_momenti": (sweep.yay_momenti[0], tek["yay_momenti"]),
        "net_kuvvet": (sweep.net_kuvvet[0], tek["net_kuvvet"]),
    }
    tum_ok = True
    for ad, (a, b) in kontroller.items():
        ok = abs(a - b) < 1e-9
        tum_ok &= ok
        print(f"  {ad:16s} sweep={a:.6f}  tek={b:.6f}  {'OK' if ok else 'FARK!'}")

    print(f"\n  Füze ayrılma ALFA = {sweep.ayrilma_alfa}")
    print(f"\nSONUÇ: {'TÜM TUTARLILIK KONTROLLERİ GEÇTİ' if tum_ok else 'HATA VAR'}")
    return 0 if tum_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
