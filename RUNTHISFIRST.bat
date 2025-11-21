@echo off
setlocal
cd /d "%~dp0"
title SMM Initial Setup
color 0B

echo ========================================================
echo          SOULS MOD MANAGER - INITIAL SETUP
echo ========================================================
echo.

:: ----------------------------------------------------------
:: 1. ZIP CHECK
:: ----------------------------------------------------------
echo Testing write permissions... > "write_test.tmp"
if not exist "write_test.tmp" goto ERROR_ZIP
del "write_test.tmp"

:: ----------------------------------------------------------
:: 2. FILE CHECK
:: ----------------------------------------------------------
if not exist "Start_Game" goto ERROR_FILES

:: ----------------------------------------------------------
:: 3. TARGET SELECTION
:: ----------------------------------------------------------
set "TARGET_APP="
set "ICON_PATH="

if exist "Souls_Mod_Manager.exe" (
    set "TARGET_APP=Souls_Mod_Manager.exe"
    set "ICON_PATH=%~dp0Souls_Mod_Manager.exe,0"
    goto CREATE_SHORTCUT
)

if exist "Souls_Mod_Manager.pyw" (
    set "TARGET_APP=Souls_Mod_Manager.pyw"
    if exist "darksign.ico" set "ICON_PATH=%~dp0darksign.ico"
    goto CHECK_PYTHON
)

goto ERROR_NO_APP

:: ----------------------------------------------------------
:: 4. PYTHON CHECK (Only for .pyw)
:: ----------------------------------------------------------
:CHECK_PYTHON
echo [INFO] EXE not found. Checking for Python...
python --version >nul 2>&1
if not errorlevel 1 goto CHECK_DEPS

py --version >nul 2>&1
if not errorlevel 1 goto CHECK_DEPS

goto ERROR_NO_PYTHON

:CHECK_DEPS
echo [INFO] Checking dependencies (Pillow)...
python -c "import PIL" >nul 2>&1
if not errorlevel 1 goto CREATE_SHORTCUT

echo [INFO] Installing Pillow...
pip install pillow
echo.

:: ----------------------------------------------------------
:: 5. SHORTCUT CREATION
:: ----------------------------------------------------------
:CREATE_SHORTCUT
echo [SETUP] Creating Desktop Shortcut for %TARGET_APP%...
set "S_PATH=%USERPROFILE%\Desktop\Souls Mod Manager.lnk"
set "S_SCRIPT=%TEMP%\CreateShortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%S_SCRIPT%"
echo sLinkFile = "%S_PATH%" >> "%S_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%S_SCRIPT%"
echo oLink.TargetPath = "%~dp0%TARGET_APP%" >> "%S_SCRIPT%"
echo oLink.WorkingDirectory = "%~dp0" >> "%S_SCRIPT%"
echo oLink.Description = "Souls Mod Manager" >> "%S_SCRIPT%"
if not "%ICON_PATH%"=="" echo oLink.IconLocation = "%ICON_PATH%" >> "%S_SCRIPT%"
echo oLink.Save >> "%S_SCRIPT%"

cscript /nologo "%S_SCRIPT%"
del "%S_SCRIPT%"

echo [SUCCESS] Shortcut created on your Desktop.
echo.
echo [LAUNCH] Starting Manager...
start "" "%~dp0%TARGET_APP%"

echo.
echo Done! You can close this window.
pause
exit

:: ----------------------------------------------------------
:: ERROR HANDLERS
:: ----------------------------------------------------------
:ERROR_ZIP
color 0C
echo [ERROR] CRITICAL FAILURE
echo.
echo It appears you are running this file from inside the ZIP archive.
echo Windows does not allow programs to work correctly from inside a ZIP.
echo.
echo PLEASE EXTRACT THIS ENTIRE FOLDER TO YOUR DESKTOP OR DOCUMENTS.
echo.
pause
exit

:ERROR_FILES
color 0E
echo [WARNING] Start_Game folder is missing!
echo Mods will NOT launch without this folder.
echo Please re-download or re-extract the zip.
echo.
pause
exit

:ERROR_NO_APP
color 0C
echo [ERROR] Could not find Souls_Mod_Manager.exe or .pyw!
echo Please re-download the release.
pause
exit

:ERROR_NO_PYTHON
color 0C
echo [ERROR] Python is not installed!
echo.
echo You are using the Source Code version (.pyw) but Python is missing.
echo Please install Python from python.org or use the .EXE release.
echo.
pause
exit
