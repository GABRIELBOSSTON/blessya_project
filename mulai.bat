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
  echo Could not start the program. Make sure the .tools\python folder exists,
  echo or install Python 3.10+ and run: py run.py
  pause
)
