@echo off
chcp 65001 >nul
title Server Yanagi Academy
cd /d "%~dp0"
set PY=
where py >nul 2>nul && set PY=py -3
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo Python non e' installato su questo PC.
  echo Scaricalo una volta da https://www.python.org/downloads/ ^(spunta "Add python.exe to PATH"^) e rilancia.
  pause & exit /b 1
)
if not exist "flags\4x3" (
  echo Scarico le bandiere per l'uso senza internet ^(solo la prima volta, serve internet^)...
  %PY% scarica-bandiere.py
)
echo.
echo  1 = dati DEFINITIVI: restano nel file dati-evento.json anche dopo la chiusura
echo  2 = dati TEMPORANEI: vengono cancellati alla chiusura del server
echo.
choice /c 12 /n /m "Scegli 1 o 2: "
if errorlevel 2 (%PY% server.py --temp) else (%PY% server.py)
pause
