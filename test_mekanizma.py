"""Birim testleri — GUI gerektirmez (yalnızca core modüller).

pytest ile veya doğrudan `python test_mekanizma.py` ile çalıştırılabilir.

En kritik test: E noktasının Y bileşenindeki hareket, ayrı hesaplanan
kalkis_mesafesi = KE*(1-cos(alfa)) değeriyle her ALFA için birebir örtüşmeli.
"""

from __future__ import annotations

import math

from core.mekanizma_hesap import (
    MekanizmaGirdileri,
    bul_beta_180_noktasi,
    hesapla_geometri_noktalari,
    hesapla_sweep,
    hesapla_tek_nokta,
)
from core.yay_hesap import YayGirdileri, hesapla_yay

TOL = 1e-9


def _alfa_araligi(mn=0.0, mx=60.5, step=0.5):
    n = int(round((mx - mn) / step)) + 1
    return [mn + step * i for i in range(n)]


def test_E_hareketi_kalkis_mesafesine_esit():
    """Ey(0) - Ey(alfa) mutlak değeri == kalkis_mesafesi (her alfa için).

    E, K etrafında alfa ile döner: Ey(alfa) = -KE*cos(alfa). Dolayısıyla
    E'nin dikey yer değiştirmesinin büyüklüğü KE*(1-cos(alfa))'dır ki bu
    tam olarak kalkis_mesafesi'dir (E yukarı yönde hareket eder).
    """
    p = MekanizmaGirdileri()
    Ey0 = hesapla_geometri_noktalari(p, 0.0)["E"][1]
    for alfa in _alfa_araligi():
        Ey = hesapla_geometri_noktalari(p, alfa)["E"][1]
        kalkis = hesapla_tek_nokta(alfa, p)["kalkis_mesafesi"]
        # Yer değiştirme büyüklüğü
        assert abs(abs(Ey0 - Ey) - kalkis) < TOL, (
            f"alfa={alfa}: |Ey0-Ey|={abs(Ey0-Ey):.9f} != kalkis={kalkis:.9f}"
        )
        # Bağımsız kapalı-form kontrolü
        beklenen = p.KE * (1 - math.cos(math.radians(alfa)))
        assert abs(kalkis - beklenen) < TOL


def test_A_ve_E_paralelkenar():
    """A(alfa) her zaman E(alfa)'dan -AE kadar X ofsetli olmalı (BA ∥ KE)."""
    p = MekanizmaGirdileri()
    for alfa in _alfa_araligi():
        n = hesapla_geometri_noktalari(p, alfa)
        assert abs((n["A"][0] - n["E"][0]) - (-p.AE)) < TOL
        assert abs(n["A"][1] - n["E"][1]) < TOL  # aynı Y (paralelkenar)


def test_sabit_pivotlar_degismiyor():
    """B, K, M noktaları alfa'dan bağımsız (sabit) kalmalı."""
    p = MekanizmaGirdileri()
    ref = hesapla_geometri_noktalari(p, 0.0)
    for alfa in _alfa_araligi():
        n = hesapla_geometri_noktalari(p, alfa)
        for isim in ("B", "K", "M"):
            assert n[isim] == ref[isim], f"{isim} alfa={alfa}'da değişti"


def test_sweep_tek_nokta_tutarli():
    """Sweep tablosunun her satırı hesapla_tek_nokta ile tutarlı olmalı."""
    yay = hesapla_yay(YayGirdileri())
    p = MekanizmaGirdileri(
        YAY_SABITI_k=yay.k, YAY_SARMAL_BOYU=YayGirdileri().L_free
    )
    sweep = hesapla_sweep(p)
    for i, alfa in enumerate(sweep.alfa_deg):
        tek = hesapla_tek_nokta(float(alfa), p)
        assert abs(sweep.net_kuvvet[i] - tek["net_kuvvet"]) < 1e-6
        assert abs(sweep.yay_kuvveti[i] - tek["yay_kuvveti"]) < 1e-6
        assert sweep.fuze_durumu[i] == tek["fuze_durumu"]


def test_ayrilma_esigi():
    """kalkis_mesafesi >= 3.2 mm olduğunda durum AYRILDI olmalı."""
    p = MekanizmaGirdileri()
    for alfa in _alfa_araligi():
        d = hesapla_tek_nokta(alfa, p)
        beklenen = "AYRILDI" if d["kalkis_mesafesi"] >= 3.2 else "ITIYOR"
        assert d["fuze_durumu"] == beklenen


def test_beta_alfa_ile_artar():
    """BETA, ALFA arttıkça artmalı ve Excel'deki değerlerle uyuşmalı.

    Excel ATAN2(x, y) -> Python math.atan2(y, x); argüman sırası doğru olmalı.
    Varsayılan sabitlerle: ALFA=0 -> BETA≈138°, ALFA=60.5 -> BETA≈219.9°.
    Yanlış argüman sırasında BETA ALFA ile azalır (yanlış).
    """
    p = MekanizmaGirdileri()
    betalar = [hesapla_tek_nokta(a, p)["BETA"] for a in _alfa_araligi()]
    for onceki, sonraki in zip(betalar, betalar[1:]):
        assert sonraki > onceki, "BETA ALFA ile artmıyor (argüman sırası ters?)"
    assert abs(betalar[0] - 138.0) < 0.5, f"ALFA=0 BETA={betalar[0]:.3f} != ~138"
    assert abs(betalar[-1] - 219.9) < 0.5, f"ALFA=60.5 BETA={betalar[-1]:.3f} != ~219.9"


def test_beta_180_kesisimi():
    """BETA varsayılan sabitlerle 180°'yi (moment kolu=0) aralık içinde geçer."""
    p = MekanizmaGirdileri()
    b = bul_beta_180_noktasi(p)
    assert b["ulasildi"], "BETA 180°'ye ulaşmıyor (argüman sırası ters olabilir)"
    assert abs(b["BETA"] - 180.0) < 1e-6


def _calistir():
    testler = [v for k, v in globals().items() if k.startswith("test_")]
    basarili = 0
    for t in testler:
        t()
        print(f"  ✓ {t.__name__}")
        basarili += 1
    print(f"\n{basarili}/{len(testler)} test GEÇTİ")
    return 0


if __name__ == "__main__":
    raise SystemExit(_calistir())
