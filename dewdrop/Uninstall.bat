@echo off
setlocal
echo Stopping any running Dewdrop instance...
taskkill /IM dewdrop.exe /F >nul 2>nul
taskkill /IM dewdrop-worker.exe /F >nul 2>nul
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Dewdrop.lnk" >nul 2>nul
if exist "%LOCALAPPDATA%\Programs\Dewdrop" (
    rmdir /S /Q "%LOCALAPPDATA%\Programs\Dewdrop"
)
echo Dewdrop has been uninstalled cleanly.
pause
