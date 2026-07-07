@echo off
REM Windows tek dosya .exe uretimi (PyInstaller)
REM Kucuk boyut icin kullanilmayan buyuk paketler haric tutulur.

pyinstaller --onefile --windowed --name "RoketFirlatmaHesap" ^
    --exclude-module matplotlib ^
    --exclude-module tkinter ^
    --exclude-module PyQt5 ^
    --exclude-module PyQt6 ^
    main.py

echo.
echo Build tamamlandi. Cikti: dist\RoketFirlatmaHesap.exe
pause
