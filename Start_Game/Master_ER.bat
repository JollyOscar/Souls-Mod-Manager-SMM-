@echo off
setlocal
:: ARGS: [1:ModName] [2:LauncherPath] [3:Ignored] [4:GameDir]

set "MOD_NAME=%~1"
set "LAUNCHER=%~2"
set "GAME_DIR=%~4"
set "SAVE_ROOT=%APPDATA%\EldenRing"
set "BACKUP_DIR=%SAVE_ROOT%\_Save_Backups\%MOD_NAME%"
set "LOG_FILE=%~dp0..\SMM_Debug.log"

echo [%DATE% %TIME%] [ER] Launching %MOD_NAME% >> "%LOG_FILE%"

:: 1. Safety Nuke
taskkill /F /IM "eldenring.exe" >nul 2>&1
echo [SMM] Clearing live save state...
for /d %%D in ("%SAVE_ROOT%\*") do (
    if /I not "%%~nxD"=="_Save_Backups" (
        del /Q "%%D\*.*" >nul 2>&1
    )
)

:: 2. Inject State
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
echo [SMM] Importing save state...
for /d %%D in ("%SAVE_ROOT%\*") do (
    if /I not "%%~nxD"=="_Save_Backups" (
        echo [%DATE% %TIME%] Restoring backup to %%D >> "%LOG_FILE%"
        robocopy "%BACKUP_DIR%" "%%D" /E /IS /IT /R:2 /W:1 >> "%LOG_FILE%"
    )
)

:: 3. Launch
if "%LAUNCHER%"=="NONE" (
    echo [SMM] Launching Vanilla via Steam...
    start steam://rungameid/1245620
) else (
    echo [SMM] Launching Mod Script...
    for %%I in ("%LAUNCHER%") do (
        echo [SMM] Running: %%~nxI
        start "" /D "%%~dpI" "%%~nxI"
    )
)

:: 4. Watchdog
echo [SMM] Monitoring session...
:WAIT_START
timeout /t 2 >nul
tasklist /FI "IMAGENAME eq eldenring.exe" 2>NUL | find /I /N "eldenring.exe">NUL
if "%ERRORLEVEL%"=="1" goto WAIT_START

:WAIT_CLOSE
timeout /t 5 >nul
tasklist /FI "IMAGENAME eq eldenring.exe" 2>NUL | find /I /N "eldenring.exe">NUL
if "%ERRORLEVEL%"=="0" goto WAIT_CLOSE

:: 5. Backup & Cleanup
echo [SMM] Game closed. Waiting for file release...
timeout /t 3 >nul
echo [SMM] Capturing save state...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
for /d %%D in ("%SAVE_ROOT%\*") do (
    if /I not "%%~nxD"=="_Save_Backups" (
        echo [%DATE% %TIME%] Backing up %%D >> "%LOG_FILE%"
        robocopy "%%D" "%BACKUP_DIR%" /MIR /R:3 /W:1 >> "%LOG_FILE%"
        
        echo [%DATE% %TIME%] Nuking %%D >> "%LOG_FILE%"
        del /Q "%%D\*.*" >nul
    )
)

echo [SMM] State saved. Safe to close.
timeout /t 3
exit