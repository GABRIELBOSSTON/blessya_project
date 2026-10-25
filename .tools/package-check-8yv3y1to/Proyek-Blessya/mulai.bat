@echo off
setlocal
cd /d "%~dp0"
if exist ".tools\python\python.exe" (
  ".tools\python\python.exe" run.py %*
) else (
  py -3 run.py %*
)
if errorlevel 1 (
  echo.
  echo Program belum dapat dijalankan. Lihat petunjuk di docs\PANDUAN-PENGGUNA.md.
  pause
)
