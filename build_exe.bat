@echo off
REM ============================================================
REM  Windows tek dosya .exe uretimi (PyInstaller)
REM  Bu dosyayi bir WINDOWS makinesinde calistirin (cift tiklayin).
REM  Python 3.11+ kurulu olmali: https://www.python.org/downloads/
REM ============================================================
setlocal

cd /d "%~dp0"

echo [1/4] Sanal ortam olusturuluyor...
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo HATA: Python bulunamadi. Python 3.11+ kurup PATH'e ekleyin.
        pause
        exit /b 1
    )
)

echo [2/4] Bagimliliklar yukleniyor...
call .venv\Scripts\python.exe -m pip install --upgrade pip
call .venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo HATA: Bagimliliklar yuklenemedi.
    pause
    exit /b 1
)

echo [3/4] .exe olusturuluyor (PyInstaller)...
call .venv\Scripts\pyinstaller.exe --onefile --windowed --name "RoketFirlatmaHesap" ^
    --exclude-module matplotlib ^
    --exclude-module tkinter ^
    --exclude-module PyQt5 ^
    --exclude-module PyQt6 ^
    main.py
if errorlevel 1 (
    echo HATA: PyInstaller basarisiz oldu.
    pause
    exit /b 1
)

echo [4/4] Tamamlandi.
echo.
echo Cikti: dist\RoketFirlatmaHesap.exe
echo Bu dosyayi tek basina paylasabilirsiniz (Python kurulu olmayan
echo Windows makinelerinde de calisir).
echo.
pause
