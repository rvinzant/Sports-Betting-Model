@echo off
setlocal enabledelayedexpansion

echo =====================================
echo Checking and installing dependencies...
echo =====================================
:: This automatically installs your requirements.txt
pip install -r requirements.txt

:start
echo --- Starting Betting Application ---

:: Start python in the background and capture its Process ID (PID)
for /f "tokens=2 delgies" %%A in ('powershell -Command "Start-Process python -ArgumentList 'app.py' -NoNewWindow -PassThru | Select-Object -ExpandProperty Id"') do set APP_PID=%%A

echo Commands: [r] Restart ^| [q] Quit

:loop
set /p user_input="> "

if /i "%user_input%"=="r" (
    echo Restarting Betting Application...
    taskkill /pid %APP_PID% /f >nul 2>&1
    goto start
)

if /i "%user_input%"=="q" (
    echo Exiting...
    taskkill /pid %APP_PID% /f >nul 2>&1
    exit /b 0
)

goto loop