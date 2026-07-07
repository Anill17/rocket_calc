# Yay Tahrikli Roket Fırlatma Mekanizması Hesap Uygulaması

Dönen bir kolun (ALFA açısı) fonksiyonu olarak tetikleme/fırlatma mekanizmasının
**yay kuvvetini, yay momentini, net kuvveti** ve füzenin **"İTİYOR" / "AYRILDI"**
durumunu gerçek zamanlı hesaplayan PySide6 masaüstü uygulaması. `KC_S_Hesap.xlsx`
Excel dosyasından birebir çevrilmiştir.

## Bölümler / Sekmeler

- **Mekanizma Hesabı (Bölüm A):** Sabit girdiler, ALFA sweep sonuç tablosu ve
  slider ile canlı animasyonlu mekanizma diyagramı.
- **Yay Tasarımı (Bölüm B):** Basma yayı mekanik tasarım hesapları (k, Wahl faktörü,
  güvenli yük vb.). `k` ve `L_free` değerleri Bölüm A ve C'yi otomatik besler.
- **Çalışma Noktaları (Bölüm C):** Yüklü boy → yük ve hedef yük → boy hesapları.

## Kurulum ve Çalıştırma

```bash
pip install -r requirements.txt
python main.py
```

> `main.py` doğrudan `roket_hesap/` klasörünün içinden çalıştırılmalıdır
> (import'lar `core.` ve `ui.` paketlerine göre çözülür).

## Doğrulama (GUI gerektirmez)

Core hesap modüllerini ve Bölüm A ↔ tek-nokta tutarlılığını doğrular:

```bash
python dogrula.py
```

Varsayılan girdilerle beklenen sonuç: tüm tutarlılık kontrolleri **GEÇER**,
ALFA=0 için `net_kuvvet ≈ 151.20 N` (F_roket referansı 150 N ile uyumlu).

> Not: Varsayılan yay girdileriyle yay indeksi **C ≈ 3.875 < 4** olduğundan
> arayüzde "⚠ Üretilebilir bir yay için C > 4 olmalı" uyarısı gösterilir.
> Bu beklenen davranıştır; `OD` artırılıp/`d` azaltılınca uyarı kalkar.

## Windows .exe Üretimi

> Not: `.exe` yalnızca **Windows üzerinde** üretilebilir (macOS/Linux'ta olmaz).
> İki yol var:

### Yol 1 — Windows makinesinde (en basit)

Proje klasörünü bir Windows makinesine kopyalayın ve `build_exe.bat` dosyasına
çift tıklayın. Betik venv kurar, bağımlılıkları yükler ve `.exe` üretir.
Çıktı: `dist/RoketFirlatmaHesap.exe` — Python kurulu olmayan Windows'ta da
tek başına çalışır (`--windowed` konsol penceresini gizler).

### Yol 2 — Windows makineniz yoksa (GitHub Actions, bulutta)

1. Bu klasörü bir GitHub deposuna push edin.
2. `.github/workflows/build-windows.yml` otomatik çalışır (bulutta Windows).
3. **Actions** sekmesi → ilgili çalışma → **Artifacts** altından
   `RoketFirlatmaHesap-windows` dosyasını indirin — içinde hazır `.exe` vardır.
4. Elle tetiklemek için: Actions → "Build Windows EXE" → "Run workflow".

## Merkezi Durum (AppState) ve Panel Bağımlılıkları

Paneller bağımsız değildir; `core/app_state.py` içindeki **AppState** tek gerçek
kaynaktır. `k` ve `L_free` computed property'dir. Bölüm B'de bir girdi değişince
`spring_changed` sinyali yayınlanır; Bölüm A (sweep/tablo/AYRILDI) ve Bölüm C
(yük/boy) buna abonedir ve **sekme kapalı olsa bile** arka planda güncellenir —
sekmeler arası geçişte bayat veri görünmez. Bölüm A sabit girdileri için ayrıca
`mechanism_changed` sinyali vardır.

## Hareketli Noktalar (E, A, T)

Diyagramda **B, K, M sabit** pivot/anchor; **E, A, T** ise slider ALFA'sıyla K
etrafında döner (B-A-E-K paralelkenar mekanizması: BA her zaman KE'ye paralel).
`test_mekanizma.py`, E'nin dikey hareketinin `kalkis_mesafesi = KE*(1-cos(alfa))`
ile birebir örtüştüğünü doğrular.

## Testler

```bash
python test_mekanizma.py     # veya: pytest test_mekanizma.py
```

## Proje Yapısı

```
roket_hesap/
  main.py                       # QApplication girişi + QSS tema
  dogrula.py                    # Bölüm 9 doğrulama betiği
  test_mekanizma.py             # Birim testleri (GUI gerektirmez)
  core/
    app_state.py                # Merkezi durum + Qt sinyalleri (spring_changed)
    mekanizma_hesap.py          # Bölüm A: sweep + hesapla_tek_nokta + geometri
    yay_hesap.py                # Bölüm B: yay tasarım hesapları
  ui/
    main_window.py              # 3 sekmeli QMainWindow, panel bağlantıları
    mekanizma_panel.py          # Bölüm A arayüzü
    yay_panel.py                # Bölüm B arayüzü
    calisma_noktalari_panel.py  # Bölüm C arayüzü
    mekanizma_widget.py         # PyQtGraph animasyonlu diyagram
  requirements.txt
  build_exe.bat
```
