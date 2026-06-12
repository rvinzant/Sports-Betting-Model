@echo off
setlocal enabledelayedexpansion

cls

echo =====================================
echo Checking and installing dependencies...
echo =====================================
:: This automatically installs your requirements.txt
pip install -r requirements.txt

:start
echo --- Starting Betting Application ---

:: Start python in the background and capture its Process ID (PID)
start "Betting App Engine" python app.py

:: 2. Give python exactly one second to initialize so it shows up in the task list
timeout /t 1 >nul

:: 3. Grab the Process ID of the python instance we just opened
for /f "tokens=2 delims=," %%A in ('tasklist /fi "imagename eq python.exe" /fo csv /nh') do (
    set "APP_PID=%%A"
    set "APP_PID=!APP_PID:"=!"
    goto :pid_captured
)

:pid_captured
echo Application started with PID: %APP_PID%
echo Commands: [r] Restart ^| [q] Quit

:loop
set /p user_input="> "

if /i "%user_input%"=="r" (
    echo Restarting Betting Application...
    taskkill /pid %APP_PID% /f >nul 2>&1
    timeout /t 1 >nul
    goto start
)

if /i "%user_input%"=="q" (
    echo Exiting...
    taskkill /pid %APP_PID% /f >nul 2>&1
    exit /b 0
)

goto loop