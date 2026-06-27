@echo off
setlocal
cd /d "%~dp0"
set PORT=8766
set URL=http://127.0.0.1:%PORT%/

echo VPS Operacional - modo local
echo.
echo Abrindo %URL%
echo Mantenha esta janela aberta enquanto estiver usando o aplicativo.
echo.
start "" "%URL%"

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 -m http.server %PORT% --bind 127.0.0.1
  goto :eof
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python -m http.server %PORT% --bind 127.0.0.1
  goto :eof
)

echo Python nao encontrado. Instale Python ou publique esta pasta em um servidor web.
pause
