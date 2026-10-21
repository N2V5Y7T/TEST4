@echo off
setlocal
cd /d "%~dp0"
set "HOTKEY=%~1"
if "%HOTKEY%"=="" set "HOTKEY=CTRL+ALT+Z"
set "DEST=%LOCALAPPDATA%\Programs\Dewdrop"

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3 is not installed or not on PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
    pause
    exit /b 1
)

echo Checking dependencies...
python -m pip install --user -r requirements.txt

echo Copying Dewdrop files to "%DEST%"...
if not exist "%DEST%" mkdir "%DEST%"
xcopy /E /I /Y "%~dp0*" "%DEST%\" >nul

echo Registering Start Menu shortcut with hotkey %HOTKEY%...
python "%DEST%\dewdrop_runtime.py" --make-shortcut "%HOTKEY%"

echo.
echo ============================================================
echo Dewdrop installed to: %DEST%
echo Shortcut key registered: %HOTKEY%
echo Press %HOTKEY% anytime to pop up the Dewdrop glass ring!
echo ============================================================
pause
